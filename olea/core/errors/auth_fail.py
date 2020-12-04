import enum

from .base_error import BaseError


class AuthFail(BaseError):
    http_code = 401


# -------------------------------------------------------------


class AccessDenied(AuthFail):
    code = 'VIPKE'

    def __init__(self, obj=None, cls_=None):
        if obj:
            super().__init__(cls=obj.__class__.__name__, id=obj.id)
        else:
            super().__init__(cls=cls_.__name__)


class PermissionDenied(AuthFail):
    code = 'XUZ19'

    def __init__(self, node: str, scope: set = None):
        if scope:
            super().__init__(node=node, scope=scope)
        else:
            super().__init__(node=node)


class AccountDeactivated(AuthFail):
    code = '7UCDA'


class InvalidCredential(AuthFail):
    code = 'R6WET'

    class T(enum.Enum):
        pwd = 'pwd'
        rst = 'reset token'
        new = 'creation token'
        email = 'email verification token'

    def __init__(self, type_: 'T'):
        super().__init__(type=type_)


class InvalidAccessToken(AuthFail):
    code = 'G1PP5'


class InvalidRefreshToken(AuthFail):
    code = 'TICTK'

    class Rsn(enum.Enum):
        exp = 'expired'
        key = 'invalid key'
        non = 'non exist'
        ip = 'location change'

    def __init__(self, rsn: 'Rsn', at=None):
        if rsn == InvalidRefreshToken.Rsn.exp:
            super().__init__(rsn=rsn.name, at=at)
        else:
            super().__init__(rsn=rsn.name)
