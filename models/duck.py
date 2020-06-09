from sqlalchemy_ import BaseModel, Column, ForeignKey, UniqueConstraint, relationship
from sqlalchemy_.types import ARRAY, Boolean, String

__all__ = ['Duck']


class Duck(BaseModel):
    __tablename__ = 'duck'

    id = Column(String, primary_key=True)
    pink_id = Column(String, ForeignKey('pink.id', ondelete='CASADE'))
    node = Column(String)
    scope = Column(ARRAY(String))
    allow = Column(Boolean)

    pink = relationship('Pink', back_populates='lemons')
    __table_args__ = (UniqueConstraint('pink_id', 'node', name='_pit_uc'), )
    __id_len__ = 8
