import enum

from sqlalchemy_ import BaseModel, Column
from sqlalchemy_.types import ARRAY, DateTime, Enum, String, Text

from .common_enums import Dep

__all__ = ['Ann', 'AnnCategory']


class AnnCategory(enum.Enum):
    tips = 'tips'
    normal = 'normal'
    important = 'important'
    urgent = 'urgent'


class Ann(BaseModel):
    __tablename__ = 'ann'

    id = Column(String, primary_key=True)
    category = Column(Enum(AnnCategory))
    deps = Column(ARRAY(Enum(Dep)))
    expired_at = Column(DateTime)
    timestamp = Column(DateTime)
    info = Column(Text)
