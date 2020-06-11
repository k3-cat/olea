from flask import g

from models import Dep, Proj, Role
from olea.base import BaseMgr, single_query
from olea.errors import AccessDenied, DuplicatedRecord, RolesLocked
from olea.exts import db

from .info_builder import build_info


class ProjQuery():
    PUBLIC_STATES = {Proj.State.working, Proj.State.pre}

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

    @classmethod
    def create(cls, base: str, type_, suff, leader_id):
        title, source, words_count = build_info(base=base, type_=type_)
        if proj := cls.query.filter_by(source=source, type=type_, suff=suff):
            if proj.state == Proj.State.freezed:
                proj.state = Proj.State.pre
                proj.leader_id = leader_id
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

    def modify_roles(self, add: dict, remove: list):
        if g.pink_id != self.o.leader_id:
            raise AccessDenied(obj=self.o)
        return self.force_modify_roles(add, remove)

    def force_modify_roles(self, add: dict, remove: list):
        if self.o.state != Proj.State.pre:
            raise RolesLocked(state=self.o.state)

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


class RoleMgr(BaseMgr):
    model = Role

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
