from abc import ABC

from flask import g

from olea.errors import AccessDenied, PermissionDenied, RecordNotFound
from olea.singleton import id_tool


def single_query(model, id_or_obj, condiction):
    if isinstance(id_or_obj, str):
        if len(id_or_obj) > 15 and not id_tool.verify(id_or_obj):
            raise RecordNotFound(cls=model, id=id_or_obj)
        if not (obj := model.query.get(id_or_obj)):
            raise RecordNotFound(cls=model, id=id_or_obj)
    else:
        obj = id_or_obj

    if condiction(obj):
        return obj
    try:
        g.check_duck()
    except PermissionDenied():
        raise AccessDenied(obj=obj)


class BaseMgr(ABC):
    model = None

    def __init__(self, obj_or_id):
        if isinstance(obj_or_id, str):
            if len(obj_or_id) > 15 and not id_tool.verify(obj_or_id):
                raise RecordNotFound(cls=self.model, id=obj_or_id)
            if not (obj := self.model.query.get(obj_or_id)):
                raise RecordNotFound(cls=self.model, id=obj_or_id)
        else:
            obj = obj_or_id
        self.o = obj

    @classmethod
    def gen_id(cls):
        return id_tool.generate(length=cls.model.__id_len__)

    @property
    def query(self):
        return self.model.query
