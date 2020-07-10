from functools import partial

from sqlalchemy import Column as BaseColumn
from sqlalchemy import DateTime, String, Text
from sqlalchemy.ext.declarative import declarative_base

Column = partial(BaseColumn, nullable=False)
BaseModel = declarative_base()


class Log(BaseModel):
    __tablename__ = 'log'

    ref = Column(String, primary_key=True)
    timestamp = Column(DateTime)
    endpoint = Column(String)
    user = Column(String)

    level = Column(String)
    info = Column(String)
    request = Column(Text)
    response = Column(Text)
