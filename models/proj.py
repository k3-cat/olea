import enum

from sqlalchemy_ import (BaseModel, Column, ForeignKey, UniqueConstraint, hybrid_property,
                         relationship)
from sqlalchemy_.types import JSONB, DateTime, Enum, Integer, String

__all__ = ['Proj', 'ProjState', 'ProjType']


class ProjState(enum.Enum):
    pre = 'pre-process'
    freezed = 'freezed'
    working = 'working'
    fin = 'finished'


class ProjType(enum.Enum):
    doc = 'documentary'
    sub = 'sub-content'
    ani = 'animation'


class Proj(BaseModel):
    __tablename__ = 'proj'

    id = Column(String, primary_key=True)
    title = Column(String, index=True)
    source = Column(String)
    type = Column(Enum(ProjType))
    suff = Column(String)
    state = Column(Enum(ProjState))
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


'''
    def to_dict(self, lv: int) -> Dict[str, Union[str, List[str]]]:
        result = {
            'id': self.id,
            'title': self.display_title,
            'type': self.type.name,
            'source': self.source,
        }
'''
