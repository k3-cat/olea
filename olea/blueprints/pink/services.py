from flask import current_app, g

from models import Duck, Pink
from olea import email_mgr
from olea.auth import authorization
from olea.base import BaseMgr, single_query
from olea.errors import RecordNotFound
from olea.singleton import db, redis
from olea.utils import random_b85


class PinkQuery():
    @staticmethod
    def single(id_):
        return single_query(model=Pink, id_or_obj=id_, condiction=lambda obj: obj.id == g.pink_id)

    @staticmethod
    def search(deps, name, qq):
        query = Pink.query
        if deps:
            query.filter(Pink.deps.in_(deps))
        else:
            if name:
                query.filter(Pink.name.ilike(f'%{name}%'))
            if qq:
                query.filter(Pink.qq.like(f'%{qq}%'))
        return query.all()

    @staticmethod
    def ducks(pink_id, node, nodes, allow):
        query = Duck.query.filter_by(pink_id=pink_id)
        if node:
            query.filter(Duck.node.ilike(f'%{node}%'))
        else:
            if nodes:
                query.filter(Duck.node.in_(nodes))
            if allow is not None:
                query.filter_by(allow=allow)
        return query.all()


class PinkMgr(BaseMgr):
    model = Pink

    def __init__(self, obj_or_id):
        self.o: self.model = None
        super().__init__(obj_or_id)

    @staticmethod
    def assign_token(deps):
        g.check_scope(deps)
        # TODO: set time out
        token = random_b85(k=20)
        redis.set(f'deps-{token}', ','.join(deps), ex=86400 * 3)
        return token

    @classmethod
    def create(cls, name: str, qq: int, other: str,pwd, email_token: str, deps_token: list):
        pink = cls.model(id=cls.gen_id(), name=name, qq=str(qq), other=other)
        pink.pwd = pwd
        if not (deps_s := redis.get(f'deps-{deps_token}')):
            # TODO: add new error type
            raise Exception()
        pink.deps = deps_s.split(',')
        PinkMgr(pink).set_email(email_token)
        db.session.add(pink)
        email_mgr.new_pink(email=pink.email, name=pink.name)
        return pink

    def update_info(self, qq: int, other: str):
        if qq:
            self.o.qq = str(qq)
        if other:
            self.o.other = other

    def set_email(self, token):
        if not (email := redis.get(f've-{token}')):
            # TODO: add new error type
            raise Exception
        self.o.email = email

    def deactive(self):
        self.o.active = False
        self.o.lemons.delete()
        return True

    def alter_ducks(self, add, remove):
        conflicts = self.o.ducks.filter(Duck.node.in_(add.keys())).all()
        for node in add.keys() - {conflict.node for conflict in conflicts}:
            info = add[node]
            duck = self.model(pink_id=self.o.id,
                              node=node,
                              allow=info['allow'],
                              scopes=list(info['scopes']))
            self.o.ducks.add(duck)
        if remove:
            self.o.ducks.filter(Duck.node.in_(remove)).delete()
        authorization.clean_cache()
        return (self.o.ducks.all(), conflicts)


class DuckMgr(BaseMgr):
    modle = Duck

    def __init__(self, /, pink_id, node):
        self.o: self.model = None
        if not (obj := self.model.query.get((pink_id, node))):
                raise RecordNotFound(cls=self.model, id=(','.join((pink_id, node))))
        self.o = obj

    def alter_scopes(self, scopes: set):
        self.o.scopes = list(scopes)
        db.session.add(self.o)
        authorization.clean_cache(self.o.pink_id)
        return scopes

    def add_scopes(self, scopes):
        return self.alter_scopes(set(self.o.scopes) | scopes)

    def remove_scopes(self, scopes):
        return self.alter_scopes(set(self.o.scopes) - scopes)
