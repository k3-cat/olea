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

    old_import = dict()
    old_all = set(getattr(module, '__all__', list()))
    for statement in imports:
        s = statement.split(' import ')
        s[0] = s[0].lstrip('from .')
        s[1] = s[1].replace('\n', '').lstrip('(').rstrip(')')
        s[1] = re.sub(r',\s+', ',', s[1])
        old_import[s[0]] = set(s[1].split(','))

    for module_str, contains in current.items():
        old_import.setdefault(module_str, set())
        add = (contains - old_import[module_str])  # add
        sub = (old_import[module_str] - contains)  # sub
        old_all = old_all | add
        old_all = old_all - sub

        old_import[module_str] = sorted(contains)

    new_file_ = list()
    new_file_.extend([
        f'from .{module_str} import {",".join(contains)}\n'
        for module_str, contains in old_import.items()
    ])
    new_all_list = json.dumps(sorted([str(name) for name in old_all])).replace('"', "'")
    new_file_.append(f'__all__ = {new_all_list}\n')

    for __, obj in inspect.getmembers(module, inspect.isfunction):
        lines, __ = inspect.getsourcelines(obj)
        new_file_.extend(lines)

    return new_file_, None
