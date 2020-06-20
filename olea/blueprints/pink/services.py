from flask import current_app, g

from models import Duck, Pink
from olea import email_mgr
from olea.auth import authorization
from olea.base import BaseMgr
from olea.errors import InvalidCredential, RecordNotFound
from olea.singleton import db, redis
from olea.utils import random_b85


class PinkMgr(BaseMgr):
    model = Pink

    t_life = current_app.config['DEPS_TOKEN_LIFE'].seconds

    def __init__(self, obj_or_id):
        self.o: Pink = None
        super().__init__(obj_or_id)

    @classmethod
    def assign_token(cls, deps, amount):
        g.check_scopes(deps)
        deps_s = ','.join(deps)
        tokens = [random_b85(k=20) for __ in range(amount)]
        redis.mset({f'deps-{token}':deps_s for token in tokens}, ex=cls.t_life)
        return tokens

    @classmethod
    def sign_up(cls, name: str, qq: int, other: str,pwd, email_token: str, deps_token: list):
        pink = cls.model(id=cls.gen_id(), name=name, qq=str(qq), other=other)
        if not (deps_s := redis.get(f'deps-{deps_token}')):
            raise InvalidCredential(type_=InvalidCredential.T.deps)
        pink.pwd = pwd
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
            raise InvalidCredential(type_=InvalidCredential.T.email)
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
        self.o: Duck = None
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
