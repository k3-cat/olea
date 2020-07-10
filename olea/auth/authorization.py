from functools import wraps
from typing import Dict, Set

from flask import g, request

from models import Duck
from olea.errors import PermissionDenied
from olea.singleton import redis, sqlogger


class DuckCache():
    @staticmethod
    def clean(pink_id):
        redis.delete(f'duckT-{pink_id}', f'duckF-{pink_id}')

    @staticmethod
    def cache(pink_id):
        t = f'duckT-{pink_id}'
        f = f'duckF-{pink_id}'
        if redis.exist(t):
            return
        for duck in Duck.query.filter_by(pink_id=pink_id):
            redis.hset(t if duck.allow else f, duck.node, ';'.join(duck.scopes))


class Node():
    index: Dict[str, str] = dict()
    white: Set[str] = set()

    @classmethod
    def register(cls, func, default_pass, node):
        endpoint = f'{func.__module__.split(".")[-2]}.{func.__name__}'

        cls.index[endpoint] = node if node else endpoint

        if default_pass:
            cls.white.add(endpoint)

    @classmethod
    def get(cls):
        endpoint = request.endpoint
        if not endpoint:
            return (False, '')
        return (endpoint in cls.white, cls.index[endpoint])


def _check_duck():
    DuckCache.cache(g.pink_id)

    default_pass, node = Node.get()
    if ((not default_pass and not redis.hexists(f'duckT-{g.pink_id}', node))
            or (default_pass and redis.hexists(f'duckF-{g.pink_id}', node))):
        raise PermissionDenied(node=node)


def check_scopes(scopes):
    default_pass, node = Node.get()

    raw_scope = redis.hget(f'duck{"T" if default_pass else "F"}-{g.pink_id}', node)
    scope_set = set(raw_scope.split(';'))
    # when scope_set is empty, it means ANY SCOPE
    if (default_pass and (diff := scopes - scope_set)) \
            or (not default_pass and (diff := scopes & scope_set if scope_set else scopes)):
        raise PermissionDenied(node=node, scope=diff)


def check_opt_duck(scopes=None):
    try:
        _check_duck()
        if scopes:
            check_scopes(scopes)

    except PermissionDenied:
        return False

    return True


def permission_required(default_pass=False, node=''):
    def decorated(f):
        Node.register(f, default_pass, node)

        @wraps(f)
        def wrapper(*args, **kwargs):
            _check_duck()
            sqlogger.log(level='perm', info='')

            return f(*args, **kwargs)

        return wrapper

    return decorated


def optional_permission(node=''):
    def decorated(f):
        Node.register(f, False, node)

        return f

    return decorated
