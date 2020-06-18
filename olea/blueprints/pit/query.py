from flask import g

from models import Dep, Pit, Role
from olea.base import single_query
from olea.errors import AccessDenied


class PitQuery():
    @staticmethod
    def single(id_):
        return single_query(model=Pit,
                            id_or_obj=id_,
                            condiction=lambda obj: obj.pink_id == g.pink_id)

    SEARCH_ALL = {Pit.State.working, Pit.State.past_due, Pit.State.delayed, Pit.State.auditing}
    MY = {
        Pit.State.init, Pit.State.pending, Pit.State.working, Pit.State.past_due,
        Pit.State.auditing, Pit.State.delayed, Pit.State.droped
    }
    ALL_DEP = {Dep.ae, Dep.au, Dep.ps}

    @classmethod
    def check_list(cls, deps):
        deps = deps & cls.ALL_DEP if deps else cls.ALL_DEP
        if not g.check_scope(scope=deps):
            raise AccessDenied(cls_=Pit)

        pits = Pit.query.join(Role) \
            .filter(Pit.state == Pit.State.auditing) \
            .filter(Role.dep.in_(deps)).all()

        return pits

    @classmethod
    def my(cls, deps, states):
        deps = deps & cls.ALL_DEP if deps else cls.ALL_DEP

        pits = Pit.query.join(Role) \
            .filter(Pit.state.in_(states & cls.MY if states else cls.MY)) \
            .filter(Pit.pink_id == g.pink_id) \
            .filter(Role.dep.in_(deps)).all()

        return pits

    @classmethod
    def search_all(cls, deps, states, pink_id=''):
        deps = deps & cls.ALL_DEP if deps else cls.ALL_DEP

        if not g.check_scope(scope=deps):
            raise AccessDenied(cls_=Pit)

        query = Pit.query.join(Role) \
            .filter(Pit.state.in_(states & cls.SEARCH_ALL if states else cls.SEARCH_ALL))
        if pink_id:
            query = query.filter(Pit.pink_id == pink_id)
        pits = query.filter(Role.dep.in_(deps)).all()

        return pits
