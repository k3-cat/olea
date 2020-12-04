__all__ = ['Chat']

from sqlalchemy_ import BaseModel, Column, ForeignKey, relationship
from sqlalchemy_.types import JSONB, Boolean, DateTime, Integer, String, Text


class Chat(BaseModel):
    __tablename__ = 'chat'

    id = Column(String, primary_key=True)
    order = Column(Integer)
    proj_id = Column(String, ForeignKey('proj.id', ondelete='CASCADE'))
    pink_id = Column(String, ForeignKey('pink.id', ondelete='SET NULL'))
    reply_to_id = Column(String, ForeignKey('chat.id', ondelete='CASCADE'), nullable=True)
    deleted = Column(Boolean, default=False)

    ver = Column(Integer, default=0)
    reply_to_ver = Column(Integer, nullable=True)
    content = Column(Text)
    at = Column(DateTime)

    history = Column(JSONB, default=dict)

    proj = relationship('Proj', back_populates='chats')
    reply_to = relationship('Chat', remote_side=[id], back_populates='replies')
    replies = relationship('Chat',
                           remote_side=[id],
                           order_by='Chat.order',
                           back_populates='reply_to',
                           lazy='dynamic')
    __id_len__ = 14

    def update(self, now, content):
        if self.ver > 0:
            self.history[self.ver] = {
                'reply_to_ver': self.reply_to_ver,
                'content': self.content,
                'at': self.at.timestamp(),
            }
        self.ver += 1
        if self.reply_to_id:
            self.reply_to_ver = self.reply_to.ver
        self.content = content
        self.at = now

    def set_order(self, proj_timestamp, now):
        self.order = (now.timestamp() - proj_timestamp.timestamp()) * 10

    def __json__(self):
        return {
            'id': self.id,
            'order': self.order,
            'deps': self.deps,
            'pink_id': self.pink_id,
            'reply_to_id': self.reply_to_id,
            'ver': self.ver,
            'content': self.content,
            'at': self.at
        }
