import re
from abc import ABC, abstractmethod
from typing import Iterable

from .errors import FieldError
from .logic_ops import All, Any

__all__ = [
    'BaseCondition', 'AnyValue', 'All', 'Any', 'InRange', 'LenInRange', 'In', 'NotIn',
    'Email', 'Regexp'
]


class BaseCondition(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def check(self, field):
        pass


class AnyValue(BaseCondition):
    def __init__(self):
        super().__init__()

    def check(self, field):
        pass


class InRange(BaseCondition):
    def __init__(self, min_val=None, max_val=None):
        self.min = min_val
        self.max = max_val

    def check(self, field):
        if self.min is not None and field.data < self.min:
            raise FieldError(e=f'value smaller than {self.min}')
        if self.max is not None and field.data >= self.max:
            raise FieldError(e=f'value bigger than {self.max}')


class LenInRange(BaseCondition):
    def __init__(self, min_len=None, max_len=None):
        self.min = min_len
        self.max = max_len

    def check(self, field):
        if self.min is not None and len(field.data) < self.min:
            raise FieldError(e=f'items less than {self.min}')
        if self.max is not None and len(field.data) > self.max:
            raise FieldError(e=f'items more than {self.max}')


class In(BaseCondition):
    def __init__(self, *values):
        self.values = set(values)

    def check(self, field):
        try:
            if isinstance(field.data, str):
                raise TypeError()
            data = set(field.data)
        except TypeError:
            data = set()
            data.add(field.data)
        if len(data | self.values) > len(self.values):
            raise FieldError(e='not allow: ' +
                             ', '.join({str(val)
                                        for val in (data - self.values)}))


class NotIn(BaseCondition):
    def __init__(self, *values):
        self.values = set(values)

    def check(self, field):
        try:
            if isinstance(field.data, str):
                raise TypeError()
            data = set(field.data)
        except TypeError:
            data = set()
            data.add(field.data)
        if len(data | self.values) == len(self.values):
            raise FieldError(e='not allow: ' +
                             ', '.join({str(val)
                                        for val in (data & self.values)}))


class Regexp(BaseCondition):
    def __init__(self, regex, flags=0, message=None):
        if isinstance(regex, str):
            regex = re.compile(regex, flags)
        self.regex = regex
        self.msg = message

    def check(self, field):
        match = self.regex.match(field.data)
        if not match:
            raise FieldError(e=f'input does not match the pattern {self.regex}'
                             if not self.msg else self.msg)


class Email(Regexp):
    def __init__(self, message='invalid email address'):
        super().__init__(
            regex=r'^[a-z0-9._-]+@(?:[a-z0-9-]+\.)+[a-z]{2,4}$',
            flags=re.IGNORECASE,
            message=message,
        )
