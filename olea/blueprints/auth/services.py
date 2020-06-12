import datetime

from flask import current_app, g, request

from models import Duck, Lemon, Pink
from olea import email_mgr
from olea.auth import authorization
from olea.base import BaseMgr
from olea.errors import (AccountDeactivated, DuplicatedRecord, InvalidCredential,
                         InvalidRefreshToken, RecordNotFound)
from olea.exts import db, redis
from olea.utils import random_b85

from .ip import ip2city
from .pwd_tools import check_pwd, generate_pwd


class PinkMgr(BaseMgr):
    module = Pink

    @classmethod
    def forget_pwd(cls, name, email):
        pink = cls.query.filter_by(name=name).first()
        if pink and pink.email != email:
            return
        token = random_b85(k=20)
        redis.set(f'rst-{token}', pink.id, ex=cls.t_life)
        email_mgr.reset_pwd(email=pink.email, token=token)

    @staticmethod
    def reset_pwd(token, pwd):
        if not (pink_id := redis.get(f'rst-{token}')):
            raise InvalidCredential(type=InvalidCredential.T.rst)
        PinkMgr(pink_id).set_pwd(pwd)
        redis.delete(token)

    def set_pwd(self, pwd):
        check_pwd(pwd)
        self.o.pwd = pwd
        return True


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
    def grante(cls, name, pwd, device_id):
        pink: Pink = Pink.query.filter_by(name=name).first()
        if not pink.active:
            raise AccountDeactivated()
        if not pink or not pink.check_pwd(pwd):
            raise InvalidCredential(type=InvalidCredential.T.pwd)
        if lemon := pink.lemons.filter_by(device_id=device_id):
            db.session.delete(lemon)

        lemon = cls.model(id=cls.gen_id(),
                          key=random_b85(k=40),
                          pink=pink,
                          device_id=device_id,
                          ip=request.remote_addr,
                          exp=g.now + cls.r_life,
                          timestamp=g.now)

        db.session.add(lemon)
        db.session.commit()
        return lemon

    def grante_access_token(self, key, device_id):
        if self.o.key != key or self.o.device_id != device_id:
            raise InvalidRefreshToken(rsn=InvalidRefreshToken.Rsn.key)
        if self.o.ip != request.remote_addr \
            and ip2city(self.o.ip) != ip2city(request.remote_addr):
            raise InvalidRefreshToken(rsn=InvalidRefreshToken.Rsn.ip)
        if self.o.exp < g.now:
            self.revoke()
            raise InvalidRefreshToken(rsn=InvalidRefreshToken.Rsn.exp, at=self.o.exp)
        if (last := redis.hget('lass_access', g.pink_id)) and g.now.timestamp() - last > 86400:
            self.o.exp = g.now + self.r_life
            db.session.add(self.o)
        redis.hset('last_access', g.pink_id, g.now.timestamp())

        token = random_b85(k=20)
        redis.set(token, g.pink_id, ex=a_life.seconds)
        return token, g.now + self.a_life

    def revoke(self):
        db.session.delete(self.o)
        db.session.commit()

    @staticmethod
    def revoke_all():
        Pink.query.get(g.pink_id).lemons.delete()
        db.session.commit()


class DuckMgr(BaseMgr):
    modle = Duck

    @staticmethod
    def alter_ducks(pink_id, add, remove):
        ducks = list()
        conflicts = list()
        for node in add.keys():
            try:
                ducks.append(DuckMgr.grante(pink_id, node, add[node]))
            except DuplicatedRecord as e:
                conflicts.append(e.obj)
        if remove:
            DuckMgr.revoke(remove)
        authorization.clean_cache()
        return (ducks, conflicts)

    @classmethod
    def grante(cls, pink_id, node, scopes: set):
        if duck := Duck.query.filter_by(pink_id=pink_id, node=node):
            raise DuplicatedRecord(obj=duck)
        else:
            duck = cls.model(id=cls.gen_id(), pink_id=pink_id, node=node, scopes=list(scopes))
            db.session.add(duck)
        return duck

    @classmethod
    def revoke(cls, pink_id, nodes):
        cls.query.filter_by(pink_id=pink_id).filter(Duck.node.in_(nodes)).delete()

    def alter_scopes(self, scopes: set):
        self.o.scopes = list(scopes)
        db.session.add(self.o)
        authorization.clean_cache()
        return scopes

    def add_scopes(self, scopes):
        return self.alter_scopes(set(self.o.scopes) | scopes)

    def remove_scopes(self, scopes):
        return self.alter_scopes(set(self.o.scopes) - scopes)
