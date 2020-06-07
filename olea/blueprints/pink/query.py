from typing import List

from models import Pink
from olea.errors import AccessDenied, RecordNotFound


def query_pink(id_: str, europaea: bool = False) -> Pink:
    pink: Pink = Pink.query.get(id_)
    if not pink:
        raise RecordNotFound(cls=Pink, id=id_)
    if not pink.active and not europaea:
        raise AccessDenied(obj=pink)
    return pink


def query_all_pinks(europaea: bool = False) -> List[Pink]:
    if not europaea:
        return Pink.query.filter_by(active=True).all()
    return Pink.query.all()
