from flask import current_app

from models import Duck, Lemon, Pink
from olea import email_mgr
from olea.auth import authorization
from olea.base import BaseMgr, single_query
from olea.errors import AccessDenied, DuplicatedRecord, InvalidCredential
from olea.exts import db, redis
from olea.utils import random_b85

from ..auth.pwd_tools import generate_pwd


class PinkQuery():
    @staticmethod
    def single(id_):
        return single_query(id_)

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

    t_life = current_app.config['PWD_RESET_TOKEN_LIFE'].seconds

    def __init__(self, obj_or_id):
        self.o: self.model = None
        super().__init__(obj_or_id)

    @classmethod
    def create(cls, name: str, qq: int, other: str, email: str, deps: list):
        pwd = generate_pwd()
        pink = cls.model(
            id=cls.gen_id(),
            name=name,
            qq=str(qq),
            other=other,
            email=email,
            deps=deps,
        )
        pink.pwd = pwd
        db.session.add(pink)
        email_mgr.new_pink(email=pink.email, name=pink.name, pwd=pwd)
        return pink

    def update_info(self, qq: int, line: str, email: str):
        if qq:
            self.o.qq = str(qq)
        if line:
            self.o.line = line
        if email:
            self.o.email = email
        return True

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

    def __init__(self, obj_or_id):
        self.o: self.model = None
        super().__init__(obj_or_id)

    def alter_scopes(self, scopes: set):
        self.o.scopes = list(scopes)
        db.session.add(self.o)
        authorization.clean_cache()
        return scopes

    def add_scopes(self, scopes):
        return self.alter_scopes(set(self.o.scopes) | scopes)

    def remove_scopes(self, scopes):
        return self.alter_scopes(set(self.o.scopes) - scopes)
