from models import Lemon, Pink
from olea.errors import AccessDenied
from olea.exts import db, mailgun

from ..base_mgr import BaseMgr
from .pwd_tools import check_pwd, generate_pwd


def _welcom_message(pink, pwd):
    mailgun.send(
        subject='初次见面, 这里是olea',
        to=(pink.email, ),
        template='new_pink',
        values={
            'name': pink.name,
            'pwd': pwd
        },
    )


class PinkMgr(BaseMgr):
    model = Pink

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
        _welcom_message(pwd=pwd)
        return pink

    def reset_pwd(self, pwd):
        self.o.pwd = pwd
        return True

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
