from flask import current_app

from models import Lemon, Pink
from olea import email_mgr
from olea.base import BaseMgr, single_query
from olea.errors import AccessDenied, InvalidCredential
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
