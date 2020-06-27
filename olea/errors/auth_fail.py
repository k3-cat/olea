import enum
from abc import ABC

from flask import g

from .base_error import BaseError


class AuthFail(BaseError, ABC):
    http_code = 401

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AccessDenied(AuthFail):
    code = 'HJESU'

    def __init__(self, obj=None, cls_=None):
        if obj:
            super().__init__(cls=obj.__class__.__name__, id=obj.id)
        else:
            super().__init__(cls=cls_.__name__)


class PermissionDenied(AuthFail):
    code = 'XUZ19'

    def __init__(self, scope: set = None):
        if scope:
            super().__init__(node=g.node, scope=scope)
        else:
            super().__init__(node=g.node)


class AccountDeactivated(AuthFail):
    code = '7UCDA'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class InvalidCredential(AuthFail):
    code = 'R6WET'

    class T(enum.Enum):
        pwd = 'pwd'
        rst = 'reset token'
        new = 'creation token'
        email = 'email verification token'

    def __init__(self, type_: 'InvalidCredential.T'):
        super().__init__(type=type_)


class InvalidAccessToken(AuthFail):
    code = 'G1PP5'

    def __init__(self):
        super().__init__()


class InvalidRefreshToken(AuthFail):
    code = 'TICTK'

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
