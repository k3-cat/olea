import inspect
import re

from ..file_helpers import py_rw


@py_rw
def detect_classes(module, file_):
    contains = set()
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if getattr(obj.__base__, '__name__', None) not in ('BaseModel', 'ZEnum'):
            continue

        contains.add(name)

    return file_, contains
