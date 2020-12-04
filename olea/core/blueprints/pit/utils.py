from functools import wraps
from typing import Set

from flask import g

from models import Pit
from olea.errors import AccessDenied, PitStatusLocked


def check_owner(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.o.pink_id != g.pink_id:
            raise AccessDenied(obj=self.o)
        return f(self, *args, **kwargs)

    return wrapper


def check_status(required: Set[Pit.S]):
    def decorate(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if self.o.status not in required:
                raise PitStatusLocked(current=self.o.status, required=required)
            return f(self, *args, **kwargs)

        return wrapper

    return decorate
