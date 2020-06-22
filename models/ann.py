import enum

from sqlalchemy_ import BaseModel, Column, ForeignKey
from sqlalchemy_.types import ARRAY, JSONB, Boolean, DateTime, Enum, Integer, String, Text

from .common_enums import Dep

__all__ = ['Ann']


class Ann(BaseModel):
    __tablename__ = 'ann'

    # Level
    class L(enum.Enum):
        tips = 'tips'
        normal = 'normal'
        important = 'important'

    id = Column(String, primary_key=True)
    level = Column(Enum(L))
    deps = Column(ARRAY(Enum(Dep)), index=True)
    poster = Column(String, ForeignKey('pink.id', ondelete='SET NULL'))
    exp = Column(DateTime)
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
