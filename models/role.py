from sqlalchemy_ import (BaseModel, Column, ForeignKey, UniqueConstraint, hybrid_property,
                         relationship)
from sqlalchemy_.types import Boolean, Enum, String, Text

from .common_enums import Dep
from .pit import Pit

__all__ = ['Role']


class Role(BaseModel):
    __tablename__ = 'role'

    id = Column(String, primary_key=True)
    proj_id = Column(String, ForeignKey('proj.id', ondelete='CASCADE'))
    dep = Column(Enum(Dep))
    name = Column(String)
    note = Column(Text)
    taken = Column(Boolean, default=False)

    proj = relationship('Proj', back_populates='roles')
    pits = relationship(
        'Pit',
        back_populates='role',
        cascade='all, delete-orphan',
        lazy='dynamic',
        passive_deletes=True,
    )
    __table_args__ = (UniqueConstraint('proj_id', 'dep', 'name', name='_role_uc'), )
    __id_len__ = 12

    @hybrid_property
    def pit(self):
        return self.pits.order_by(Pit.timestamp.desc()).first()

    def to_dict(self):
        return (self.id, self.dep.name, self.role)
