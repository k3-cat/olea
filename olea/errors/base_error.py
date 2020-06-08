import json
import re
from abc import ABC, abstractmethod

from flask import request


class BaseError(BaseException, ABC):
    http_code = 500
    code = ''

    def __init_subclass__(cls):
        cls.pre = re.sub(r'(?!^)([A-Z])', r' \1', cls.__name__) + ' - '
        return super().__init_subclass__()

    @abstractmethod
    def __init__(self, **kwargs):
        self.parms = kwargs
        super().__init__()

    def __json__(self):
        d = {
            'code': self.code,
            'msg': re.sub(r'(?!^)([A-Z])', r' \1', self.__class__.__name__),
            'parms': self.parms
        }

        return d
