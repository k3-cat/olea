import enum
from typing import Dict, Iterable

from .base_error import BaseError


class BadOpt(BaseError):
    http_code = 403


# ------------------- proj ---------------------


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

    def __init__(self, rsn: 'InvalidSource.Rsn', url=''):
        if rsn == InvalidSource.Rsn.web:
            super().__init__(rsn=rsn.name, url=url)
        else:
            super().__init__(rsn=rsn.name)


class RoleIsTaken(BadOpt):
    code = 'IFHK2'

    def __init__(self, by):
        super().__init__(pink_id=by.id, pink_name=by.name)


class NotQualifiedToPick(BadOpt):
    code = 'E9QVS'

    def __init__(self, dep):
        super().__init__(dep=dep)


class InvalidReply(BadOpt):
    code = 'GAQNX'


# ------------------- pink ---------------------


class WeekPwd(BadOpt):
    code = '4SPSN'

    class Rsn(enum.Enum):
        common = 'common pwd'
        strength = 'low strength'

    def __init__(self, rsn: 'WeekPwd.Rsn', strength=0.0):
        if rsn == WeekPwd.Rsn.strength:
            super().__init__(rsn=rsn.name, strength=strength)
        else:
            super().__init__(rsn=rsn.name)


# ------------------- pit ---------------------


class PitStatusLocked(BadOpt):
    code = '2VCI9'

    def __init__(self, current, required: Iterable):
        required_list = [req.name for req in required]
        super().__init__(curret=current.name, required=required_list)


# ------------------- o3o ---------------------


class UnallowedType(BadOpt):
    code = 'YP3OM'

    def __init__(self, mime: str, required: str):
        super().__init__(mime=mime, required=required)


class DoesNotMeetRequirements(BadOpt):
    code = 'Y42HF'

    def __init__(self, confl: Dict[str, str], required: Dict[str, str], token):
        super().__init__(confl=confl, required=required, token=token)
