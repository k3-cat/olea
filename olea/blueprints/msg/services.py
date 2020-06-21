from flask import g

from models import Ann
from olea.base import BaseMgr
from olea.errors import AccessDenied
from olea.singleton import db


class AnnMgr(BaseMgr):
    module = Ann

    def __init__(self, obj_or_id):
        self.o: Ann = None
        super().__init__(obj_or_id)

    @classmethod
    def post(cls, cat, deps, exp, content):
        g.check_scopes(deps)
        ann = cls.model(id=cls.gen_id(),
                        cat=cat,
                        deps=deps,
                        exp=exp,
                        poster=g.pink_id,
                        timestamp=g.now,
                        content=content)
        db.session.add(ann)

        return ann

    def edit(self, content):
        if self.o.poster != g.pink_id:
            raise AccessDenied(obj=self.o)

        self.o.update(now=g.now, content=content)

    def delete(self):
        if self.o.poster != g.pink_id:
            raise AccessDenied(obj=self.o)

        self.o.deleted = True
