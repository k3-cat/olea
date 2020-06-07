import enum
from abc import ABC

from .base_error import BaseError


class AuthFail(BaseError, ABC):
    http_code = 401

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AccessDenied(AuthFail):
    code = 'UJCB'

    def __init__(self, obj: object):
        super().__init__(cls=obj.__class__.__name__, id=obj.id)


class AccountDeactivated(AuthFail):
    code = 'ssss'


class InvalidCredential(AuthFail):
    code = '516O'


class InvalidAccessToken(AuthFail):
    code = '516O'


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
            super().__init__(rsn=rsn.name, at=at)
