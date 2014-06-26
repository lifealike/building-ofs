from django import forms


class CommaSeparatedField(forms.CharField):
    widget = forms.TextInput

    def prepare_value(self, value):
        if value is None:
            return ''

        if isinstance(value, (list, tuple)):
            return ', '.join(value)

        return value

    def to_python(self, value):
        if not value:
            return []
        return [v.strip() for v in value.split(',')]


class SimpleModelChoiceField(forms.ModelChoiceField):
    '''
    A model choice field that doesn't clean the provided value to its
    corresponding model object and works better with our current implementation
    of related fields in our RPCModels

    '''

    def clean(self, value):
        return value


class SimpleModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    '''
    A Multiple choice model field that doesn't clean the provided value to its
    corresponding model object and works better with our current implementation
    of related fields in our RPCModels

    '''

    def clean(self, value):
        return value
