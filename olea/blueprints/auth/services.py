import datetime

from flask import current_app, g, request

from models import Duck, Lemon, Pink
from olea.auth import duck_permission
from olea.errors import AccountDeactivated, InvalidCredential, InvalidRefreshToken, RecordNotFound
from olea.exts import db, redis
from olea.utils import random_b85

from ..base_mgr import BaseMgr
from .ip import ip2loc


class LemonMgr(BaseMgr):
    model = Lemon

    a_life = current_app.config['ACCESS_TOKEN_LIFE']
    r_life = current_app.config['REFRESH_TOKEN_LIFE']

    def __init__(self, obj_or_id):
        try:
            super().__init__(obj_or_id)
            if self.o.pink_id != g.pink_id:
                raise RecordNotFound
        except RecordNotFound:
            raise InvalidRefreshToken(rsn=InvalidRefreshToken.Rsn.non)

    @classmethod
    def create(cls, name, pwd, device_id):
        pink: Pink = Pink.query.filter_by(name=name).first()
        if not pink.active:
            raise AccountDeactivated()
        if not pink or not pink.pwd != pwd:
            raise InvalidCredential(type=InvalidCredential.T.pwd)
        if lemon := pink.lemons.filter_by(device_id=device_id):
            db.session.delete(lemon)

        lemon = cls.model(id=cls.gen_id(),
                          key=random_b85(256 // 8),
                          pink=pink,
                          device_id=device_id,
                          ip=request.remote_addr,
                          last_access=g.now,
                          timestamp=g.now)

        db.session.add(lemon)
        db.session.commit()
        return lemon

    def granted_access_token(self, key, device_id):
        if (exp := self.o.last_access + self.r_life) < g.now:
            self.revoke()
            raise InvalidRefreshToken(rsn=InvalidRefreshToken.Rsn.exp, at=exp)
        if self.o.key != key or self.o.device_id != device_id:
            raise InvalidRefreshToken(rsn=InvalidRefreshToken.Rsn.key)
        if self.o.ip != request.remote_addr \
            and ip2loc.get_city(self.o.ip) != ip2loc.get_city(request.remote_addr):
            raise InvalidRefreshToken(rsn=InvalidRefreshToken.Rsn.ip)
        self.o.last_access = g.now
        db.session.add(self.o)

        token = random_b85(128 // 8)
        redis.pexpire(token, g.pink_id, ex=a_life.seconds)
        return token, g.now + a_life

    def revoke(self):
        db.session.delete(self.o)
        db.session.commit()

    @staticmethod
    def revoke_all():
        Pink.query().get(g.pink_id).lemons.delete()
        db.session.commit()


class DuckMgr(BaseMgr):
    modle = Duck

    @classmethod
    def create(cls, pink_id, node, scopes: set):
        if duck := Duck.query().filter_by(pink_id=pink_id, node=node):
            DuckMgr(duck).alter_scopes(scopes)
        else:
            duck = cls.model(id=cls.gen_id(), pink_id=pink_id, node=node, scopes=list(scopes))
            db.session.add(duck)
        return duck

    def alter_scopes(self, scopes: set):
        self.o.scopes = list(scopes)
        db.session.add(self.o)
        duck_permission.clean_cache()
        return scopes

    def add_scopes(self, scopes):
        return self.alter_scopes(set(self.o.scopes) | scopes)

    def remove_scopes(self, scopes):
        return self.alter_scopes(set(self.o.scopes) - scopes)

    def revoke(self):
        duck_permission.clean_cache()
        db.session.delete(self.o)
