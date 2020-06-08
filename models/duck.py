from sqlalchemy_ import BaseModel, Column, ForeignKey, UniqueConstraint
from sqlalchemy_.types import ARRAY, String

__all__ = ['Duck']


class Duck(BaseModel):
    __tablename__ = 'duck'

    id = Column(String, primary_key=True)
    pink_id = Column(String, ForeignKey('pink.id', ondelete='CASADE'))
    node = Column(String)
    scope = Column(ARRAY(String))

    __table_args__ = (UniqueConstraint('pink_id', 'node', name='_pit_uc'), )
    __id_len__ = 8
