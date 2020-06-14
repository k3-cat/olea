from datetime import timedelta
from typing import List

from flask import current_app, g

from models import Dep, Pink, Pit, Proj, Role
from olea.base import BaseMgr, single_query
from olea.errors import (AccessDenied, DuplicatedRecord, NotQualifiedToPick, ProjMetaLocked,
                         RoleIsTaken)
from olea.exts import db

from .info_builder import build_info


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
            raise AccessDenied(cls=Proj)
        query = Proj.query.filter(Proj.state.in_(states if states else cls.PUBLIC_STATES))
        if types:
            query.filter(Proj.type.in_(types))
        return query.all()


class ProjMgr(BaseMgr):
    model = Proj

    gap = timedelta(days=1)
    au_due = current_app.config['AU_DUE']
    ps_due = current_app.config['PS_DUE']
    ae_due = current_app.config['AE_DUE']

    def __init__(self, obj_or_id):
        self.o: self.model = None
        super().__init__(obj_or_id)

    @classmethod
    def create(cls, base: str, type_, suff, leader_id):
        title, source, words_count = build_info(base=base, type_=type_)
        if proj := cls.query.filter_by(source=source, type=type_, suff=suff):
            if proj.state == Proj.State.freezed:
                proj.state = Proj.State.pre
                proj.leader_id = leader_id
                proj.add_track(info=Proj.Trace.re_open, now=g.now, by=g.pink_id)
            else:
                raise DuplicatedRecord(obj=proj)
        else:
            proj = cls.model(
                id=cls.gen_id(),
                title=title,
                source=source,
                suff=suff,
                words_count=words_count,
                leader_id=leader_id,
            )
        db.session.add(proj)
        return proj

    def start(self):
        if g.pink_id != self.o.leader_id:
            raise AccessDenied(obj=self.o)
        if self.o.state != Proj.State.pre:
            raise ProjMetaLocked(state=self.o.state)

        self.o.state = Proj.State.working
        self.o.add_track(info=Proj.Trace.start, now=g.now)

        pits:List[Pit] = Pit.query.join(Role) \
            .filter(Role.proj_id == self.o.id) \
            .filter(Pit.state==Pit.State.init) \
            .all()
        for pit in pits:
            pit.state = Pit.State.pending
            if pit.role.dep == Dep.au:
                pit.start_at = g.now + gap
                pit.due = pit.start_at + self.au_due
            elif pit.role.dep == Dep.ps:
                pit.start_at = g.now + gap
                pit.due = pit.start_at + self.ps_due
            elif pit.role.dep == Dep.ae:
                pit.start_at = g.now + gap + self.au_due
                pit.due = pit.start_at + self.ae_due
            else:
                # prevent unexpected role dep, should never be called
                Exception('Unexpected Role Dep')

    def modify_roles(self, add: dict, remove: list):
        if g.pink_id != self.o.leader_id:
            raise AccessDenied(obj=self.o)
        return self.force_modify_roles(add, remove)

    def force_modify_roles(self, add: dict, remove: list):
        if self.o.state != Proj.State.pre:
            raise ProjMetaLocked(state=self.o.state)

        # add first, to prevent conflicts
        for dep, roles in add.values():
            for name in roles:
                try:
                    RoleMgr.create(self.o, dep, name)
                except DuplicatedRecord:
                    pass
        RoleMgr.remove(remove)

        db.session.commit()
        return self.o.roles

    def finish(self, url):
        self.o.state = Proj.State.fin
        self.o.url = url
        self.o.add_track(info=Proj.Trace.finish, now=g.now)

    def freeze(self):
        self.o.state = Proj.State.freezed
        self.o.add_track(info=Proj.Trace.freeze, now=g.now)


class RoleMgr(BaseMgr):
    model = Role

    def __init__(self, obj_or_id):
        self.o: self.model = None
        super().__init__(obj_or_id)

    @classmethod
    def create(cls, proj: Proj, dep: Dep, name: str):
        if role := cls.query.filter_by(proj_id=proj.id, dep=dep, name=name):
            raise DuplicatedRecord(obj=role)
        role = cls.model(id=cls.gen_id(), proj=proj, dep=dep, name=name)
        db.session.add(role)
        return role

    @classmethod
    def remove(cls, ids):
        cls.query.filter(Role.id.in_(ids))

    def full_pick(self, pink_id):
        if self.o.taken:
            raise RoleIsTaken(by=self.o.pit)
        self.o.taken = True
        pit = PitMgr.create(self.o, pink_id)
        if pink_id != g.pink_id:
            pit.add_track(info=Pit.Trace.pick_f, now=g.now, by=g.pink_id)
        return pit

    def pick(self):
        pink = Pink.query.get(g.pink_id)
        if self.o.dep not in pink.deps:
            raise NotQualifiedToPick(dep=self.o.dep)
        return self.full_pick(pink.id)


class PitMgr(BaseMgr):
    model = Pit

    def __init__(self, obj_or_id):
        self.o: self.model = None
        super().__init__(obj_or_id)

    def __init__(self, obj_or_id, europaea=False):
        super().__init__(obj_or_id)
        if not europaea and self.o.pink_id != g.pink_id:
            raise AccessDenied(obj=self.o)

    @classmethod
    def create(cls, role, pink_id):
        pit = cls.model(id=cls.gen_id(), role=role, pink_id=pink_id, timestamp=g.now)
        db.session.add(pit)
        return pit
