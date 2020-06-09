from passlib.context import LazyCryptContext
from sqlalchemy_ import BaseModel, Column, hybrid_property, orm, relationship
from sqlalchemy_.types import ARRAY, JSONB, Boolean, Enum, String

from .common_enums import Dep

__all__ = ['Pink']


class Pwd:
    CONTEXT = LazyCryptContext(
        schemes=['argon2'],
        argon2__time_cost=2,
        argon2__memory_cost=256 * 1024,
        argon2__parallelism=4,
    )

    def __init__(self, _pwd):
        self.p = _pwd

    def __eq__(self, pwd):
        return Pwd.CONTEXT.verify(pwd, self.p)

    def set(self, pwd):
        self.p = Pwd.CONTEXT.hash(pwd)

    def __str__(self):
        return self.p


class Pink(BaseModel):
    __tablename__ = 'pink'

    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    qq = Column(String)
    line = Column(String)
    email = Column(String, unique=True)
    deps = Column(ARRAY(Enum(Dep)))
    _pwd = Column(String)
    active = Column(Boolean, default=True)
    ability = Column(JSONB)
    metainfo = Column(JSONB)

    pits = relationship('Pit', back_populates='pink', lazy='dynamic', passive_deletes=True)
    ducks = relationship('Duck', back_populates='pink', lazy='dynamic', passive_deletes=True)
    lemons = relationship('Lemon', back_populates='pink', lazy='dynamic', passive_deletes=True)
    __id_len__ = 9

    @hybrid_property
    def pwd(self):
        return None

    @orm.reconstructor
    def init_on_load(self):
        self.pwd = Pwd(self._pwd)

    @pwd.setter
    def pwd(self, new_pwd):
        self.pwd.set(new_pwd)
        self._pwd = str(self.pwd)


'''
    def to_dict(self, lv: int):
        result = {
            'id': self.id,
            'name': self.name,
            'qq': self.qq,
            'line': self.line,
            'deps': [dep.name for dep in self.deps],
        }
        if lv >= 1:
            result['cc'] = self.cc
            result['pits'] = [
                pit.to_dict() for pit in PitMgr.get_effective_pit(self.pits)
            ]
        if lv >= 2:
            result['email'] = self.email
        return result
'''
