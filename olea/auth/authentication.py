from flask import abort, g, request
from sentry_sdk import configure_scope

from olea.errors import InvalidCredential
from olea.singleton import redis

anonymous_endpoints = set()


def init_app(app):
    @app.before_request
    def login():
        if request.endpoint not in anonymous_endpoints:
            check_lemon()


def check_lemon():
    try:
        token = request.headers['Authorization']
    except (KeyError, ValueError):
        abort(401)

    if not (pink_id := redis.get(token)):
        raise InvalidCredential(type=InvalidCredential.T.acc)

    g.pink_id = pink_id
    with configure_scope() as scope:
        scope.user = {'id': pink_id}


def allow_anonymous(f):
    anonymous_endpoints.add(f'auth.{f.__name__}')
    return f
