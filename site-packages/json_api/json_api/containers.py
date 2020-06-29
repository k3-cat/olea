__all__ = ['Container']

from jsonschema import Draft7Validator

from .errors import InputError
from .fields import BaseField


class ContainerMeta(type):
    def __new__(cls, name_, bases, attrs):
        if name_ == "Container":
            return type.__new__(cls, name_, bases, attrs)

        fields = dict()
        for name, obj in attrs.items():
            if isinstance(obj, type) and (issubclass(obj, (BaseField, ContainerMeta))):
                fields[name] = obj()

            elif isinstance(obj, (BaseField, Container)):
                fields[name] = obj

        for name in fields.keys():
            attrs.pop(name)

        attrs['__fields__'] = fields

        return type.__new__(cls, name_, bases, attrs)


class Container(metaclass=ContainerMeta):
    _condition = None

    def __init__(self, required=True, condition=None):
        self._required = required
        if condition:
            self._condition = condition
        self._data = dict()

    def __getattr__(self, key):
        return self._data[key]

    def __get_item__(self, key):
        return self.__getattr__(key)

    def schema(self):
        result = {'type': 'object', 'properties': dict(), 'required': list()}
        for name, field in self.__fields__.items():
            if field._required:
                result['required'].append(name)
            result['properties'][name] = field.schema()
        if not result['required']:
            result.pop('required')
        result['additionalProperties'] = False
        return result

    def wrap_data(self, data, errors, extra=None):
        for name, field in self.__fields__.items():
            if name not in data:
                self._data[name] = field.set_default()
                continue

            validator = getattr(self, f'check_{name}')
            self._data[name], errors = field.wrap_data(data[name],
                                                       errors=errors.get(name, None),
                                                       extra=validator)
            if errors is not None:
                errors[name] = errors

        errors = extra(data, errors)

        return (self, errors)

    def process_input(self, data):
        errors = dict()
        v = Draft7Validator(self.schema())
        for e in v.iter_errors(data):
            head = errors
            for i, path in enumerate(e.absolute_path, 1):
                if i == len(e.absolute_path):
                    break
                head.setdefault(path, dict())
                head = head[path]
            head[path] = e.message

        __, errors = self.wrap_data(data, errors)

        if errors:
            raise InputError(errors)
