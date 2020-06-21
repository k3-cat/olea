from flask import g

from models import Proj, Chat
from olea.base import single_query
from olea.errors import AccessDenied
from olea.singleton import redis


class ProjQuery():
    PUBLIC_STATES = {Proj.S.working, Proj.S.pre, Proj.S.upload}

    @classmethod
    def single(cls, id_):
        proj = single_query(model=Proj,
                            id_or_obj=id_,
                            condiction=lambda obj: obj.state in cls.PUBLIC_STATES)
        return proj

    @classmethod
    def search(cls, states=None, cats=None):
        if states - cls.PUBLIC_STATE and not g.check_opt_perm:
            raise AccessDenied(cls_=Proj)
        query = Proj.query.filter(Proj.state.in_(states))
        if cats:
            query.filter(Proj.cat.in_(cats))
        return query.all()


class ChatQuery():
    @staticmethod
    def chat_index(proj_id):
        available = redis.smembers(f'cAvbl-{proj_id}')
        index = dict(zip(available, redis.hmget(f'cTree-{proj_id}', *available)))

        return index

    @staticmethod
    def chats(chats):
        return Chat.query.filter(Chat.id.in_(chats)).all()
