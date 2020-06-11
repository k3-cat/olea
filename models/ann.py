import enum

from sqlalchemy_ import BaseModel, Column
from sqlalchemy_.types import ARRAY, DateTime, Enum, String, Text

from .common_enums import Dep

__all__ = ['Ann']


class Ann(BaseModel):
    __tablename__ = 'ann'

    class Category(enum.Enum):
        tips = 'tips'
        normal = 'normal'
        important = 'important'

    id = Column(String, primary_key=True)
    category = Column(Enum(Category))
    deps = Column(ARRAY(Enum(Dep)))
    expired_at = Column(DateTime)
    timestamp = Column(DateTime)
    info = Column(Text)
