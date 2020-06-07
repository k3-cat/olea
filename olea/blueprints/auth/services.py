import datetime
import os
from base64 import b85encode

from flask import current_app, g, request

from models import Lemon, Pink
from olea.errors import AccountDeactivated, InvalidCredential, InvalidRefreshToken, RecordNotFound
from olea.exts import db, redis

from ..base_mgr import BaseMgr


class AuthMgr(BaseMgr):
    model = Lemon

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

    def granted_access_token(self, key):
        if (exp := self.o.last_access + datetime.timedelta(days=90)) < g.now:
            self.revoke()
            raise InvalidRefreshToken(rsn=InvalidRefreshToken.Rsn.exp, at=exp)
        if self.o.key != key:
            raise InvalidRefreshToken(rsn=InvalidRefreshToken.Rsn.key)
        token = b85encode(os.urandom(128 // 8))
        ex = current_app.config['ACCESS_TOKEN_EXP']
        redis[token] = g.pink_id
        redis.pexpire(token, ex=ex)
        return token, g.now + datetime.timedelta(seconds=ex)

    def revoke(self):
        db.session.delete(self.o)
        db.session.commit()

    @staticmethod
    def revoke_all():
        Pink.query().get(g.pink_id).lemons.delete()
        db.session.commit()
