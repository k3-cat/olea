from typing import Tuple

from models import Pit
from olea.errors import StateLocked


def check_state(state: Pit.State, required: Tuple[Pit.State]):
    if state not in required:
        raise StateLocked(current=state, required=required)
