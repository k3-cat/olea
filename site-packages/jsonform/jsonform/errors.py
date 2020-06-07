import re
from abc import ABC


class FieldError(BaseException):
    def __init__(self, e=None):
        if e:
            if isinstance(e, str):
                self.error = set()
                self.error.add(e)
            else:
                raise TypeError()
        else:
            self.error = None

    def __setitem__(self, key, item):
        if not self.error:
            self.error = dict()
        if key not in self.error:
            self.error[key] = FieldError()
        if isinstance(item, set):
            self.error[key].extend(item)
        elif isinstance(item, dict):
            self.error[key].error = item
        else:
            raise TypeError()

    def __bool__(self):
        return bool(self.error)

    def extend(self, error):
        if not self.error:
            self.error = set()
        self.error = self.error | error

    def clean(self):
        if isinstance(self.error, dict):
            for key, item in self.error.items():
                if isinstance(item, FieldError):
                    item.clean()
                    self.error[key] = item.error
        elif len(self.error) == 1:
            self.error = self.error.pop()


class FormError(BaseException):
    def __init__(self, error=None):
        self.error = error
        self.f_errors = dict()

    def __setitem__(self, name, error):
        self.f_errors[name] = error

    def __bool__(self):
        return bool(self.f_errors) or bool(self.error)

    def __json__(self):
        d = {'msg': 'Form Error'}
        if self.error:
            d['errors'] = self.error
        if self.f_errors:
            d['field_errors'] = self.f_errors
        return d
