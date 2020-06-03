import base64
import datetime
from abc import ABC, abstractmethod

from .conditions import AnyValue
from .errors import FieldError, FormError

__all__ = [
    'Field', 'StringField', 'IntegerField', 'FloatField', 'BooleanField',
    'DateTimeField', 'DateField', 'TimeField', 'ListField', 'EnumField', 'BytesField'
]


class Field(ABC):
    _default = None

    def __new__(cls, *args, **kwargs):
        if 'init' in kwargs:
            kwargs.pop('init')
            return super().__new__(cls)
        return UnboundField(cls, *args, **kwargs)

    def __init__(self,
                 condition=AnyValue(),
                 optional: bool = False,
                 default=None,
                 init=False):
        self.condition = condition
        self.optional = optional
        self.default = default or self._default

        self._data = None
        self.is_empty = False

    @property
    def data(self):
        return self._data

    def mark_empty(self):
        if not self.optional:
            raise FieldError('cannot be blank')
        self.is_empty = True
        if callable(self.default):
            self._data = self.default()
        else:
            self._data = self.default

    @abstractmethod
    def process_data(self, value):
        self.condition.check(self)


class UnboundField:
    def __init__(self, field_cls, *args, **kwargs):
        self.field_cls = field_cls
        self.args = args
        self.kwargs = kwargs
        self.kwargs['init'] = True

    def bind(self):
        return self.field_cls(*self.args, **self.kwargs)


class StringField(Field):
    _default = ''

    def process_data(self, value):
        if not isinstance(value, str):
            raise FieldError('invalid string')
        self._data = value
        super().process_data(value)


class IntegerField(Field):
    _default = 0

    def process_data(self, value):
        if not isinstance(value, int):
            raise FieldError('invalid integer')
        self._data = value
        super().process_data(value)


class FloatField(Field):
    _default = 0.0

    def process_data(self, value):
        if not isinstance(value, float):
            raise FieldError('invalid float')
        self._data = value
        super().process_data(value)


class BooleanField(Field):
    def process_data(self, value):
        if not isinstance(value, bool):
            raise FieldError('invalid boolean')
        self._data = value
        super().process_data(value)


class DateTimeField(Field):
    def __init__(self, pattern='%Y-%m-%dT%H:%M:%S', **kwargs):
        super().__init__(**kwargs)
        self.pattern = pattern

    def process_data(self, value):
        try:
            self._data = datetime.datetime.strptime(value, self.pattern)
        except ValueError:
            raise FieldError('invalid datetime')
        super().process_data(value)


class DateField(DateTimeField):
    def __init__(self, pattern='%Y-%m-%d', **kwargs):
        super().__init__(pattern, **kwargs)

    def process_data(self, value):
        try:
            self._data = datetime.datetime.strptime(value, self.pattern).date()
        except ValueError:
            raise FieldError('invalid date')
        super().process_data(value)


class TimeField(DateTimeField):
    def __init__(self, pattern='%H:%M:%S', **kwargs):
        super().__init__(pattern, **kwargs)

    def process_jsondata(self, value):
        try:
            self._data = datetime.datetime.strptime(value, self.pattern).time()
        except ValueError:
            raise FieldError('invalid time')
        super().process_data(value)


class EnumField(Field):
    def __init__(self, enum_class, **kwargs):
        super().__init__(**kwargs)
        self.enum_class = enum_class

    def process_data(self, value):
        try:
            enum_obj = self.enum_class[value]
        except KeyError:
            raise FieldError('invalid enum')
        self._data = enum_obj
        super().process_data(value)


class BytesField(Field):
    def __init__(self, length, **kwargs):
        super().__init__(**kwargs)
        self.length = length

    def process_data(self, value):
        try:
            self.data = base64.decodebytes(value)
        except (ValueError, TypeError):
            raise FieldError('invalid base64 string')
        if len(self.data) != self.length:
            raise FieldError('invalid length')
        super().process_data(value)


class ListField(Field):
    def __init__(self, field, default=list, **kwargs):
        self.field = field
        self.data_ = None
        super().__init__(default=default, **kwargs)

    @property
    def data(self):
        if not self.data_:
            self.data_ = [field.data for field in self._data]
        return self.data_

    def process_data(self, value):
        if not isinstance(value, list):
            raise FieldError('invalid list')

        self._data = list()
        e = FieldError()
        for i, val in enumerate(value):
            field = self.field.bind()
            try:
                field.process_data(val)
            except FieldError as e_:
                e[i] = e_.error
            self._data.append(field)
        if e:
            raise e
        super().process_data(value)


class SubForm(Field):
    def __init__(self, form, **kwargs):
        self.form = form
        kwargs.pop('condition', None)
        super().__init__(**kwargs)

    def process_data(self, value):
        try:
            self.form.process(jsondata=value)
        except FormError as e_:
            e = FieldError()
            if e_.error:
                e['error'] = e_.error
            if e_.f_errors:
                e['f_errors'] = e_.f_errors
            raise e
