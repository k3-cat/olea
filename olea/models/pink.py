__all__ = ['Pink']

from passlib.hash import argon2
from sqlalchemy_ import BaseModel, Column, relationship
from sqlalchemy_.types import ARRAY, Boolean, String

from .common_enums import DEP

pwd_hasher = argon2.using(time_cost=50, memory_cost=1024 * 16, parallelism=2)


class Pink(BaseModel):
    __tablename__ = 'pink'

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    qq = Column(String, nullable=True)
    other = Column(String, nullable=True)
    deps = Column(ARRAY(DEP))
    _pwd = Column(String)
    active = Column(Boolean, default=True)

    pits = relationship('Pit', back_populates='pink', lazy='dynamic', passive_deletes=True)
    ducks = relationship('Duck', back_populates='pink', lazy='dynamic', passive_deletes=True)
    lemons = relationship('Lemon', back_populates='pink', lazy='dynamic', passive_deletes=True)
    __id_len__ = 9

    @property
    def pwd(self):
        raise AttributeError('SHOLD NOT READ PWD')

    @pwd.setter
    def pwd(self, new_pwd):
        self._pwd = pwd_hasher.hash(new_pwd)

    def check_pwd(self, pwd):
        return pwd_hasher.verify(self._pwd, pwd)

    def __json__(self):
        return {
            'id': self.id,
            'name': self.name,
            'qq': self.qq,
            'other': self.other,
            'deps': self.deps
        }
