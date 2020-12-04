from flask import g

from models import Duck, Pink
from core.base import single_query
from core.singleton import redis


def pink_serializer(pink=None, pinks=None):
    if not pinks:
        result = pink.__json__()
        result['last_access'] = redis.hget('last_access', g.pink_id)
        if pink.id == g.pink_id:
            user, host = pink.email.split('@')
            result['email'] = f'{user[0:3]}******@{host}'

    else:
        result = list()
        queue = list()
        for p in pinks:
            result.append(p.__json__())
            queue.append(p.id)

        last_access = redis.hmget('last_access', *queue)
        for info, access_time in zip(result, last_access):
            info['last_access'] = access_time

    return result


class PinkQuery():
    @staticmethod
    def single(id_):
        pink = single_query(model=Pink, id_or_obj=id_, condiction=lambda obj: obj.id == g.pink_id)

        return pink_serializer(pink)

    @staticmethod
    def search(deps, name, qq):
        query = Pink.query
        if deps:
            query.filter(Pink.deps.in_(deps))
        else:
            if name:
                query.filter(Pink.name.ilike(f'%{name}%'))
            if qq:
                query.filter(Pink.qq.like(f'%{qq}%'))
        pinks = query.all()

        return pink_serializer(pinks=pinks)


class DuckQuery():
    @staticmethod
    def ducks(pink_id, node, nodes, allow):
        query = Duck.query.filter_by(pink_id=pink_id)
        if node:
            query.filter(Duck.node.ilike(f'%{node}%'))
        else:
            if nodes:
                query.filter(Duck.node.in_(nodes))
            if allow is not None:
                query.filter_by(allow=allow)
        return query.all()
