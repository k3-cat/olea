import enum
from typing import Iterable

from .base_error import BaseError


class BadOpt(BaseError):
    http_code = 403


# -------------------------------------------------------------


class ProjMetaLocked(BadOpt):
    code = 'CUGMS'

    def __init__(self, status):
        super().__init__(status=status)


class InvalidSource(BadOpt):
    code = 'M1CDO'

    class Rsn(enum.Enum):
        inp = 'invalid input'
        non = 'not found'
        web = 'web page not found'

    def __init__(self, rsn: 'Rsn', url=''):
        if rsn == InvalidSource.Rsn.web:
            super().__init__(rsn=rsn.name, url=url)
        else:
            super().__init__(rsn=rsn.name)


class RoleIsTaken(BadOpt):
    code = 'IFHK2'

    def __init__(self, by):
        super().__init__(pink_id=by.id, pink_name=by.name)


class InvalidReply(BadOpt):
    code = 'GAQNX'


class PitStatusLocked(BadOpt):
    code = '2VCI9'

    def __init__(self, current, required: Iterable):
        required_list = [req.name for req in required]
        super().__init__(curret=current.name, required=required_list)
