import inspect

from ..file_helpers import add_module


@add_module
def detect_classes(module):
    contains = set()
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if getattr(obj, '__module__', '') != module.__name__:
            continue

        contains.add(name)

    return contains
