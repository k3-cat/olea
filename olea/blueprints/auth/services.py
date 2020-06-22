from functools import wraps

from flask import current_app, g, request

from models import Lemon, Pink
from olea import email_mgr
from olea.auth.authentication import revoke_all_lemons
from olea.base import BaseMgr
from olea.errors import AccountDeactivated, InvalidCredential, InvalidRefreshToken, RecordNotFound
from olea.singleton import db, ip2loc, redis, pat
from olea.utils import random_b85

from .pwd_tools import check_pwd


def _verify_email():
    ve_life = current_app.config['EMAIL_VERIFICATION_LIFE']

    def verify_email(email):
        token = pat.encode(exp=(g.now + ve_life).timestamp(),
                           payload={
                               'old': Pink.query.get(g.pink_id) if g.pink_id else None,
                               'new': email
                           })

    return wraps(verify_email)


verify_email = _verify_email()


class PinkMgr(BaseMgr):
    module = Pink

    t_life = current_app.config['PWD_RESET_TOKEN_LIFE'].seconds

    def __init__(self, obj_or_id):
        self.o: Pink = None
        super().__init__(obj_or_id)

    @classmethod
    def forget_pwd(cls, name, email):
        pink = cls.model.query.filter_by(name=name).one()
        if pink and pink.email != email:
            return
        token = random_b85(k=20)
        redis.set(f'rst-{token}', pink.id, ex=cls.t_life)
        email_mgr.pwd_reset(email=pink.email, name=pink.name, token=token)

    @staticmethod
    def reset_pwd(token, pwd):
        if not (pink_id := redis.get(f'rst-{token}')):
            raise InvalidCredential(type=InvalidCredential.T.rst)

        PinkMgr(pink_id).set_pwd(pwd)
        revoke_all_lemons(pink_or_id=pink_id)

        redis.delete(token)

    def set_pwd(self, pwd):
        check_pwd(pwd)
        self.o.pwd = pwd

    def all_lemons(self):
        return self.o.lemons


class LemonMgr(BaseMgr):
    model = Lemon

    a_life = current_app.config['ACCESS_TOKEN_LIFE']
    r_life = current_app.config['REFRESH_TOKEN_LIFE']

    def __init__(self, obj_or_id):
        self.o: Lemon = None
        try:
            super().__init__(obj_or_id)
            if self.o.pink_id != g.pink_id:
                raise RecordNotFound
        except RecordNotFound:
            raise InvalidRefreshToken(rsn=InvalidRefreshToken.Rsn.non)

    @classmethod
    def grante(cls, name, pwd, device_id):
        pink: Pink = Pink.query.filter_by(name=name).one()
        if not pink.active:
            raise AccountDeactivated()
        if not pink or not pink.check_pwd(pwd):
            raise InvalidCredential(type=InvalidCredential.T.pwd)

        pink.lemons.filter_by(device_id=device_id).delete()

        lemon = cls.model(id=cls.gen_id(),
                          key=random_b85(k=40),
                          pink=pink,
                          device_id=device_id,
                          ip=request.remote_addr,
                          exp=g.now + cls.r_life,
                          timestamp=g.now)
        db.session.add(lemon)

        return lemon

    def grante_access_token(self, key, device_id):
        if self.o.key != key or self.o.device_id != device_id:
            raise InvalidRefreshToken(rsn=InvalidRefreshToken.Rsn.key)
        if self.o.ip != request.remote_addr \
            and ip2loc.get_city(self.o.ip) != ip2loc.get_city(request.remote_addr):
            raise InvalidRefreshToken(rsn=InvalidRefreshToken.Rsn.ip)
        if self.o.exp < g.now:
            self.revoke()
            raise InvalidRefreshToken(rsn=InvalidRefreshToken.Rsn.exp, at=self.o.exp)

        last = redis.hget('lass_access', g.pink_id)
        if last and g.now.timestamp() - last > 86400:
            self.o.exp = g.now + self.r_life

        token = random_b85(k=20)
        with redis.pipeline(transaction=False) as p:
            p.hset('last_access', g.pink_id, g.now.timestamp())
            p.set(token, g.pink_id, ex=a_life.seconds)
            p.execute()

        return token, g.now + self.a_life

    def revoke(self):
        db.session.delete(self.o)

    def revoke_all(self):
        revoke_all_lemons(pink_or_id=g.pink_id)
