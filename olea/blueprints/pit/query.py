from flask import g

from models import Pit, Role
from olea.auth import check_opt_duck, check_scopes
from olea.base import single_query
from olea.errors import AccessDenied


class PitQuery():
    @staticmethod
    def single(id_):
        return single_query(model=Pit,
                            id_or_obj=id_,
                            condiction=lambda obj: obj.pink_id == g.pink_id)

    @classmethod
    def checks(cls, deps):
        if not check_scopes(deps):
            raise AccessDenied(cls_=Pit)

        pits = Pit.query.join(Role). \
            filter(Pit.status == Pit.S.auditing). \
            filter(Role.dep.in_(deps)).all()

        return pits

    @classmethod
    def in_dep(cls, dep, status):
        if not check_scopes(dep):
            raise AccessDenied(cls_=Pit)

        pits = Pit.query.join(Role). \
            filter(Role.dep == dep). \
            filter(Pit.status.in_(status)).all()

        return pits

    @classmethod
    def search(cls, deps, status_set, pink_id=''):
        if (not pink_id or pink_id != g.pink_id) and not check_opt_duck(scopes=deps):
            raise AccessDenied(cls_=Pit)

        query = Pit.query.join(Role)
        if deps:
            query = query.filter(Role.dep.in_(deps))
        if status_set:
            query = query.filter(Pit.status.in_(status_set))
        if pink_id:
            query = query.filter(Pit.pink_id == pink_id)

        return query.all()
