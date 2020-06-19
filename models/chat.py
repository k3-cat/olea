from sqlalchemy_ import BaseModel, Column, ForeignKey, relationship
from sqlalchemy_.types import ARRAY, JSONB, Boolean, DateTime, Enum, Integer, String, Text

__all__ = ['Chat']


class Chat(BaseModel):
    __tablename__ = 'chat'

    id = Column(String, primary_key=True)
    order = Column(Integer, unique=True)
    proj_id = Column(String, ForeignKey('proj.id', ondelete='CASCADE'))
    pink_id = Column(String, ForeignKey('pink.id', ondelete='SET NULL'))
    reply_to_id = Column(String, ForeignKey('chat.id', ondelete='CASCADE'))

    ver = Column(Integer, default=0)
    content = Column(Text)
    timestamp = Column(DateTime)

    history = Column(JSONB, default=dict)

    deleted = Column(Boolean, default=False)

    proj = relationship('Proj', back_populates='chats')
    reply_to = relationship('Chat', remote_side=[id], back_populates='replys')
    replys = relationship('Chat',
                          remote_side=[id],
                          order_by='Chat.order',
                          back_populates='reply_to',
                          lazy='dynamic')
    __id_len__ = 14

    def update(self, now, content):
        self.history[self.ver] = {
            'timestamp': self.timestamp.timestamp(),
            'content': self.content,
        }
        self.ver += 1
        self.timestamp = now
        self.content = content

    def set_order(self, proj_timestamp, now):
        self.order = (now.timestamp() - proj_timestamp.timestamp()) * 10
