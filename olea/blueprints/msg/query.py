from flask import g

from models import Ann, Pink, Chat
from olea.errors import AccessDenied
from olea.singleton import redis


class AnnQuery():
    @staticmethod
    def search(deps):
        if deps - Pink.query.get(g.pink_id).deps:
            raise AccessDenied(cls_=Ann)

        query = Ann.query.filter_by(deleted=False)
        if deps:
            query = query.filter(Ann.deps.in_(deps))

        anns = query.all()
        for ann in anns:
            ann.readers.set_default(g.pink_id, list())

            trace = ann.readers[g.pink_id]
            if len(trace) == ann.ver:
                continue

            trace.append(g.now)

        return anns


class ChatQuery():
    @staticmethod
    def chat_index(proj_id, offset):
        logs = redis.zrange(f'cLog-{proj_id}', offset, -1)

        return logs

    @staticmethod
    def chats(chats):
        return Chat.query.filter(Chat.id.in_(chats)).all()
