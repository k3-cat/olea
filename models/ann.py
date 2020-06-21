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
    deps = Column(ARRAY(Enum(Dep)))
    poster = Column(String, ForeignKey('pink.id', ondelete='SET NULL'))
    exp = Column(DateTime)
    deleted = Column(Boolean, default=False)

    ver = Column(Integer, default=0)
    timestamp = Column(DateTime)
    content = Column(Text)

    history = Column(JSONB, default=dict)

    __id_len__ = 8

    def update(self, now, content):
        self.history[self.ver] = {
            'timestamp': self.timestamp.timestamp(),
            'content': self.content,
        }
        self.ver += 1
        self.timestamp = now
        self.content = content
