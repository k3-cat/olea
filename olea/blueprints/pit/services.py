import datetime

from flask import g

from models import Dep, Pit, Role
from olea.base import BaseMgr, single_query
from olea.errors import AccessDenied
from olea.exts import db, onerive

from .utils import check_state


class PitQuery():
    @staticmethod
    def single(id_):
        return single_query(model=Pit,
                            id_or_obj=id_,
                            condiction=lambda obj: obj.pink_id == g.pink_id)

    SEARCH_ALL = (Pit.State.working, Pit.State.auditing, Pit.State.delayed)
    SEARCH_ONE = (Pit.State.init, Pit.State.working, Pit.State.auditing, Pit.State.delayed,
                  Pit.State.droped, Pit.State.droped_f)
    ALL_DEP = {Dep.ae, Dep.au, Dep.ps}

    @classmethod
    def search(cls, deps, pink_id=''):
        deps = deps & cls.ALL_DEP if deps else cls.ALL_DEP
        if pink_id != g.pink_id and not g.chek_opt_duck(scope=deps):
            raise AccessDenied(cls=Pit)
        query = Pit.query.join(Role)
        if pink_id:
            query = query.filter(Pit.state.in_(cls.SEARCH_ONE)).filter(Pit.pink_id == g.pink_id)
        else:
            query = query.filter(Pit.state.in_(cls.SEARCH_ALL))
        pits = query.filter(Role.dep.in_(deps)).all()
        return pits


class PitMgr(BaseMgr):
    model = Pit

    ALLOWED_DEPS = {
        Dep.ps: {Dep.ae},
        Dep.au: {Dep.ae},
    }

    def checker_download(self):
        check_state(self.o.state, (Pit.State.auditing, ))
        self._download()

    def download(self):
        check_state(self.o.state, (Pit.State.fin, ))
        if self.o.pink_id != g.pink_id and not g.check_opt_duck(scopes={self.o.role.dep}):
            sub_query = db.session.query(Pit.role_id) \
                .filter_by(pink_id=g.pink_id) \
                .filter(Pit.state.in_((Pit.State.pending, Pit.State.working, Pit.State.auditing))) \
                .sub_query()
            roles = Role.query.filter(Role.id.in_(sub_query)).all()
            '''
            roles = Role.query.join(Pit) \
                .filter(Pit.pink_id == g.pink_id) \
                .filter(Pit.state.in_((Pit.State.pending, Pit.State.working, Pit.State.auditing))) \
                .filter(Role.proj_id == self.o.role.proj_id) \
                .all()
            '''
            if not self.ALLOWED_DEPS[self.o.role.dep] & {role.dep for role in roles}:
                raise AccessDenied(obj=self.o.mango)
        self._download()

    def _download(self):
        return onerive.share(self.o.mango.id)

    def check_pass(self):
        check_state(self.o.state, (Pit.State.auditing, ))
        self.o.state = Pit.State.fin
        self.o.add_track(info=Pit.Trace.check_pass, now=g.now, by=g.pink_id)

    def check_fail(self):
        check_state(self.o.state, (Pit.State.auditing, ))
        self.o.state = Pit.State.working
        self.o.add_track(info=Pit.Trace.check_fail, now=g.now, by=g.pink_id)
        if (self.o.due - g.now).days < 3:
            self.o.state = Pit.State.delayed
            self.o.due = g.now + datetime.timedelta(days=3)
            self.o.add_track(info=Pit.Trace.extend, now=g.now)
