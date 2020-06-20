from passlib.hash import argon2
from sqlalchemy_ import BaseModel, Column, hybrid_property, orm, relationship
from sqlalchemy_.types import ARRAY, JSONB, Boolean, Enum, String

from .common_enums import Dep

__all__ = ['Pink']

pwd_hasher = argon2.using(time_cost=50, memory_cost=1024 * 16, parallelism=2)


class Pink(BaseModel):
    __tablename__ = 'pink'

    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    email = Column(String, unique=True)
    qq = Column(String)
    other = Column(String, nullable=True)
    deps = Column(ARRAY(Enum(Dep)))
    _pwd = Column(String)
    active = Column(Boolean, default=True)

    pits = relationship('Pit', back_populates='pink', lazy='dynamic', passive_deletes=True)
    ducks = relationship('Duck', back_populates='pink', lazy='dynamic', passive_deletes=True)
    lemons = relationship('Lemon', back_populates='pink', lazy='dynamic', passive_deletes=True)
    __id_len__ = 9

    @property
    def pwd(self):
        raise AttributeError('shold not read pwd')

    @pwd.setter
    def pwd(self, new_pwd):
        self._pwd = pwd_hasher.hash(new_pwd)

    def check_pwd(self, pwd):
        return pwd_hasher.verify(self._pwd, pwd)
