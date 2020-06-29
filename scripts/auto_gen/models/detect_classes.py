import enum
import inspect
import re

from sqlalchemy_ import BaseModel

from ..file_helpers import add_module

_metadata = BaseModel.metadata


@add_module
def detect_classes(module):
    contains = set()
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if (getattr(obj, 'metadata', None) is not _metadata and not issubclass(obj, enum.Enum)) \
            or name in ('BaseModel', 'ZEnum'):

            continue

        contains.add(name)

    return contains
