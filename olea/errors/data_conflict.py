from abc import ABC

from .base_error import BaseError


class DataConflict(BaseError, ABC):
    http_code = 400


class RecordNotFound(DataConflict):
    code = 'SYAV5'

    def __init__(self, cls_, id_):
        super().__init__(cls=cls_.__name__, id=id_)


class DuplicatedRecord(DataConflict):
    code = 'XB0TZ'

    def __init__(self, obj):
        self.obj = obj
        super().__init__(cls=obj.__class__.__name__, id=obj.id)


class FileVerConflict(DataConflict):
    code = '5RV81'

    def __init__(self, req_sha1):
        super().__init__(req_sha1=req_sha1)


class FileExist(DataConflict):
    code = '62C0G'

    def __init__(self, pit):
        super().__init__(pit_id=pit.id, ver=pit.ver)
