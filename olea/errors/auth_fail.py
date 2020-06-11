import enum
from abc import ABC

from flask import g

from .base_error import BaseError


class AuthFail(BaseError, ABC):
    http_code = 401

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AccessDenied(AuthFail):
    code = 'UJCB'

    def __init__(self, obj: object, cls: object):
        if obj:
            super().__init__(cls=obj.__class__.__name__, id=obj.id)
        else:
            super().__init__(cls=cls.__name__)


class PermissionDenied(AuthFail):
    code = 'abcd'

    def __init__(self, scope: set = None):
        if scope:
            super().__init__(node=g.node, scope=scope)
        else:
            super().__init__(node=g.node)


class AccountDeactivated(AuthFail):
    code = 'ssss'


class InvalidCredential(AuthFail):
    code = '516O'

    class T(enum.Enum):
        pwd = 'pwd'
        acc = 'access token'
        rst = 'reset token'

    def __init__(self, type: 'InvalidCredential.T'):
        super().__init__(type=type)


class InvalidRefreshToken(AuthFail):
    code = '516O'

    class Rsn(enum.Enum):
        exp = 'expired'
        key = 'invalid key'
        non = 'non exist'
        ip = 'location change'

    def __init__(self, rsn: 'InvalidRefreshToken.Rsn', at=None):
        if rsn == InvalidRefreshToken.Rsn.exp:
            super().__init__(rsn=rsn.name, at=at)
        else:
            super().__init__(rsn=rsn.name)
