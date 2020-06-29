from flask import g

from models import Ann, Chat, Pink
from olea.base import single_query
from olea.errors import AccessDenied
from olea.singleton import redis


def ann_serilizer(ann=None, anns=None):
    if not anns:
        result = ann.__json__()
        result['readers'] = ann.readers

    else:
        result = list()
        for a in anns:
            info = a.__json__()
            count = 0
            for read_time_track in a.readers.values():
                if len(read_time_track) >= a.ver:
                    count += 1
            info['readers'] = count
            result.append(info)

    return result


class AnnQuery():
    @staticmethod
    def single(id_):
        ann = single_query(Ann, id_, lambda obj: obj.deleted is False)
        return ann_serilizer(ann)

    @staticmethod
    def search(deps):
        if deps - Pink.query.get(g.pink_id).deps:
            raise AccessDenied(cls_=Ann)

        query = Ann.query.filter_by(deleted=False)
        if deps:
            query = query.filter(Ann.deps.in_(deps))

        anns = query.all()
        for ann in anns:
            ann.read(by=g.pink_id, now=g.now)

        return ann_serilizer(anns=anns)


class ChatQuery():
    @staticmethod
    def chat_logs(proj_id, offset):
        logs = redis.zrange(f'cLog-{proj_id}', offset, -1)

        return logs

    @staticmethod
    def chats(chats):
        return Chat.query.filter(Chat.id.in_(chats)).all()
