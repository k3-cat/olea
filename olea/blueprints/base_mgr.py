from abc import ABC

from olea.errors import RecordNotFound
from olea.id_tool import id_tool


class BaseMgr(ABC):
    model = None

    def __init__(self, obj_or_id):
        if isinstance(obj_or_id, str):
            if not id_tool.verify(obj_or_id):
                raise RecordNotFound(cls=self.model, id=obj_or_id)
            obj = self.model.query.get(obj_or_id)
            if not obj:
                raise RecordNotFound(cls=self.model, id=obj_or_id)
        else:
            obj = obj_or_id
        self.o: self.model = obj

    @classmethod
    def gen_id(cls):
        return id_tool.generate(length=cls.model.__id_len__)

    @property
    def query(self):
        return self.model.query
