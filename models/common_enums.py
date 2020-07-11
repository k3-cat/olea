__all__ = ['Dep']

import enum

from sqlalchemy_.types import Enum


class ZEnum(enum.Enum):
    def __str__(self):
        return self.name


class Dep(ZEnum):
    _sp = '00'
    ld = '30'
    tr = '41'
    yt = '42'
    au = '50'
    ps = '60'
    ae = '70'


DEP = Enum(Dep, name='dep')
