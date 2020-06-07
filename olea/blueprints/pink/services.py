from flask import current_app

from models import Lemon, Pink
from olea.errors import AccessDenied
from olea.exts import db, mailgun, redis
from olea.utils import random_b85

from ..base_mgr import BaseMgr
from .pwd_tools import check_pwd, generate_pwd


class PinkMgr(BaseMgr):
    model = Pink

    t_life = current_app.config['RESET_PWD_TOKEN_LIFE'].seconds

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
        db.session.commit()

        mailgun.send(subject='初次见面, 这里是olea',
                     to=(pink.email, ),
                     template='new_pink',
                     values={
                         'name': pink.name,
                         'pwd': pwd
                     })
        return pink

    @classmethod
    def reset_pwd_init(cls, name, email):
        pink = cls.model.query().filter_by(name=name).first()
        if pink and pink.email != email:
            return
        token = random_b85(128 // 8)
        redis.set(token, pink.id, ex=cls.t_life)
        mailgun.send(subject='你的密码重置令牌',
                     to=(pink.email, ),
                     template='reset_pwd',
                     values={'token': token})

    @classmethod
    def reset_pwd_fin(cls, token, pwd):
        if not (pink_id := redis.get(token)):
            pass
        PinkMgr(pink_id).set_pwd(pwd)
        redis.delete(token)

    def set_pwd(self, pwd):
        check_pwd(pwd)
        self.o.pwd = pwd
        return True

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
