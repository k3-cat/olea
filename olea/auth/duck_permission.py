from functools import wraps

from flask import abort, g, request

from olea.exts import db, rediss


class DuckPermission:
    def get_scope(self):
        try:
            scopes = request.headers['Scope'].split()
        except (KeyError, ValueError):
            abort(400)
        return scopes

    def verify_duck(self, lemon):
        return True

    def login_required(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            scope, key = self.get_key()
            self.verify_duck(query_lemon(key))
            return f(*args, **kwargs)

        return decorated
