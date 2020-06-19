from flask import g

from models import Duck, Pink
from olea.base import single_query


class PinkQuery():
    @staticmethod
    def single(id_):
        return single_query(model=Pink, id_or_obj=id_, condiction=lambda obj: obj.id == g.pink_id)

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
        return query.all()

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
