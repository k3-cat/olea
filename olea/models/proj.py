__all__ = ['Proj']

from enum_tools import ZEnum
from sqlalchemy_ import (BaseModel, Column, ForeignKey, UniqueConstraint, hybrid_property,
                         relationship)
from sqlalchemy_.types import ARRAY, DateTime, Enum, Integer, String


class Proj(BaseModel):
    __tablename__ = 'proj'

    # Status
    class S(ZEnum):
        pre = 'p'
        freezed = 'FF'
        working = 'w'
        upload = 'u'
        fin = 'F'

    # Category
    class C(ZEnum):
        doc = 'documentary'
        sub = 'sub-content'
        ani = 'animation'

    id = Column(String, primary_key=True)
    title = Column(String, index=True)
    source = Column(String)
    cat = Column(Enum(C, name='proj_cat'))
    suff = Column(String)
    status = Column(Enum(S, name='proj_status'), default=S.pre)
    leader_id = Column(String, ForeignKey('pink.id', ondelete='SET NULL'))
    word_count = Column(Integer)
    start_at = Column(DateTime, nullable=True)
    finish_at = Column(DateTime, nullable=True)
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
    class T(ZEnum):
        re_open = 'r'
        freeze = 'F'
        upload = 'U'
        start = 's'

    def add_track(self, info: 'Proj.T', now, by=''):
        base = f'{info.value} - {now}'
        if info == Proj.T.re_open:
            self.track.append(f'{base} by:{by}')
        else:
            self.track.append(base)

    def __json__(self):
        return {
            'id': self.id,
            'title': self.display_title,
            'source': self.source,
            'cat': self.cat,
            'status': self.status,
            'leader_id': self.leader_id,
            'word_count': self.word_count,
            'start_at': self.start_at
        }
