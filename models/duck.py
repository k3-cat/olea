from sqlalchemy_ import BaseModel, Column, ForeignKey, UniqueConstraint, relationship
from sqlalchemy_.types import ARRAY, Boolean, String

__all__ = ['Duck']


class Duck(BaseModel):
    __tablename__ = 'duck'

    pink_id = Column(String, ForeignKey('pink.id', ondelete='CASCADE'), primary_key=True)
    node = Column(String, primary_key=True)
    allow = Column(Boolean)
    scopes = Column(ARRAY(String))

    pink = relationship('Pink', back_populates='lemons')
    __table_args__ = (UniqueConstraint('pink_id', 'node', name='_duck_uc'), )
