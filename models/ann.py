import enum

from sqlalchemy_ import BaseModel, Column, ForeignKey
from sqlalchemy_.types import ARRAY, Enum, JSONB, Boolean, DateTime, Integer, String, Text

from .common_enums import DEP

__all__ = ['Ann']


class Ann(BaseModel):
    __tablename__ = 'ann'

    # Level
    class L(enum.Enum):
        tips = 'tips'
        normal = 'normal'
        important = 'important'

    id = Column(String, primary_key=True)
    level = Column(Enum(L, name='ann_level'))
    deps = Column(ARRAY(DEP), index=True)
    poster_id = Column(String, ForeignKey('pink.id', ondelete='SET NULL'))
    expiration = Column(DateTime)
    deleted = Column(Boolean, default=False)

    ver = Column(Integer, default=0)
    content = Column(Text)
    at = Column(DateTime)

    history = Column(JSONB, default=dict)

    __id_len__ = 8

    def update(self, now, content):
        self.history[self.ver] = {
            'content': self.content,
            'at': self.at.timestamp(),
        }
        self.ver += 1
        self.at = now
        self.content = content
