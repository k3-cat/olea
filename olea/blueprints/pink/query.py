from flask import g

from models import Duck, Pink
from olea.base import single_query
from olea.singleton import redis


def pink_serilizer(pink, pinks=None):
    if not pinks:
        result = pink.__json__()
        result['last_access'] = redis.hget('last_access', g.pink_id)

    else:
        result = list()
        queue = list()
        for pink in pinks:
            result.append(pink.__json__())
            queue.append(pink.id)

        last_access = redis.hmget('last_access', *queue)
        for info, access_time in zip(result, last_access):
            info['last_access'] = access_time

    return result


class PinkQuery():
    @staticmethod
    def single(id_):
        pink = single_query(model=Pink, id_or_obj=id_, condiction=lambda obj: obj.id == g.pink_id)

        return pink_serilizer(pink)

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

        return pink_serilizer(pinks=pinks)


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
