import enum

from sqlalchemy_.types import Enum

__all__ = ['Dep']


class ZEnum(enum.Enum):
    def __str__(self):
        return self.name


class Dep(ZEnum):
    ld = '30'
    tr = '41'
    yt = '42'
    au = '50'
    ps = '60'
    ae = '70'


DEP = Enum(Dep, name='dep')
