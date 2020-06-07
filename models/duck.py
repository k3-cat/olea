from sqlalchemy_ import BaseModel, Column, ForeignKey
from sqlalchemy_.types import String

__all__ = ['Duck']


class Duck(BaseModel):
    __tablename__ = 'duck'

    key = Column(String, primary_key=True)
    pink_id = Column(String, ForeignKey('pink.id', ondelete='CASADE'))
    node = Column(String)
    scope = Column(String)
