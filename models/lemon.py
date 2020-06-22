from sqlalchemy_ import BaseModel, Column, ForeignKey, UniqueConstraint, relationship
from sqlalchemy_.types import UUID, DateTime, String

__all__ = ['Lemon']


class Lemon(BaseModel):
    __tablename__ = 'lemon'

    id = Column(String, primary_key=True)
    key = Column(String)
    pink_id = Column(String, ForeignKey('pink.id', ondelete='CASCADE'))
    ip = Column(String)
    device_id = Column(UUID)
    expiration = Column(DateTime)
    timestamp = Column(DateTime)

    pink = relationship('Pink', back_populates='lemons')
    __table_args__ = (UniqueConstraint('pink_id', 'device_id', name='_lemon_uc'), )
    __id_len__ = 10
