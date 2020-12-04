import re

from flask import g


class BaseError(Exception):
    http_code = 500
    code = ''

    def __new__(cls, *args, **kwargs):
        pre = re.sub(r'(?!^)([A-Z])', r' \1', cls.__base__.__name__)
        cls.msg = pre + ' - ' + re.sub(r'(?!^)([A-Z])', r' \1', cls.__name__)
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, **kwargs):
        self.parms = kwargs
        super().__init__()

    def __json__(self):
        d = {
            'code': self.code,
            'ref': g.ref,
            'msg': self.msg,
            'parms': self.parms
        }

        return d
