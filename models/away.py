from sqlalchemy_ import BaseModel, Column, ForeignKey
from sqlalchemy_.types import Date, DateTime, String, Text

__all__ = ['Away']


class Away(BaseModel):
    __tablename__ = 'away'

    id = Column(String, primary_key=True)
    pink_id = Column(String, ForeignKey('pink.id'))
    reason = Column(Text)
    begin = Column(Date)
    end = Column(Date)
    timestamp = Column(DateTime)
