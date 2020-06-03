import enum
from abc import ABC, abstractmethod

from .errors import FieldError, FormError
from .fields import UnboundField


class JsonForm(ABC):
    def __init__(self, data: dict = None):
        self.fields = list()
        for name, obj in self.__class__.__dict__.items():
            if not isinstance(obj, UnboundField):
                continue
            self.fields.append(name)
            field = obj.bind()
            setattr(self, f'_{name}_', field)
            setattr(self, name, lambda: field.data)

        if data:
            self.process(data)

    def __getitem__(self, key):
        return getattr(self, key).data

    def test_empty(self, name):
        if name in self.fields:
            return getattr(self, f'_{name}_').is_empty
        raise AttributeError()

    def process(self, data: dict):
        e = FormError()
        for name in set(data.keys()) | set(self.fields):
            if name not in self.fields:
                e[name] = 'unknow field'
                continue

            field = getattr(self, f'_{name}_')
            try:
                if name not in data or not data[name]:
                    field.mark_empty()
                else:
                    field.process_data(data[name])
                if inline_check := getattr(self, f'check_{name}', None):
                    inline_check(field)
            except FieldError as e_:
                e_.clean()
                e[name] = e_.error
        try:
            if form_check := getattr(self, 'check', None):
                form_check()
        except FormError as e_:
            e.error = e_.error

        if e:
            raise e
