import re
from functools import wraps

from flask import abort, g, request

from models import Duck
from olea.errors import PermissionDenied
from olea.exts import db, redis


class DuckPermission():
    def __init__(self, login):
        self.login = login

    @staticmethod
    def clean_cache(pink_id):
        redis.delete(f'{pink_id}-T')
        redis.delete(f'{pink_id}-F')

    @staticmethod
    def cache_ducks(pink_id):
        t = set()
        f = set()
        for duck in Duck.query().filter_by(pink_id=pink_id):
            t.add(duck.node) if duck.allow else f.add(duck.node)
        redis.set(f'{pink_id}-T', t)
        redis.set(f'{pink_id}-F', f)

    def check_duck(self, default, node):
        if not node:
            node = re.sub(r'^/([a-z]*).*/([a-z_]*)$', r'\1.\2', request.path)
        g.node = node

        if not redis.exist(f'{g.pink_id}-T'):
            self.cache_ducks(g.pink_id)

        if (default and not redis.sismember(f'{g.pink_id}-T', node)) or \
            (not default and redis.sismember(f'{g.pink_id}-F', node)):
            raise PermissionDenied()

    def check_scopes(self, default):
        if not g.scopes:
            return

        # when scope_set is empty, it means ANY SCOPE
        scope_set = set(Duck.query().fiter_by(node=g.node, pink_id=g.pink_id).first().scope)
        if (default and (diff := g.scope - scope_set)) or \
            (not default and (diff := g.scope & scope_set if scope_set else g.scope)):
            raise PermissionDenied(scope=diff)

    def permission_required(self, default=False, node=''):
        def decorate(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                self.check_duck(default, node)
                result = f(*args, **kwargs)
                self.check_scopes(default)
                return result

            return self.login(wrapper)

        return decorate
