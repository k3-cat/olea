import json
from typing import List
from collections import deque

from flask import g

from models import Chat, Dep, Pink, Pit, Proj, Role
from olea.base import BaseMgr
from olea.dep_graph import DepGraph
from olea.errors import (AccessDenied, DuplicatedRecord, InvalidReply, NotQualifiedToPick,
                         ProjMetaLocked, RoleIsTaken)
from olea.singleton import db, redis

from .info_builder import build_info

dep_graph = DepGraph()


class ProjMgr(BaseMgr):
    model = Proj

    def __init__(self, obj_or_id):
        self.o: Proj = None
        super().__init__(obj_or_id)

    @classmethod
    def create(cls, base: str, cat, suff, leader_id):
        title, source, words_count = build_info(base=base, cat=cat)
        if proj := cls.model.query.filter_by(source=source, cat=cat, suff=suff):
            if proj.state == Proj.S.freezed:
                proj.state = Proj.S.pre
                proj.leader_id = leader_id
                proj.add_track(info=Proj.T.re_open, now=g.now, by=g.pink_id)

            else:
                raise DuplicatedRecord(obj=proj)

        else:
            proj = cls.model(
                id=cls.gen_id(),
                title=title,
                source=source,
                cat=cat,
                suff=suff,
                words_count=words_count,
                leader_id=leader_id,
            )
        db.session.add(proj)

        return proj

    def modify_roles(self, add: dict, remove: list):
        if g.pink_id != self.o.leader_id:
            raise AccessDenied(obj=self.o)
        if self.o.state != Proj.S.pre:
            raise ProjMetaLocked(state=self.o.state)

        # add first, to prevent conflicts
        fails = dict()
        for dep, roles in add.items():
            exists = Role.query.filter_by(dep=dep).filter(Role.name.in_(roles)).all()
            fails[dep] = [role.name for role in exists]
            for name in roles - set(fails[dep]):
                RoleMgr.create(self.o, dep, name)

        if remove:
            RoleMgr.remove(remove)

        return (self.o.roles, fails)

    def start(self):
        if g.pink_id != self.o.leader_id:
            raise AccessDenied(obj=self.o)
        if self.o.state != Proj.S.pre:
            raise ProjMetaLocked(state=self.o.state)

        self.o.state = Proj.S.working
        self.o.add_track(info=Proj.T.start, now=g.now)

        pits: List[Pit] = Pit.query.join(Role). \
            filter(Role.proj_id == self.o.id). \
            filter(Pit.state == Pit.S.init). \
            all()
        for pit in pits:
            pit.start_at = dep_graph.get_start_time(base=g.now, dep=pit.role.dep)
            pit.due = pit.start_at + dep_graph.DURATION[pit.role.dep]
            pit.state = Pit.S.working if pit.start_at == g.now else Pit.S.pending

    def finish(self, url):
        self.o.state = Proj.S.fin
        self.o.url = url
        self.o.add_track(info=Proj.T.finish, now=g.now)

        redis.delete(f'cPath-{self.o.id}', f'cTree-{self.o.id}')

    def freeze(self):
        self.o.state = Proj.S.freezed
        self.o.add_track(info=Proj.T.freeze, now=g.now)

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
        role = cls.model(id=cls.gen_id(), proj=proj, dep=dep, name=name)
        db.session.add(role)

        return role

    @classmethod
    def remove(cls, ids):
        cls.model.query.filter(Role.id.in_(ids)).delete()

    def full_pick(self, pink_id):
        if self.o.taken:
            raise RoleIsTaken(by=self.o.pit)

        self.o.taken = True
        pit = PitMgr.create(self.o, pink_id)
        if pink_id != g.pink_id:
            pit.add_track(info=Pit.T.pick_f, now=g.now, by=g.piT)

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

    @staticmethod
    def _is_visible(proj_id, id_):
        if not redis.sismember(f'cAvbl-{proj_id}', id_):
            raise InvalidReply()

    @staticmethod
    def _get_path(proj_id, id_):
        return redis.sscan(f'cPath-{proj_id}', f'*/{id_}')

    @classmethod
    def post(cls, proj: Proj, reply_to_id: str, content: str):
        chat = cls.model(id=cls.gen_id(),
                         proj_id=proj.id,
                         pink_id=g.pink_id,
                         content=content,
                         timestamp=g.now)
        chat.set_order(proj_timestamp=proj.timestamp, now=g.now)
        chat.reply_to_id = reply_to_id  # can be none
        db.session.add(chat)

        if reply_to_id:
            cls._is_visible(proj.id, reply_to_id)

            path = cls._get_path(proj.id, reply_to_id)
            father = reply_to_id

        else:
            path = '/'
            father = proj.id

        replys_s = redis.hget(f'cTree-{proj.id}', father)
        with redis.pipeline(transaction=True) as p:
            p.hset(f'cTree-{proj.id}', chat.id, '')
            p.sadd(f'cAvbl-{proj.id}', chat.id)
            p.sadd(f'cPath-{proj.id}', path)

            if not replys_s:
                p.hset(f'cTree-{proj.id}', father, chat.id)
            else:
                replys = replys_s.split(';')
                replys.append(chat.id)
                p.hset(f'cTree-{proj.id}', father, ';'.join(replys))

            p.execute()

        return chat

    def edit(self, content):
        if self.o.pink_id != g.pink_id:
            raise AccessDenied(obj=self.o)
        self._is_visible(self.o.proj_id, self.o.id)

        self.o.update(now=g.now, content=content)

    def delete(self):
        self._is_visible(self.o.proj_id, self.o.id)

        self.o.delete = True

        path = '/'.join(self._get_path(self.o.proj_id, self.o.id).split('/')[:-1])
        queue = [redis.sscan_iter(f'cPath-{self.o.proj_id}', f'{path}/*')]
        redis.srem(f'cAvbl-{self.o.proj_id}', *[cpath.split('/')[-1] for cpath in  queue])
