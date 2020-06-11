from sqlalchemy_ import BaseModel, Column, hybrid_property, orm, relationship
from sqlalchemy_.types import ARRAY, JSONB, Boolean, Enum, String

from .common_enums import Dep

__all__ = ['Pink']


class Pink(BaseModel):
    __tablename__ = 'pink'

    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    qq = Column(String)
    line = Column(String)
    email = Column(String, unique=True)
    deps = Column(ARRAY(Enum(Dep)))
    pwd = Column(String)
    active = Column(Boolean, default=True)
    ability = Column(JSONB)
    metainfo = Column(JSONB)

    pits = relationship('Pit', back_populates='pink', lazy='dynamic', passive_deletes=True)
    ducks = relationship('Duck', back_populates='pink', lazy='dynamic', passive_deletes=True)
    lemons = relationship('Lemon', back_populates='pink', lazy='dynamic', passive_deletes=True)
    __id_len__ = 9
