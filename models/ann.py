from sqlalchemy_ import BaseModel, Column, ForeignKey
from sqlalchemy_.types import ARRAY, JSONB, Boolean, DateTime, Enum, Integer, String, Text

from .common_enums import DEP, ZEnum

__all__ = ['Ann']


class Ann(BaseModel):
    __tablename__ = 'ann'

    # Level
    class L(ZEnum):
        tips = 'tips'
        normal = 'normal'
        important = 'important'

        def __str__(self):
            return self.name

    id = Column(String, primary_key=True)
    level = Column(Enum(L, name='ann_level'))
    deps = Column(ARRAY(DEP), index=True)
    poster_id = Column(String, ForeignKey('pink.id', ondelete='SET NULL'))
    expiration = Column(DateTime)
    deleted = Column(Boolean, default=False)

    ver = Column(Integer, default=1)
    content = Column(Text)
    at = Column(DateTime)

    history = Column(JSONB, default=dict)
    readers = Column(JSONB, default=dict)

    __id_len__ = 8

    def read(self, by, now):
        try:
            trace = self.readers[by]
        except KeyError:
            trace = list()
            self.readers[by] = trace

        if len(trace) == self.ver:
            return
        if skiped := self.ver - len(trace) > 1:
            trace.extend([0] * skiped - 1)
        trace.append(now.timestamp())

    def update(self, content, now):
        self.history[self.ver] = {
            'content': self.content,
            'at': self.at.timestamp(),
        }
        self.ver += 1
        self.at = now
        self.content = content

    def __json__(self):
        return {
            'id': self.id,
            'level': self.level,
            'deps': self.deps,
            'poster_id': self.poster_id,
            'exp': self.expiration,
            'ver': self.ver,
            'content': self.content,
            'at': self.at
        }
