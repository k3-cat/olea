import datetime

from flask import g

from models import Dep, Pit, PitState, Role
from olea.errors import AccessDenied
from olea.exts import onerive

from ..base_mgr import BaseMgr
from .utils import check_state

_ALLOWED_DEPS = {
    Dep.ps: {Dep.ae},
    Dep.au: {Dep.ae},
}


class PitMgr(BaseMgr):
    model = Pit

    def checker_download(self):
        check_state(self.o.state, (PitState.auditing, ))
        self.force_download()

    def download(self):
        check_state(self.o.state, (PitState.fin, ))
        roles = Role.query.join(Pit) \
            .filter(Pit.pink_id == g.pink_id) \
            .filter(Role.proj_id == Pit.role.proj_id) \
            .filter(Pit.state.in_((PitState.pending, PitState.working, PitState.auditing))).all()
        if self._ALLOWED_DEPS[self.o.role.dep] & {role.dep for role in roles}:
            raise AccessDenied(obj=self.o.mango)
        self.force_download()

    def force_download(self):
        return onerive.share(self.o.mango.id)

    def check_pass(self):
        check_state(self.o.state, (PitState.auditing, ))
        self.o.state = PitState.fin
        self.o.add_track(info=Pit.Trace.check_pass, now=g.now, by=g.pink_id)

    def check_fail(self):
        check_state(self.o.state, (PitState.auditing, ))
        self.o.state = PitState.working
        self.o.add_track(info=Pit.Trace.check_fail, now=g.now, by=g.pink_id)
        if (self.o.due - g.now).days < 3:
            self.o.state = PitState.delayed
            self.o.due = g.now + datetime.timedelta(days=3)
            self.o.add_track(info=Pit.Trace.extend, now=g.now)
