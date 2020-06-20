from flask import g

from models import Ann, Pink
from olea.errors import AccessDenied


class AnnQuery():
    @staticmethod
    def search(deps):
        if deps - Pink.query.get(g.pink_id).deps:
            raise AccessDenied(cls_=Ann)

        query = Ann.query.filter_by(deleted=False)
        if deps:
            query = query.filter(Ann.deps.in_(deps))

        return query.all()
