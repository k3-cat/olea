from flask import g

from models import Proj
from olea.base import single_query
from olea.errors import AccessDenied


class ProjQuery():
    PUBLIC_STATES = {Proj.State.working, Proj.State.pre, Proj.State.upload}

    @classmethod
    def single(cls, id_):
        proj = single_query(model=Proj,
                            id_or_obj=id_,
                            condiction=lambda obj: obj.state in cls.PUBLIC_STATES)
        return proj

    @classmethod
    def search(cls, states=None, types=None):
        if states - cls.PUBLIC_STATE and not g.check_opt_perm:
            raise AccessDenied(cls_=Proj)
        query = Proj.query.filter(Proj.state.in_(states if states else cls.PUBLIC_STATES))
        if types:
            query.filter(Proj.type.in_(types))
        return query.all()
