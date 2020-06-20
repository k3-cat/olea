from flask import g

from models import Proj, Chat
from olea.base import single_query
from olea.errors import AccessDenied
from olea.singleton import redis


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
            raise AccessDenied(cls_=Proj)
        query = Proj.query.filter(Proj.state.in_(states))
        if types:
            query.filter(Proj.type.in_(types))
        return query.all()


class ChatQuery():
    @staticmethod
    def chat_index(proj_id):
        return redis.hgetall(f'cTree-{proj_id}')

    @staticmethod
    def chats(chats):
        return Chat.query.filter(Chat.id.in_(chats)).all()
