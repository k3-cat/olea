from models import Duck, Pink
from core.auth import authentication, authorization, check_scopes
from core.base import BaseMgr
from core.errors import InvalidCredential, RecordNotFound
from core.singleton import db, pat, redis, sendgrid
from core.utils import FromConf, random_b85


class PinkMgr(BaseMgr):
    model = Pink

    t_life = FromConf.load('TL_NEW_PINK')

    @classmethod
    def assign_token(cls, deps, amount):
        check_scopes(deps)

        deps_s = ','.join(deps)
        tokens = [random_b85(k=20) for __ in range(amount)]
        redis.mset({f'deps-{token}': deps_s for token in tokens}, ex=cls.t_life.seconds)

        return tokens

    @classmethod
    def sign_up(cls, name: str, pwd, qq: int, other: str, email_token: str, deps_token: str):
        if not (deps_s := redis.get(f'deps-{deps_token}')):
            raise InvalidCredential(type_=InvalidCredential.T.new)

        pink = cls.model(id=cls.gen_id(), name=name, email=None, qq=str(qq), other=other)
        pink.pwd = pwd
        pink.deps = deps_s.split(',')
        PinkMgr(pink).set_email(email_token)
        db.session.add(pink)

        sendgrid.send(to=pink.email, template_name='new pink', name=pink.name)

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

    def deactivate(self):
        self.o.active = False

        authentication.revoke_all_lemons(self.o)

    def alter_ducks(self, add, remove):
        conflicts = self.o.ducks.filter(Duck.node.in_(add.keys())).all()

        for node in add.keys() - {conflict.node for conflict in conflicts}:
            info = add[node]
            DuckMgr.grant(pink_id=self.o.id,
                          node=node,
                          allow=info['allow'],
                          scopes=list(info['scopes']))

        if remove:
            self.o.ducks.filter(Duck.node.in_(remove)).delete()

        authorization.DuckCache.clean(pink_id=self.o.id)

        return (self.o.ducks.all(), conflicts)


class DuckMgr(BaseMgr):
    model = Duck

    def __init__(self, pink_id, node):
        if not (obj := self.model.query.get((pink_id, node))):
            raise RecordNotFound(cls_=self.model, id_=(','.join((pink_id, node))))
        self.o = obj

    @classmethod
    def grant(cls, pink_id, node, allow, scopes):
        duck = cls.model(pink_id=pink_id, node=node, allow=allow, scopes=scopes)
        db.session.add(duck)

        return duck

    def modi_scopes(self, scopes: set):
        self.o.scopes = list(scopes)

        authorization.DuckCache.clean(self.o.pink_id)

        return scopes

    def add_scopes(self, scopes):
        return self.modi_scopes(set(self.o.scopes) | scopes)

    def remove_scopes(self, scopes):
        return self.modi_scopes(set(self.o.scopes) - scopes)
