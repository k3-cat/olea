import inspect
import re

from ..file_helpers import add_module, read, write
from .error_code import check_err_code, generate_err_code


def gen_statement():
    return f"    code = '{generate_err_code()}'\n"


@write
@read
@add_module
def fix_error_code(module, file_):
    offset = 0
    contains = set()
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if getattr(obj.__base__.__base__, '__name__', None) != 'BaseError':
            continue

        contains.add(name)

        lines, base_no = inspect.getsourcelines(obj)
        if not obj.code:
            file_.insert(offset + base_no + 1, gen_statement())
            file_.insert(offset + base_no + 2, '\n')
            offset += 2

        else:
            if check_err_code(obj.code):
                continue

            for i, line in enumerate(lines):
                if re.match(r"^    code = '.*'\n$", line):
                    break
            file_[offset + base_no + i] = gen_statement()

    return file_, contains
