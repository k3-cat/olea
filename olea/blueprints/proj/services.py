from typing import List

from flask import g

from models import Dep, Pink, Pit, Proj, Role, Chat
from olea.base import BaseMgr
from olea.dep_graph import DepGraph
from olea.errors import (AccessDenied, DuplicatedRecord, NotQualifiedToPick, ProjMetaLocked,
                         RoleIsTaken, InvalidReply)
from olea.singleton import db

from .info_builder import build_info

dep_graph = DepGraph()


class ProjMgr(BaseMgr):
    model = Proj

    def __init__(self, obj_or_id):
        self.o: Proj = None
        super().__init__(obj_or_id)

    @classmethod
    def create(cls, base: str, type_, suff, leader_id):
        title, source, words_count = build_info(base=base, type_=type_)
        if proj := cls.model.query.filter_by(source=source, type=type_, suff=suff):
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

    def modify_roles(self, add: dict, remove: list):
        if g.pink_id != self.o.leader_id:
            raise AccessDenied(obj=self.o)
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

    def start(self):
        if g.pink_id != self.o.leader_id:
            raise AccessDenied(obj=self.o)
        if self.o.state != Proj.State.pre:
            raise ProjMetaLocked(state=self.o.state)

        self.o.state = Proj.State.working
        self.o.add_track(info=Proj.Trace.start, now=g.now)

        pits: List[Pit] = Pit.query.join(Role) \
            .filter(Role.proj_id == self.o.id) \
            .filter(Pit.state == Pit.State.init) \
            .all()
        for pit in pits:
            pit.start_at = dep_graph.get_start_time(base=g.now, dep=pit.role.dep)
            pit.due = pit.start_at + dep_graph.DURATION[pit.role.dep]
            pit.state = Pit.State.working if pit.start_at == g.now else Pit.State.pending

    def finish(self, url):
        self.o.state = Proj.State.fin
        self.o.url = url
        self.o.add_track(info=Proj.Trace.finish, now=g.now)

    def freeze(self):
        self.o.state = Proj.State.freezed
        self.o.add_track(info=Proj.Trace.freeze, now=g.now)

    def post_chat(self, reply_to_id, content):
        # TODO: permission check
        return ChatMgr.post(self, reply_to_id, content)


class RoleMgr(BaseMgr):
    model = Role

    def __init__(self, obj_or_id):
        self.o: Role = None
        super().__init__(obj_or_id)

    @classmethod
    def create(cls, proj: Proj, dep: Dep, name: str):
        if role := cls.model.query.filter_by(proj_id=proj.id, dep=dep, name=name):
            raise DuplicatedRecord(obj=role)
        role = cls.model(id=cls.gen_id(), proj=proj, dep=dep, name=name)
        db.session.add(role)
        return role

    @classmethod
    def remove(cls, ids):
        cls.model.query.filter(Role.id.in_(ids))

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

    def __init__(self, obj_or_id, europaea=False):
        self.o: Pit = None
        super().__init__(obj_or_id)
        if not europaea and self.o.pink_id != g.pink_id:
            raise AccessDenied(obj=self.o)

    @classmethod
    def create(cls, role, pink_id):
        pit = cls.model(id=cls.gen_id(), role=role, pink_id=pink_id, timestamp=g.now)
        db.session.add(pit)
        return pit


class ChatMgr(BaseMgr):
    module = Chat

    def __init__(self, obj_or_id):
        self.o: Chat = None
        super().__init__(obj_or_id)

    @classmethod
    def post(cls, proj: Proj, reply_to_id: str, content: str):
        chat = cls.model(id=cls.gen_id(),
                         proj_id=proj.id,
                         pink_id=g.pink_id,
                         content=content,
                         timestamp=g.now)

        index = proj.chat_index
        if reply_to_id:
            if reply_to_id not in index:
                raise InvalidReply()

            index = index[reply_to_id]
            chat.reply_to_id = reply_to_id

        index[chat.id] = dict()
        chat.set_order(proj_timestamp=proj.timestamp, now=g.now)

        return chat

    def edit(self, content):
        if self.o.pink_id != g.pink_id:
            raise AccessDenied(obj=self.o)

        self.o.update(now=g.now, content=content)

    def delete(self):
        self.o.delete = True

        if self.o.reply_to_id:
            index = self.o.proj.index[self.o.reply_to_id]
        else:
            index = self.o.proj.index
        index.pop(self.o.id)
