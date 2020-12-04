__all__ = ['Dep']

from enum_tools import ZEnum
from sqlalchemy_.types import Enum


class Dep(ZEnum):
    _sp = '00'
    ld = '30'
    tr = '41'
    yt = '42'
    au = '50'
    ps = '60'
    ae = '70'


DEP = Enum(Dep, name='dep')
