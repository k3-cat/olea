from flask import g

from models import Ann, Chat, Proj
from olea.base import BaseMgr
from olea.errors import AccessDenied, InvalidReply, ProjMetaLocked
from olea.singleton import db, redis


class AnnMgr(BaseMgr):
    module = Ann

    def __init__(self, obj_or_id):
        self.o: Ann = None
        super().__init__(obj_or_id)

    @classmethod
    def post(cls, cat, deps, expiration, content):
        g.check_scopes(deps)
        ann = cls.model(id=cls.gen_id(),
                        cat=cat,
                        deps=deps,
                        expiration=expiration,
                        poster_id=g.pink_id,
                        content=content,
                        at=g.now)
        db.session.add(ann)

        return ann

    def edit(self, content):
        if self.o.poster_id != g.pink_id:
            raise AccessDenied(obj=self.o)

        self.o.update(now=g.now, content=content)

    def delete(self):
        if self.o.poster_id != g.pink_id:
            raise AccessDenied(obj=self.o)

        self.o.deleted = True


class ProjMgr(BaseMgr):
    def __init__(self, obj_or_id):
        self.o: Proj = None
        super().__init__(obj_or_id)

    def post_chat(self, reply_to_id, content):
        if self.o.status != Proj.S.working:
            raise ProjMetaLocked(status=self.o.status)

        # TODO: permission check
        return ChatMgr.post(self, reply_to_id, content)


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
    def post(cls, proj, reply_to_id: str, content: str):
        chat = cls.model(id=cls.gen_id(),
                         proj_id=proj.id,
                         pink_id=g.pink_id,
                         at=g.now,
                         content=content)
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

        with redis.pipeline(transaction=True) as p:
            p.zadd(f'cLog-{proj.id}', f'+ {chat.id}')
            p.sadd(f'cAvbl-{proj.id}', chat.id)
            p.sadd(f'cPath-{proj.id}', path)

            p.execute()

        return chat

    def edit(self, content):
        if self.o.pink_id != g.pink_id:
            raise AccessDenied(obj=self.o)
        self._is_visible(self.o.proj_id, self.o.id)

        self.o.update(now=g.now, content=content)

        redis.zadd(f'cLog-{self.o.proj_id}', f'e {self.o.id}')

    def delete(self):
        self._is_visible(self.o.proj_id, self.o.id)

        self.o.delete = True

        path = self._get_path(self.o.proj_id, self.o.id)
        queue = [redis.sscan_iter(f'cPath-{self.o.proj_id}', f'{path}/*')]
        with redis.pipeline(transaction=True) as p:
            p.zadd(f'cLog-{self.o.proj_id}', f'- {self.o.id}')
            p.srem(f'cAvbl-{self.o.proj_id}', *[cpath.split('/')[-1] for cpath in queue])

            p.execute()

    def restore(self):
        self.o.delete = False

        path = self._get_path(self.o.proj_id, self.o.id)
        queue = [redis.sscan_iter(f'cPath-{self.o.proj_id}', f'{path}/*')]
        with redis.pipeline(transaction=True) as p:
            p.zadd(f'cLog-{self.o.proj_id}', f'r {self.o.id}')
            p.sadd(f'cAvbl-{self.o.proj_id}', *[cpath.split('/')[-1] for cpath in queue])

            p.execute()
