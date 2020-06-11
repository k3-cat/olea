import enum

from sqlalchemy_ import (BaseModel, Column, ForeignKey, UniqueConstraint, hybrid_property,
                         relationship)
from sqlalchemy_.types import JSONB, DateTime, Enum, Integer, String

__all__ = ['Proj']


class Proj(BaseModel):
    __tablename__ = 'proj'

    class State(enum.Enum):
        pre = 'pre-process'
        freezed = 'freezed'
        working = 'working'
        fin = 'finished'

    class Type(enum.Enum):
        doc = 'documentary'
        sub = 'sub-content'
        ani = 'animation'

    id = Column(String, primary_key=True)
    title = Column(String, index=True)
    source = Column(String)
    type = Column(Enum(Type))
    suff = Column(String)
    state = Column(Enum(State))
    leader_id = Column(String, ForeignKey('pink.id'))
    chat = Column(JSONB)
    word_count = Column(Integer)
    timestamp = Column(DateTime)
    finished_at = Column(DateTime)
    url = Column(String)
    income = Column(Integer)

    progress = relationship(
        'Progress',
        uselist=False,
        back_populates='proj',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    roles = relationship(
        'Role',
        back_populates='proj',
        cascade='all, delete-orphan',
        lazy='dynamic',
        passive_deletes=True,
    )
    __table_args__ = (UniqueConstraint('source', 'type', 'suff', name='_proj_uc'), )
    __id_len__ = 11

    @hybrid_property
    def display_title(self):
        return f'{self.title}({self.suff})' if self.suff else self.title
