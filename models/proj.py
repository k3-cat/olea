import enum

from sqlalchemy_ import (BaseModel, Column, ForeignKey, UniqueConstraint, hybrid_property,
                         relationship)
from sqlalchemy_.types import ARRAY, DateTime, Enum, Integer, String

__all__ = ['Proj']


class Proj(BaseModel):
    __tablename__ = 'proj'

    # State
    class S(enum.Enum):
        pre = 'pre-process'
        freezed = 'freezed'
        working = 'working'
        upload = 'pending upload'
        fin = 'finished'

    # Category
    class C(enum.Enum):
        doc = 'documentary'
        sub = 'sub-content'
        ani = 'animation'

    id = Column(String, primary_key=True)
    title = Column(String, index=True)
    source = Column(String)
    cat = Column(Enum(C))
    suff = Column(String)
    state = Column(Enum(S), default=S.pre)
    leader_id = Column(String, ForeignKey('pink.id', ondelete='SET NULL'))
    word_count = Column(Integer)
    url = Column(String, nullable=True)
    timestamp = Column(DateTime)

    track = Column(ARRAY(String), default=list)

    roles = relationship('Role', back_populates='proj', lazy='dynamic', passive_deletes=True)
    chats = relationship('Chat', back_populates='proj', lazy='dynamic', passive_deletes=True)
    __table_args__ = (UniqueConstraint('source', 'cat', 'suff', name='_proj_uc'), )
    __id_len__ = 11

    @hybrid_property
    def display_title(self):
        return f'{self.title}({self.suff})' if self.suff else self.title

    # Trace
    class T(enum.Enum):
        re_open = 'r'
        freeze = 'F'
        upload = 'U'
        start = '+'
        finish = '-'

    def add_track(self, info: 'Proj.T', now, by=''):
        base = f'{info.name} - {now}'
        if info == Proj.T.re_open:
            self.track.append(f'{base} by:{by}')
        else:
            self.track.append(base)
