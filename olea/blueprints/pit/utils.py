from typing import Tuple

from models import PitState
from olea.errors import StateLocked


def check_state(state: PitState, required: Tuple[PitState]):
    if state not in required:
        raise StateLocked(current=state, required=required)
