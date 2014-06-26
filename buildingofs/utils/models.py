import datetime
import json
from decimal import Decimal

from django import forms
from django.conf import settings
from django.core import validators, exceptions
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from pytz import common_timezones

from . import filters
from . import managers
from . import forms as common_forms


class RPCModel(models.Model):
    objects = managers.RPCManager()

    class Meta:
        abstract = True

    @classmethod
    def get_column(cls, column):
        """
        Get column from column name
        """
        field = cls._meta.get_field(column)
        column = {
            'type': field.get_internal_type(),
            'attr': field.column,
            'label': field.verbose_name.capitalize(),
            'filters': filters.get_filters(field.get_internal_type())
        }

        if hasattr(field, 'sortable') and field.sortable:
            column['sortable'] = True
            if field.sortable_field:
                column['sortable_column'] = field.sortable_field
        return column

    @classmethod
    def get_columns(cls):
        """
        Get all columns
        """
        columns = []
        for field in cls.get_fields():
            column = cls.get_column(field.column)
            columns.append(column)
        return columns

    @classmethod
    def get_fields(cls):
        return cls._meta.fields

    @classmethod
    def get_field(cls, field_name):
        if field_name == 'pk':
            return cls._meta.pk
        fields = cls.get_fields()
        for field in fields:
            if field.column == field_name:
                return field
        return None

    def __init__(self, *args, **kwargs):
        if not kwargs:
            if args and isinstance(args[0], dict):
                kwargs = args[0].copy()
                args = tuple()

        self._initial_kwargs = kwargs.copy()

        # Slower, kwargs-ready version.
        fields_iter = iter(self._meta.fields)
        for val, field in zip(args, fields_iter):
            setattr(self, field.attname, val)
            kwargs.pop(field.name, None)

        # Now we're left with the unprocessed fields that *must* come from
        # keywords, or default.

        for field in fields_iter:
            if kwargs:
                if hasattr(self, 'name_map') and self.name_map.get(field.attname):
                    attname = self.name_map[field.attname]
                else:
                    attname = field.attname

                try:
                    val = kwargs.pop(attname)
                except KeyError:
                    # This is done with an exception rather than the
                    # default argument on pop because we don't want
                    # get_default() to be evaluated, and then not used.
                    # Refs #12057.
                    val = field.get_default()
            else:
                val = field.get_default()

            setattr(self, field.attname, field.to_python(val))

        if kwargs:
            for prop in list(kwargs):
                try:
                    if isinstance(getattr(self.__class__, prop), property):
                        setattr(self, prop, kwargs.pop(prop))
                except AttributeError:
                    pass

        self._state = self.__dict__.copy()

        if kwargs:
            self._extra_data = kwargs

    def _changed_fields(self):
        return [k for k, v in self._state.items() if self.__dict__[k] != v]

    def _get_default_data(self):
        fields_with_defaults = [f.name for f in self._meta.fields if f.has_default()]
        return {k: getattr(self, k) for k in fields_with_defaults}

    def _parse_data(self, data):
        for key, val in data.items():
            if isinstance(val, datetime.datetime):
                data[key] = val.isoformat()
                continue
            if isinstance(val, datetime.date):
                data[key] = val.isoformat()
                continue
            if isinstance(val, Decimal):
                data[key] = str(val)
                continue
            if val == '' and self._meta.get_field(key).null:
                data[key] = None
                continue

        return data

    def refresh(self):
        data = self.__class__.objects.get(pk=self.pk)
        return self.__class__(data.__dict__)

    @classmethod
    def get_class_url(cls, name_sufix):
        view_name = cls._meta.object_name.lower() + '-' + name_sufix
        try:
            return reverse(view_name)
        except NoReverseMatch:
            return None

    @classmethod
    def get_list_url(cls):
        return cls.get_class_url('index')

    @classmethod
    def get_create_url(cls):
        return cls.get_class_url('create')

    def get_absolute_url(self, name_sufix):
        view_name = self._meta.object_name.lower() + '-' + name_sufix
        if self.pk:
            try:
                return reverse(view_name, kwargs={'id': str(self.pk)})
            except NoReverseMatch:
                return None
        else:
            return None

    def get_detail_url(self):
        return self.get_absolute_url('view')

    def get_delete_url(self):
        return self.get_absolute_url('delete')

    def validate_unique(self, exclude=None):
        """ We're not using the built in unique checks. For now we'll rely on the platform to
        Let us know if we've done something wrong. """
        return None

    def __json__(self):
        fields = [f.name for f in self.get_fields()]
        return {k:v for k, v in self.__dict__.items() if k in fields}


# Mixin
class SortableMixin(object):
    def __init__(self, *args, **kwargs):
        self.sortable = kwargs.pop('sortable', False)
        self.sortable_field = kwargs.pop('sortable_field', None)
        super(SortableMixin, self).__init__(*args, **kwargs)


class IntegerField(SortableMixin, models.IntegerField):
    __metaclass__ = models.SubfieldBase


class BooleanField(SortableMixin, models.BooleanField):
    __metaclass__ = models.SubfieldBase


class NoneToBooleanField(SortableMixin, models.BooleanField):
    'For boolean fields that could initially be defined as None in platform'

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value is None:
            value = False
        return super(NoneToBooleanField, self).to_python(value)


class NullBooleanField(SortableMixin, models.NullBooleanField):
    __metaclass__ = models.SubfieldBase


class TextField(SortableMixin, models.TextField):
    __metaclass__ = models.SubfieldBase


class CharField(SortableMixin, models.CharField):
    __metaclass__ = models.SubfieldBase


class EmailField(models.EmailField):
    __metaclass__ = models.SubfieldBase


class DateTimeField(SortableMixin, models.DateTimeField):
    __metaclass__ = models.SubfieldBase


class DateField(SortableMixin, models.DateField):
    __metaclass__ = models.SubfieldBase


class TimeField(SortableMixin, models.TimeField):
    __metaclass__ = models.SubfieldBase


class DecimalField(SortableMixin, models.DecimalField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        value = super(DecimalField, self).to_python(value)
        if value:
            return value.quantize(Decimal('0.00'))
        return value


class IPAddressField(models.IPAddressField):
    __metaclass__ = models.SubfieldBase


class PennyField(SortableMixin, models.DecimalField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, Decimal):
            # then we have already been called once, django likes to call
            # to_python for validation as well
            return value

        value = super(PennyField, self).to_python(value)
        return value / 100

    def get_prep_value(self, value):
        value = value * 100
        return super(PennyField, self).get_prep_value(value)


class FloatField(SortableMixin, models.FloatField):
    __metaclass__ = models.SubfieldBase


class SimpleManagerField(models.Field):
    def __init__(self, model, *args, **kwargs):
        self._model = model
        super(SimpleManagerField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        return managers.SimpleManager(self._model, value)


class CityField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        cities = [(code, data['name'])
                  for code, data in settings.SUPPORTED_CITIES.items()]
        cities = sorted(cities, key=lambda city: city[1])

        defaults = {
            'choices': cities,
        }
        defaults.update(kwargs)
        super(CityField, self).__init__(*args, **defaults)


class TimezoneField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        supported_cities_only = kwargs.pop('supported_cities_only', False)
        if supported_cities_only:
            timezones = list(
                set(
                    (data['timezone'], data['timezone'])
                    for data in settings.SUPPORTED_CITIES.values()
                    if 'timezone' in data
                )
            )
        else:
            timezones = [(timezone, timezone)
                         for timezone in common_timezones]

        timezones = sorted(timezones, key=lambda timezone: timezone[1])

        defaults = {
            'choices': timezones,
            'max_length': 32  # Longest string in pytz.all_timezones
        }
        defaults.update(kwargs)
        super(TimezoneField, self).__init__(*args, **defaults)


class CityLocaleField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        locales = list(
            set(
                (data['locale'], data['locale'])
                for data in settings.SUPPORTED_CITIES.values()
                if 'locale' in data
            )
        )
        locales = sorted(locales, key=lambda locale: locale[1])

        defaults = {
            'choices': locales
        }
        defaults.update(kwargs)
        super(CityLocaleField, self).__init__(*args, **defaults)


class CountryCodeField(SortableMixin, models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        country_codes = sorted(
            settings.COUNTRY_CODES.items(), key=lambda c: c[1]
        )

        defaults = {
            'choices': country_codes,
        }
        defaults.update(kwargs)
        super(CountryCodeField, self).__init__(*args, **defaults)


class StringListField(models.Field):
    __metaclass__ = models.SubfieldBase
    default_error_messages = {
        'invalid_list': _('Attribute should be a list'),
    }

    def formfield(self, **kwargs):
        defaults = {
            'form_class': common_forms.CommaSeparatedField,
        }
        defaults.update(kwargs)
        return super(StringListField, self).formfield(**defaults)

    def clean(self, value, model_instance):
        value = self.to_python(value)
        self.validate(value, model_instance)
        for v in value:
            self.run_validators(v)
        return value

    def validate(self, value, model_instance):
        if not isinstance(value, (list, tuple)):
            raise exceptions.ValidationError(self.error_messages['invalid_list'])
        return super(StringListField, self).validate(value, model_instance)

class IntegerListField(StringListField):
    __metaclass__ = models.SubfieldBase
    default_error_messages = {
        'invalid_list': _('Attribute should be a list'),
        'invalid_type': _('All values should be integer'),
    }

    def clean(self, value, model_instance):
        value = self.to_python(value)

        try:
            value = [int(x) for x in value]
        except TypeError:
            raise exceptions.ValidationError(self.error_messages['invalid_type'])

        self.validate(value, model_instance)
        for v in value:
            self.run_validators(v)
        return value


class JSONField(forms.Field):
    widget = forms.HiddenInput

    def prepare_value(self, value):
        if isinstance(value, list):
            return json.dumps(value)
        else:
            return value

    def to_python(self, value):
        return json.loads(value)


class ListField(models.Field):

    def validate(self, value, model_instance):
        for item in value:
            try:
                json.dumps(item)
            except ValueError:
                raise exceptions.ValidationError('All elements must be JSON serializable')

    def formfield(self, **kwargs):
        defaults = {'required': not self.blank,
                    'label': capfirst(self.verbose_name),
                    'help_text': self.help_text}

        if self.has_default():
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()

        return JSONField(**defaults)


class LookupField(models.TextField):
    '''
    To be used for lookup relationship fields in platform.
    This fields are not editable text fields and their value is the Lookup
    text for a given ForeignKey relationship.

    '''

    def __init__(self, related_field, *args, **kwargs):
        self.related_field = related_field
        kwargs.update({
            'editable': False,
            'blank': True,
            'null': False,
            'default': '',
        })
        super(LookupField, self).__init__(*args, **kwargs)


class ForeignKey(models.Field):
    "Loosely coupled Foreign key for other RPC Models"
    __metaclass__ = models.SubfieldBase
    description = 'Foreign key to another RPCModel'
    empty_strings_allowed = False
    default_error_messages = {
        'invalid_choice': _('Select a valid choice. %(value)s is not one of the available choices.'),
        'invalid': _('Invalid selection.'),
    }

    def __init__(self, related_model, *args, **kwargs):
        self.related_model = related_model
        if kwargs.get('choices'):
            raise Exception(
                'Should not provide a choices argument for this field'
            )
        super(ForeignKey, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        self.set_attributes_from_name(name)
        self.model = cls
        cls._meta.add_field(self)
        if self.related_model == 'self':
            self.related_model = cls

    def get_internal_type(self):
        return self.related_model._meta.pk.get_internal_type()

    def db_type(self, connection):
        # This is just for syncdb sake
        return self.related_model._meta.pk.db_type(connection)

    def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH):
        """Returns choices with a default blank choices included, for use
        as SelectField choices for this field."""
        first_choice = include_blank and blank_choice or []
        return first_choice + self.rpc_choices()

    def rpc_choices(self):
        pk_name = self.related_model._meta.pk.name
        choices = [(getattr(model_inst, pk_name), str(model_inst))
                   for model_inst in self.related_model.objects.all()]
        return list(choices)

    def get_choices_default(self):
        return self.get_choices()

    def to_python(self, value):
        if self.get_internal_type() == 'CharField':
            return value
        else:
            # It's an IntegerField
            if value in validators.EMPTY_VALUES:
                return None
            try:
                value = int(str(value))
            except (ValueError, TypeError):
                raise exceptions.ValidationError(self.error_messages['invalid'])
            return value

    def validate(self, value, model_instance):
        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if value not in validators.EMPTY_VALUES:
            try:
                self.related_model.objects.get(
                    **{self.related_model._meta.pk.name: value}
                )
            except self.related_model.DoesNotExist:
                msg = self.error_messages['invalid_choice'] % {'value': value}
                raise exceptions.ValidationError(msg)
        else:
            return

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages['null'])

        if not self.blank and value in validators.EMPTY_VALUES:
            raise exceptions.ValidationError(self.error_messages['blank'])

    def formfield(self, **kwargs):
        defaults = {
            'form_class': common_forms.SimpleModelChoiceField,
            'queryset': self.related_model.objects,
        }
        defaults.update(kwargs)
        return super(ForeignKey, self).formfield(**defaults)


class ManyToManyField(ForeignKey):
    __metaclass__ = models.SubfieldBase
    description = 'ManyToMany Field to another RPCModel'
    default_error_messages = {
        'invalid_choice': _('Invalid choice. %(value)s is not one of the available choices.'),
        'invalid_choices': _('Invalid choices. Values %(value)s  are not in the available choices.'),
        'invalid_list': _('Enter a list of values.'),
        'invalid': _('Invalid selection.'),
    }

    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise exceptions.ValidationError(
                self.error_messages['invalid_list']
            )

        res = []
        for item in value:
            res.append(super(ManyToManyField, self).to_python(item))

        return res

    def validate(self, value, model_instance):
        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if value not in validators.EMPTY_VALUES:
            valid_values = [
                option[0] for option in self.get_choices()
            ]

            if set(value).intersection(set(valid_values)) == set(value):
                return
            else:
                invalid_values = list(
                    set(value).difference(set(valid_values))
                )
                if len(invalid_values) == 1:
                    msg = self.error_messages['invalid_choice'] % {'value': invalid_values[0]}
                else:
                    msg = self.error_messages['invalid_choices'] % {'value': invalid_values}
                raise exceptions.ValidationError(msg)

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages['null'])

        if not self.blank and value in validators.EMPTY_VALUES:
            raise exceptions.ValidationError(self.error_messages['blank'])

    def formfield(self, **kwargs):
        defaults = {
            'form_class': common_forms.SimpleModelMultipleChoiceField,
            'queryset': self.related_model.objects,
        }
        defaults.update(kwargs)
        return super(ForeignKey, self).formfield(**defaults)
