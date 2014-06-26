import hashlib
import math

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.forms.models import model_to_dict

from buildingofs.ofsapi import rpc

from .filters import validate_filter, get_operator, process_filter


class RPCManager(models.Manager):
    page_size = 25
    default_sort = None
    default_sort_desc = False
    filters = {}
    rpc_kwargs = {}  # extra rpc kwargs to send
    CACHE_TIMEOUT = settings.CACHE_TIMEOUT

    def _legacy_rpc_call(self, method, params, **rpc_kwargs):
        return method(params=params, **rpc_kwargs)

    def rpc_call(self, params, topic=None, method=None, rpc_kwargs=None):
        topic = topic if topic is not None else self.topic
        method = method if method is not None else self.method

        _topic = getattr(rpc, topic)
        _method = getattr(_topic, method)

        _rpc_kwargs = getattr(self, 'rpc_kwargs').copy()
        if (rpc_kwargs):
            _rpc_kwargs.update(rpc_kwargs)

        if getattr(self, 'legacy', False):
            return self._legacy_rpc_call(_method, params, **_rpc_kwargs)

        params.update(_rpc_kwargs)
        params.pop('batch_results', None)
        return _method(**params)

    def filter(self, sort_by=None, sort_desc=False, rpc_kwargs=None, **kwargs):
        """
        Returns empty list if no results

        Account.objects.filter(booking_ref='DBKSJ43')
        Account.objects.filter(booking_ref__contains='DBK')
        """

        pk = kwargs.pop('pk', None)

        filters = self.filters.copy()
        filters.update(kwargs)

        if pk:
            filters[self.model._meta.pk.name] = pk

        _filters = self.convert_filters(filters)

        params = {
            'batch_results': False,
            'sort_by': sort_by,
            'sort_desc': sort_desc,
            'filters': _filters,
        }

        results = self.preprocess_rpc_response(
            self.rpc_call(params, rpc_kwargs=rpc_kwargs)
        )

        models = map(self.model, results)
        return models

    def preprocess_rpc_response(self, response):
        """
        Override this function if you need to manipulate data before
        turning them into models

        """
        # handle case of [total, [results...]]
        if len(response) == 2 and isinstance(response[0], int) and isinstance(response[1], list):
            response = response[1]

        return response

    def all(self, **kwargs):
        return self.filter(**kwargs)

    def _cache_key(self, **kwargs):
        app = self.model._meta.app_label
        model = self.model._meta.object_name
        key = hashlib.md5(str(kwargs)).hexdigest()
        return "{}.{}-{}".format(app, model, key)

    def _cache_keys_key(self):
        app = self.model._meta.app_label
        model = self.model._meta.object_name
        return "{}.{}-KEYS".format(app, model)

    def cached(self, **kwargs):
        key = self._cache_key(**kwargs)

        objects = cache.get(key)

        if objects is None:
            objects = self.filter(**kwargs)
            cache.set(key, objects, self.CACHE_TIMEOUT)
            existing_keys = cache.get(self._cache_keys_key(), [])
            existing_keys.append(key)
            cache.set(self._cache_keys_key(), existing_keys)

        return objects

    def get_cached(self, **kwargs):
        result = self.cached(**kwargs)
        if not result:
            raise self.model.DoesNotExist()

        if len(result) > 1:
            raise self.model.MultipleObjectsReturned()

        return result[0]

    def clear_cache(self):
        existing_keys = cache.get(self._cache_keys_key(), [])
        for key in existing_keys:
            cache.delete(key)

    def values(self):
        '''
            This returns only those attrs that have been successfully mapped
            with the model's fields

        '''
        return map(model_to_dict, self.filter())

    def count(self, **kwargs):
        return len(self.filter(**kwargs))

    def get(self, **kwargs):
        """
        Calls filter and returns first one.

        Raise MulipleObject error if more than one
        Raise DoesNotExist error if not one

        try:
            Account.objects.get(id=747)
        except Account.DoesNotExitst:
            foo
        except Account.MulipleObjct
            foo
        """
        result = self.filter(**kwargs)
        if not result:
            raise self.model.DoesNotExist()

        if len(result) > 1:
            raise self.model.MultipleObjectsReturned()

        return result[0]

    def get_page(self, page, page_size=None, sort_by=None, sort_desc=False,
                 **kwargs):
        """
        Get page of results

        page - page number to get
        page_size - number of results per page
        sort_by - column to sort by
        sort_desc - whether to sort descending
        **kwargs - filters to apply

        Example:

            # get first page of all objects with id greater than 20
            Account.objects.get_page(1, id__gte=20)

        Returns [total number of results, number of pages, list of models]
        """

        page_size = page_size if page_size is not None else self.page_size

        if sort_by is None:
            sort_by = self.default_sort
            sort_desc = self.default_sort_desc

        filters = self.filters.copy()
        filters.update(kwargs)
        _filters = self.convert_filters(filters)

        params = {
            'batch_results': True,
            'batch_size': page_size,
            'batch': page,
            'sort_by': sort_by,
            'sort_desc': sort_desc,
            'filters': _filters,
        }

        rpc_response = self.rpc_call(params)
        if not rpc_response:
            return 0, 0, []

        total, results = rpc_response

        num_pages = int(math.ceil(total / float(page_size)))

        models = map(self.model, results)

        return total, num_pages, models

    def convert_filters(self, filters):
        """
        Convert filters for platform query

        Input:
            {
                'booking_ref': 'DBKSJ43',
                'booking_ref__contains': 'DBK',
                'booking_ref__in': ['DBKSJ43','DWSK678'],
            }

        Output:
            [
                ('booking_ref', 'equal:DBKSJ43'),
                ('booking_ref', 'like:DBK'),
                ('booking_ref', 'in:DBKSJ43,DWSK678'),
            ]
        """
        converted = []

        if filters is None:
            return converted

        for filter in filters:
            field, operator = process_filter(filter)
            value = filters[filter]

            _field = self.model.get_field(field)
            _operator = get_operator(operator)

            ## validate
            validate_filter(_field.get_internal_type(), value)
            converted.append(
                (_field.name, _operator.format_value(value))
            )
        return converted


class SimpleManager(object):
    """ takes a simple list of dicts and maps them to a model
        then allows filtering on them. only does basic filtering
        with == for now. """

    def __init__(self, model, items, *args, **kwargs):
        self.model = model
        self._items = map(model, items)

    def __iter__(self):
        for item in self._items:
            yield item

    def exists(self):
        return len(self._items) > 0

    def filter(self, **kwargs):
        for item in self._items:
            if all(getattr(item, attr) == value for attr, value in kwargs.iteritems()):
                yield item

    def get(self, **kwargs):
        result = self.filter(**kwargs)
        try:
            first_result = result.next()
        except StopIteration:
            raise self.model.DoesNotExist()

        try:
            result.next()
        except StopIteration:
            pass
        else:
            raise self.model.MultipleObjectsReturned()

        return first_result
