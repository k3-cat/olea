from abc import ABC

from .base_error import BaseError


class DataConflict(BaseError, ABC):
    http_code = 400


class RecordNotFound(DataConflict):
    code = 'I4HX'

    def __init__(self, cls, id_):
        super().__init__(cls=cls.__name__, id=id_)


class DuplicatedRecord(DataConflict):
    code = 'JQ9I'

    def __init__(self, obj):
        super().__init__(cls=obj.__class__.__name__, id=obj.id)


class FileVerConflict(DataConflict):
    code = 'asda'

    def __init__(self, req_sha1):
        super().__init__(req_sha1=req_sha1)


class FileExist(DataConflict):
    code = 'JQ9I'

    def __init__(self, pit_id, ver):
        super().__init__(pit_id=pit_id, ver=ver)
