from flask import g
from sqlalchemy_ import BaseModel

from olea.auth import check_opt_duck
from olea.errors import AccessDenied, RecordNotFound
from olea.id_tool import IdTool

id_tool = IdTool()


def single_query(model, id_or_obj, condiction):
    if isinstance(id_or_obj, str):
        if len(id_or_obj) > 15 and not id_tool.verify(id_or_obj):
            raise RecordNotFound(cls_=model, id_=id_or_obj)
        if not (obj := model.query.get(id_or_obj)):
            raise RecordNotFound(cls_=model, id_=id_or_obj)
    else:
        obj = id_or_obj

    if condiction(obj) or check_opt_duck():
        return obj

    raise AccessDenied(obj=obj)


class BaseMgr():
    model = BaseModel

    def __init__(self, obj_or_id):
        if isinstance(obj_or_id, str):
            if len(obj_or_id) > 15 and not id_tool.verify(obj_or_id):
                raise RecordNotFound(cls_=self.model, id_=obj_or_id)
            if not (obj := self.model.query.get(obj_or_id)):
                raise RecordNotFound(cls_=self.model, id_=obj_or_id)
        else:
            obj = obj_or_id
        self.o = obj

    @classmethod
    def gen_id(cls):
        return id_tool.generate(length=cls.model.__id_len__)
