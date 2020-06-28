import inspect
import re

from ..file_helpers import py_rw
from .error_code import check_err_code, generate_err_code

statement = lambda: f"    code = '{generate_err_code()}'\n"


@py_rw
def fix_error_code(module, file_):
    offset = 0
    contains = set()
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if getattr(obj.__base__.__base__, '__name__', None) != 'BaseError':
            continue

        contains.add(name)

        lines, base_no = inspect.getsourcelines(obj)
        if not obj.code:
            file_.insert(offset + base_no + 1, statement())
            file_.insert(offset + base_no + 2, '\n')
            offset += 2

        else:
            if check_err_code(obj.code):
                continue

            for i, line in enumerate(lines):
                if re.match(r"^    code = '.*'\n$", line):
                    break
            file_[offset + base_no + i] = statement()

    return file_, contains
