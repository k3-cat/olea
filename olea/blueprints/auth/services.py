import datetime
import os
from base64 import b85encode

import IP2Location
from flask import current_app, g, request

from models import Lemon, Pink
from olea.errors import AccountDeactivated, InvalidCredential, InvalidRefreshToken, RecordNotFound
from olea.exts import db, redis

from ..base_mgr import BaseMgr
from .ip import ip2loc


class AuthMgr(BaseMgr):
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
            raise InvalidCredential()

        if pink.lemons.count() > 3:
            db.session.delete(pink.lemons.first())

        lemon = cls.model(id=cls.gen_id(),
                          key=b85encode(os.urandom(256 // 8)),
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

        token = b85encode(os.urandom(128 // 8))
        redis[token] = g.pink_id
        redis.pexpire(token, ex=a_life.seconds)
        return token, g.now + a_life

    def revoke(self):
        db.session.delete(self.o)
        db.session.commit()

    @staticmethod
    def revoke_all():
        Pink.query().get(g.pink_id).lemons.delete()
        db.session.commit()
