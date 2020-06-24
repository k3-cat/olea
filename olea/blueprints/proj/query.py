from flask import g

from models import Proj
from olea.base import single_query
from olea.errors import AccessDenied


class ProjQuery():
    PUBLIC_STATUS = {Proj.S.working, Proj.S.pre, Proj.S.upload}

    @classmethod
    def single(cls, id_):
        proj = single_query(model=Proj,
                            id_or_obj=id_,
                            condiction=lambda obj: obj.status in cls.PUBLIC_STATUS)
        return proj

    @classmethod
    def search(cls, status_set=None, cats=None):
        if status_set - cls.PUBLIC_STATE and not g.check_opt_perm:
            raise AccessDenied(cls_=Proj)
        query = Proj.query.filter(Proj.status.in_(status_set))
        if cats:
            query.filter(Proj.cat.in_(cats))
        return query.all()
