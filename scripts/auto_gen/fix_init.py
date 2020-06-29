import inspect
import json
import re
from functools import wraps
from itertools import chain

from werkzeug.utils import import_string

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
def fix_init(filepath, file_, current):
    file_text = ''.join(file_)

    # fetch old __all__ list
    if match := re.match(r'__all__ = \[(.*)\]$', file_text, flags=re.DOTALL | re.M):
        old_all = set(match.group(1).replace('\n', ''). \
            replace(' ', '').replace("'", '').split(','))

    else:
        old_all = set()

    # fetch old import statements
    offsets = list()
    imports = list()
    for i in chain(
            re.finditer(r'^(?:from .*? )?import \(.*?\)$\n', file_text, flags=re.DOTALL | re.M),
            re.finditer(r'^(?:from .*? )?import (?!\().*?$\n', file_text, flags=re.M),
    ):
        offsets.append(i.end())
        imports.append(i.group())

    # find the last line of import statements
    if offsets:
        unused_lines = file_text.count('\n', 0, max(offsets))
    else:
        unused_lines = 0

    # build map from sub_module_name to line_no in `imports`
    imports_map = {
        statement.split(' import ')[0].lstrip('from .'): i
        for i, statement in enumerate(imports)
    }

    # update import statements
    for module_str, contains in current.items():
        statement = f'from .{module_str} import {",".join(contains)}\n'
        try:
            old_contains = set(imports[imports_map[module_str]]. \
                split(' import ')[0]. \
                replace('\n', '').replace(' ', '').lstrip('(').rstrip(')'). \
                split(','))

        except KeyError:
            imports.append(statement)
            old_all = old_all | contains

        else:
            imports[imports_map[module_str]] = statement
            old_all = (old_all - old_contains) | contains

    # update file
    new_file_ = list()
    new_all_list = json.dumps(sorted(str(name) for name in old_all)).replace('"', "'")
    new_file_.append(f'__all__ = {new_all_list}\n\n')
    new_file_.extend(imports)
    new_file_.extend(file_[unused_lines:])

    return new_file_, None
