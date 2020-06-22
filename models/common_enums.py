import enum
from sqlalchemy_.types import Enum

__all__ = ['Dep']


class Dep(enum.IntEnum):
    ld = 30
    tr = 41
    yt = 42
    au = 50
    ps = 60
    ae = 70


DEP = Enum(Dep, name='dep')
