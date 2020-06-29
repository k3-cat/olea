import inspect
import json
import re
from functools import wraps

from .file_helpers import add_module, read, write
from .g import DIR


def add_filepath(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        target = kwargs.pop('target')
        kwargs['filepath'] = DIR / target.replace('.', '/') / '__init__.py'

        return fun(*args, **kwargs)

    return wrapper


@add_filepath
@write
@read
@add_module
def fix_init(module, file_, current):
    file_text = ''.join(file_)
    imports = re.findall(r'^(?:from .*? )?import \(.*?\)$', file_text, flags=re.DOTALL | re.M)
    imports.extend(re.findall(r'^(?:from .*? )?import (?!\().*?$', file_text, flags=re.M))
    imports = [f'{statement}\n' for statement in imports]
    old_all = set(getattr(module, '__all__', list()))

    imports_map = {
        statement.split(' import ')[0].lstrip('from .'): i
        for i, statement in enumerate(imports)
    }

    for module_str, contains in current.items():
        statement = f'from .{module_str} import {",".join(contains)}\n'
        try:
            old_contains = set(imports[imports_map[module_str]]. \
                split(' import ')[0]. \
                replace('\n', '').lstrip('(').rstrip(')'). \
                split(','))

        except KeyError:
            imports.append(statement)

        else:
            imports[imports_map[module_str]] = statement
            old_all = (old_all - old_contains) | contains

    new_file_ = list()
    new_file_.append(f'__all__ = {new_all_list}\n\n')
    new_file_.extend(imports)
    new_all_list = json.dumps(sorted(str(name) for name in old_all)).replace('"', "'")

    for __, obj in inspect.getmembers(module, inspect.isfunction):
        lines, __ = inspect.getsourcelines(obj)
        new_file_.extend(lines)

    print(*new_file_)

    return new_file_, None
