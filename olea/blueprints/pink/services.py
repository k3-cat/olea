from flask import g

from models import Duck, Pink
from olea import email_mgr
from olea.auth import authorization
from olea.auth.authentication import revoke_all_lemons
from olea.base import BaseMgr
from olea.errors import InvalidCredential, RecordNotFound
from olea.singleton import db, pat, redis
from olea.utils import FromConf, random_b85


class PinkMgr(BaseMgr):
    model = Pink

    t_life = FromConf('TL_NEW_PINK')

    def __init__(self, obj_or_id):
        self.o: Pink = None
        super().__init__(obj_or_id)

    @classmethod
    def assign_token(cls, deps, amount):
        g.check_scopes(deps)
        deps_s = ','.join(deps)
        tokens = [random_b85(k=20) for __ in range(amount)]
        redis.mset({f'deps-{token}': deps_s for token in tokens}, ex=cls.t_life.seconds)
        return tokens

    @classmethod
    def sign_up(cls, name: str, pwd, qq: int, other: str, email_token: str, deps_token: list):
        if not (deps_s := redis.get(f'deps-{deps_token}')):
            raise InvalidCredential(type_=InvalidCredential.T.new)

        pink = cls.model(id=cls.gen_id(), name=name, email=None, qq=str(qq), other=other)
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
        payload = pat.decode(token)
        if self.o.email != payload['old']:
            raise InvalidCredential(type_=InvalidCredential.T.email)

        self.o.email = payload['new']

    def deactive(self):
        self.o.active = False

        revoke_all_lemons(self.o)

    def alter_ducks(self, add, remove):
        conflicts = self.o.ducks.filter(Duck.node.in_(add.keys())).all()

        for node in add.keys() - {conflict.node for conflict in conflicts}:
            info = add[node]
            DuckMgr.grante(pink_id=self.o.id,
                           node=node,
                           allow=info['allow'],
                           scopes=list(info['scopes']))

        if remove:
            self.o.ducks.filter(Duck.node.in_(remove)).delete()

        authorization.clean_cache(pink_id=self.o.id)

        return (self.o.ducks.all(), conflicts)


class DuckMgr(BaseMgr):
    modle = Duck

    def __init__(self, /, pink_id, node):
        self.o: Duck = None
        if not (obj := self.model.query.get((pink_id, node))):
            raise RecordNotFound(cls_=self.model, id_=(','.join((pink_id, node))))
        self.o = obj

    @classmethod
    def grante(cls, pink_id, node, allow, scopes):
        duck = cls.model(pink_id=pink_id,
                         node=node,
                         allow=allow,
                         scopes=scopes)
        db.session.add(duck)

        return duck


    def modi_scopes(self, scopes: set):
        self.o.scopes = list(scopes)

        authorization.clean_cache(self.o.pink_id)

        return scopes

    def add_scopes(self, scopes):
        return self.modi_scopes(set(self.o.scopes) | scopes)

    def remove_scopes(self, scopes):
        return self.modi_scopes(set(self.o.scopes) - scopes)
