import re
from functools import wraps

from flask import abort, g, request

from models import Duck
from olea.errors import PermissionDenied
from olea.exts import db, redis


def clean_cache(pink_id):
    redis.delete(f'duckT-{pink_id}')
    redis.delete(f'duckF-{pink_id}')


def cache_ducks(pink_id):
    t = f'duckT-{pink_id}'
    f = f'duckF-{pink_id}'
    if redis.exist(t):
        return
    for duck in Duck.query.filter_by(pink_id=pink_id):
        redis.hset(t if duck.allow else f, duck.node, ';'.join(duck.scopes))


def has_duck(node):
    cache_ducks(g.pink_id)
    return redis.hexist(f'duckT-{g.pink_id}', node)


def check_duck(default_pass, node):
    if not node:
        path = request.path
        if path.endswith('/'):
            path += 'all'
        node = re.sub(r'^/([a-z]*).*/([a-z_]*)$', r'\1.\2', path)
    g.node = node

    cache_ducks(g.pink_id)
    if (not default_pass and not redis.hexist(f'duckT-{g.pink_id}', node)) or \
        (default_pass and redis.hexist(f'duckF-{g.pink_id}', node)):
        raise PermissionDenied()


def check_scopes(default_pass, scopes):
    raw_scope = redis.hget(f'duck{"T" if default_pass else "F"}-{g.pink_id}', g.node)
    scope_set = set(raw_scope.split(';'))
    # when scope_set is empty, it means ANY SCOPE
    if (default_pass and (diff := scopes - scope_set)) or \
        (not default_pass and (diff := scopes & scope_set if scope_set else scopes)):
        raise PermissionDenied(scope=diff)


def optinal_permission(node=''):
    def check_opt_duck(scopes=None):
        try:
            check_duck(False, node)
            passed = True
        except PermissionDenied:
            passed = False
        if passed and scopes:
            check_scopes(False, scopes)
        return passed

    def decorate(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            g.check_duck = check_opt_duck
            return f(*args, **kwargs)

        return wrapper

    return decorate


def permission_required(default_pass=False, node=''):
    def decorate(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            check_duck(default_pass, node)
            g.check_scope = lambda scopes: check_scopes(default_pass, scopes)
            return f(*args, **kwargs)

        return wrapper

    return decorate
