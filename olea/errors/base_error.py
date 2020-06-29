import re

from flask import g


class BaseError(Exception):
    http_code = 500
    code = ''

    def __init_subclass__(cls):
        cls.pre = re.sub(r'(?!^)([A-Z])', r' \1', cls.__name__) + ' - '
        return super().__init_subclass__()

    def __init__(self, **kwargs):
        self.parms = kwargs
        super().__init__()

    def __json__(self):
        d = {
            'code': self.code,
            'ref': g.ref,
            'msg': re.sub(r'(?!^)([A-Z])', r' \1', self.__class__.__name__),
            'parms': self.parms
        }

        return d
