from sqlalchemy_ import BaseModel, Column, ForeignKey, UniqueConstraint, relationship
from sqlalchemy_.types import ARRAY, Boolean, String

__all__ = ['Duck']


class Duck(BaseModel):
    __tablename__ = 'duck'

    pink_id = Column(String, ForeignKey('pink.id', ondelete='CASADE'), primary_key=True)
    node = Column(String, primary_key=True)
    scopes = Column(ARRAY(String))
    allow = Column(Boolean)

    pink = relationship('Pink', back_populates='lemons')
