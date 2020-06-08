from functools import wraps

from flask import abort, g, request
from sentry_sdk import configure_scope

from models import Pink
from olea.errors import InvalidCredential
from olea.exts import db, redis


class LemonAuth:
    def __init__(self, scheme='Bearer'):
        self.scheme = scheme.upper()

    def check_lemon(self):
        try:
            scheme, token = request.headers['Authorization'].split(maxsplit=1)
        except (KeyError, ValueError):
            abort(400)
        if scheme.upper() != self.scheme:
            abort(400)

        if not (pink_id := redis.get(token)):
            raise InvalidCredential(type=InvalidCredential.T.acc)

        g.pink_id = pink_id
        with configure_scope() as scope:
            scope.user = {'id': pink_id}

        return True

    def login_required(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            self.check_lemon()
            return f(*args, **kwargs)

        return wrapper
