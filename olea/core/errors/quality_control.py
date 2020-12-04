import enum
from typing import Dict

from .base_error import BaseError


class QualityControl(BaseError):
    http_code = 409


# -------------------------------------------------------------


class NotQualifiedToPick(QualityControl):
    code = 'E9QVS'

    def __init__(self, dep):
        super().__init__(dep=dep)


class WeekPwd(QualityControl):
    code = '4SPSN'

    class Rsn(enum.Enum):
        common = 'common pwd'
        strength = 'low strength'

    def __init__(self, rsn: 'Rsn', strength=0.0):
        if rsn == WeekPwd.Rsn.strength:
            super().__init__(rsn=rsn.name, strength=strength)
        else:
            super().__init__(rsn=rsn.name)


class DoesNotMeetRequirements(QualityControl):
    code = 'Y42HF'

    def __init__(self, confl: Dict[str, str], required: Dict[str, str], token):
        super().__init__(confl=confl, required=required, token=token)
