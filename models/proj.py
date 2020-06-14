import enum

from sqlalchemy_ import (BaseModel, Column, ForeignKey, UniqueConstraint, hybrid_property,
                         relationship)
from sqlalchemy_.types import ARRAY, JSONB, DateTime, Enum, Integer, String

__all__ = ['Proj']


class Proj(BaseModel):
    __tablename__ = 'proj'

    class State(enum.Enum):
        pre = 'pre-process'
        freezed = 'freezed'
        working = 'working'
        upload = 'pending upload'
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
    track = Column(ARRAY(String), default=list)
    timestamp = Column(DateTime)
    word_count = Column(Integer)
    url = Column(String)
    chat = Column(JSONB)

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

    class Trace(enum.Enum):
        re_open = 'r'
        freeze = 'F'
        upload = 'U'
        start = '+'
        finish = '-'

    def add_track(self, info: 'Pit.Trace', now, by=''):
        base = f'{info.name} - {now}'
        if info == Trace.re_open:
            self.track.append(f'{base} by:{by}')
        else:
            self.track.append(base)
