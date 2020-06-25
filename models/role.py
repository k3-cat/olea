from sqlalchemy_ import (BaseModel, Column, ForeignKey, UniqueConstraint, hybrid_property,
                         relationship)
from sqlalchemy_.types import Enum, Boolean, String, Text

from .common_enums import DEP
from .pit import Pit

__all__ = ['Role']


class Role(BaseModel):
    __tablename__ = 'role'

    id = Column(String, primary_key=True)
    proj_id = Column(String, ForeignKey('proj.id', ondelete='CASCADE'))
    dep = Column(DEP, index=True)
    name = Column(String, unique=True)
    note = Column(Text, nullable=True)
    taken = Column(Boolean, default=False)

    proj = relationship('Proj', back_populates='roles')
    pits = relationship('Pit', back_populates='role', lazy='dynamic', passive_deletes=True)
    __table_args__ = (UniqueConstraint('proj_id', 'dep', 'name', name='_role_uc'), )
    __id_len__ = 12

    def __json__(self):
        return {
            'id': self.id,
            'dep': self.dep,
            'name': self.name,
            'note': self.note,
        }
