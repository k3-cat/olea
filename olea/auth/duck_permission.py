import re
from functools import wraps

from flask import abort, g, request

from models import Duck
from olea.errors import PermissionDenied
from olea.exts import db, redis


class DuckPermission:
    def cache_ducks(self):
        redis.set(f'{g.pink_id}-T', 1, ex=2)
        redis.set(f'{g.pink_id}-F', 1, ex=2)

    def check_duck(self, default, node):
        if not node:
            node = re.sub(r'^/([a-z]*).*/([a-z_]*)$', r'\1.\2', request.path)
        g.node = node

        if not redis.exist(f'{g.pink_id}-T'):
            self.cache_ducks()

        if (default and not redis.sismember(f'{g.pink_id}-T', node)) or \
            (not default and redis.sismember(f'{g.pink_id}-F', node)):
            raise PermissionDenied()

    def check_scopes(self, default):
        if not g.scopes:
            return

        scope_set = set(Duck.query().fiter_by(node=g.node, pink_id=g.pink_id).first().scope)
        if (default and (diff := g.scope - scope_set)) or \
            (not default and (diff := g.scope & scope_set)):
            raise PermissionDenied(scope=diff)

    def permission_required(self, default=False, node=''):
        def decorate(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                self.check_duck(default, node)
                result = f(*args, **kwargs)
                self.check_scopes(default)
                return result

            return wrapper

        return decorate
