import enum
from abc import ABC
from typing import Dict, Iterable

from .base_error import BaseError


class BadOpt(BaseError, ABC):
    http_code = 403


# ------------------- proj ---------------------


class RolesLocked(BadOpt):
    code = 'I4HX'

    def __init__(self, state):
        super().__init__(state=state)


class InvalidSource(BadOpt):
    code = '4JZE'

    invalid_input = lambda: InvalidSource(rsn='invalid input')
    not_found = lambda: InvalidSource(rsn='not found')
    web_not_exist = lambda url: InvalidSource(rsn='web page does not exist', url=url)


class RoleIsTaken(BadOpt):
    code = '4J67'

    def __init__(self, by):
        super().__init__(pink_id=by.id, pink_name=by.name)


class NotQualifiedToPick(BadOpt):
    code = 'CWAI'

    def __init__(self, dep):
        super().__init__(dep=dep.name)


# ------------------- pink ---------------------


class PwdTooWeek(BadOpt):
    code = ''

    low_strength = lambda strength: PwdTooWeek(rsn='low strength', strength=strength)
    common_pwd = lambda: PwdTooWeek(rsn='common password')


# ------------------- pit ---------------------


class StateLocked(BadOpt):
    code = 'L5OM'

    def __init__(self, current, required: Iterable):
        required_list = [req.name for req in required]
        super().__init__(curret=current.name, required=required_list)


# ------------------- o3o ---------------------


class UnallowedType(BadOpt):
    code = 'C3D8'

    def __init__(self, mime: str, required: str):
        super().__init__(mime=mime, required=required)


class DoesNotMeetRequirements(BadOpt):
    code = '84RX'

    def __init__(self, confl: Dict[str, str], required: Dict[str, str], token):
        super().__init__(confl=confl, required=required, token=token)
