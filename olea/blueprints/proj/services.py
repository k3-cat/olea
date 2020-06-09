from flask import g

from models import Dep, Proj, ProjState, Role
from olea.errors import AccessDenied, DuplicatedRecord, RolesLocked
from olea.exts import db

from ..base_mgr import BaseMgr
from .info_builder import build_info


class ProjMgr(BaseMgr):
    model = Proj

    @classmethod
    def create(cls, base: str, type_, suff, leader_id):
        title, source, words_count = build_info(base=base, type_=type_)
        if proj := cls.model.query().filter_by(source=source, type=type_, suff=suff):
            if proj.state == ProjState.freezed:
                proj.state = ProjState.pre
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
        if self.o.state != ProjState.pre:
            raise RolesLocked(state=self.o.state)

        # add first, to prevent conflicts
        for dep, roles in add.values():
            for name in roles:
                RoleMgr.create(self.o, dep, name)

        for role_id in remove:
            RoleMgr(role_id).remove()

        db.session.commit()
        return self.o.roles


class RoleMgr(BaseMgr):
    model = Role

    @classmethod
    def create(cls, proj: Proj, dep: Dep, name: str):
        role = cls.model(id=cls.gen_id(), proj=proj, dep=dep, name=name)
        db.session.add(role)
        return role

    def remove(self):
        db.session.delete(self.o)
        return True
