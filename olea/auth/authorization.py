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
        for duck in Duck.query.filter_by(pink_id=pink_id):
            t.add(duck.node) if duck.allow else f.add(duck.node)
        redis.set(f'{pink_id}-T', t)
        redis.set(f'{pink_id}-F', f)

    @staticmethod
    def has_duck(node):
        if not redis.exist(f'{g.pink_id}-T'):
            DuckPermission.cache_ducks(g.pink_id)
        return redis.sismember(f'{g.pink_id}-T', node)

    @staticmethod
    def check_duck(default_pass, node):
        if not node:
            path = request.path
            if path.endswith('/'):
                path += 'all'
            node = re.sub(r'^/([a-z]*).*/([a-z_]*)$', r'\1.\2', path)
        g.node = node

        if not redis.exist(f'{g.pink_id}-T'):
            DuckPermission.cache_ducks(g.pink_id)

        if (not default_pass and not redis.sismember(f'{g.pink_id}-T', node)) or \
            (default_pass and redis.sismember(f'{g.pink_id}-F', node)):
            raise PermissionDenied()

    @staticmethod
    def check_scopes(scopes):
        duck = Duck.query.fiter_by(node=g.node, pink_id=g.pink_id).first()
        scope_set = set(duck.scopes)
        # when scope_set is empty, it means ANY SCOPE
        if (duck.allow and (diff := scopes - scope_set)) or \
            (not duck.allow and (diff := scopes & scope_set if scope_set else scopes)):
            raise PermissionDenied(scope=diff)

    def optinal_permission(self, node=''):
        def decorate(f):
            def check_opt_duck(scopes=None):
                try:
                    self.check_duck(False, node)
                    passed = True
                except PermissionDenied:
                    passed = False
                if scopes:
                    self.check_scopes(scopes)
                return passed

            @wraps(f)
            def wrapper(*args, **kwargs):
                g.check_duck = check_opt_duck
                result = f(*args, **kwargs)
                return result

            return self.login(wrapper)

        return decorate

    def permission_required(self, default_pass=False, node=''):
        def decorate(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                self.check_duck(default_pass, node)
                g.check_scope = self.check_scopes
                result = f(*args, **kwargs)
                return result

            return self.login(wrapper)

        return decorate
