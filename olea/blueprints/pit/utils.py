from functools import wraps
from typing import Set

from flask import g

from models import Pit
from olea.errors import AccessDenied, StateLocked


def check_owner(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.o.pink_id != g.pink_id:
            raise AccessDenied(obj=self.o)
        return f(self, *args, **kwargs)

    return wrapper


def check_state(required: Set[Pit.S]):
    def decorate(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if self.o.state not in required:
                raise StateLocked(current=self.o.state, required=required)
            return f(self, *args, **kwargs)

        return wrapper

    return decorate
