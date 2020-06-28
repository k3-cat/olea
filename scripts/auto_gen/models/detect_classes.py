import inspect
import re

from ..file_helpers import add_module


@add_module
def detect_classes(module):
    contains = set()
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if getattr(obj.__base__, '__name__', None) not in ('BaseModel', 'ZEnum'):
            continue

        contains.add(name)

    return contains
