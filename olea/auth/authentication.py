from flask import abort, g, request
from sentry_sdk import configure_scope

from models import Pink
from olea.errors import InvalidAccessToken
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
        raise InvalidAccessToken()

    g.pink_id = pink_id
    with configure_scope() as scope:
        scope.user = {'id': pink_id}


def allow_anonymous(f):
    anonymous_endpoints.add(f'auth.{f.__name__}')
    return f


def revoke_all_lemons(pink_or_id):
    # lemons will never be added into session, unless when issuing an access token
    if isinstance(pink_or_id, str):
        pink_or_id = Pink.query.get(pink_or_id)

    pink_or_id.lemons.delete(synchronize_session=False)
