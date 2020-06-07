from typing import List

from models import Proj, Role
from olea.errors import RecordNotFound


def query_all_projs(europaea: bool = False) -> List[Proj]:
    if not europaea:
        return Proj.query.filter_by(finish_at=None).all()
    return Proj.query.all()


def query_role(id_: str) -> Role:
    role: Role = Role.get(id_)
    if not role:
        raise RecordNotFound(cls=Role, id_=id_)
    return role
