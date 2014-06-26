import iso8601


#==============================================================================
# Type Filters
#==============================================================================


class Filter(object):
    def validate(self, value):
        return value

    def format_value(self, value):
        return value


class DateFilter(Filter):
    def validate(self, value):
        try:
            iso8601.parse_date(value)
        except:
            raise ValueError("'{}' is not a valid datetime".format(value))
        return value


class BooleanFilter(Filter):
    def validate(self, value):
        acceptable = ("0", "1")
        if not value in acceptable:
            raise ValueError("Must be one of {}".format(acceptable))
        return value

#==============================================================================
# Operator Mixins
#==============================================================================


class Is(object):
    def operation(self):
        return 'is'

    def format_value(self, value):
        return '%s' % value


class Equals(object):
    def operation(self):
        return 'equals'

    def format_value(self, value):
        return 'equal:%s' % value


class Contains(object):
    def operation(self):
        return 'contains'

    def format_value(self, value):
        return 'like:%s' % value


class LessThan(object):
    def operation(self):
        return 'lte'

    def format_value(self, value):
        return 'lte:%s' % value


class GreaterThan(object):
    def operation(self):
        return 'gte'

    def format_value(self, value):
        return 'gte:%s' % value


class Not(object):
    def operation(self):
        return 'not'

    def format_value(self, value):
        return 'not:%s' % value


class In(object):
    def operation(self):
        return 'in'

    def format_value(self, value):
        if isinstance(value, (list, tuple)):
            value = ','.join(value)
        return 'in:%s' % value


filter_operators = {
    'is': Is,
    'equals': Equals,
    'contains': Contains,
    'lte': LessThan,
    'gte': GreaterThan,
    'not': Not,
    'in': In,
}

filter_types = {
    'TextField': [
        'contains',
        'equals'
    ],
    'CharField': [
        'contains',
        'equals'
    ],
    'IntegerField': [
        'equals',
        'gte',
        'lte',
    ],
    'BooleanField': [
        'is',
    ],
    'DateTimeField': [
        'equals',
        'gte',
        'lte',
    ],
    'DecimalField': [
        'equals',
        'gte',
        'lte',
    ],
}

filter_validators = {
    'BooleanField': BooleanFilter,
    'DateTimeField': DateFilter,
}


def get_filters(type):
    """
    Return a list of filters for a particular attribute type
    """
    filters = []
    if type in filter_types:
        for filter in filter_types[type]:
            filters.append(filter_operators[filter]().operation())
    return filters


def get_operator(type):
    return filter_operators[type]()


def validate_filter(type, value):
    """
    Validate value against filter

    Raises ValueError if not valid
    """
    if type in filter_validators:
        filter_validators[type]().validate(value)


def process_filter(filter):
    """
    Convert filter format into field and operator

    Input:

        'foo__lte'

    Ouput:

        'foo', 'lte'

    If no operator then default to 'equals'
    """
    m = filter.split('__')
    if len(m) == 1:
        return filter, 'equals'
    else:
        return m[0], m[1]
