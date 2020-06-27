import inspect
import json
import random
import re
import string
import sys

from pathlib import Path

from werkzeug.utils import find_modules, import_string

MODULE = 'errors'

CHARS = string.digits + string.ascii_uppercase


def generate_err_code(k):
    result = []
    for i in range(k - 1):
        result.append(random.randint(0, 35))
    sum_ = 0
    code = ''
    for order in result:
        sum_ += order
        code += CHARS[order]
    code += CHARS[(36 - (sum_ % 36)) % 36]
    return code


statement = lambda: f"    code = '{generate_err_code(5)}'\n"


def check_err_code(code):
    result = []
    for char in code:
        result.append(CHARS.index(char))
    sum_ = 0
    for order in result:
        sum_ += order
    if sum_ % 36 != 0:
        return False
    return True


def build_import_statement(module):
    for module_name in find_modules(module):
        module = import_string(module_name)
        with open(inspect.getsourcefile(module), 'r') as f:
            file_ = ['']
            file_.extend(f)

        offset = 0
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if getattr(obj.__base__.__base__, '__name__', None) != 'BaseError':
                continue

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

        with open(inspect.getsourcefile(module), 'w') as f:
            f.writelines(file_)


if __name__ == "__main__":
    DIR = (Path(__file__).parents[2] / 'olea')
    PATH = DIR / MODULE / '__init__.py'
    sys.path.append(str(DIR))

    build_import_statement(MODULE)
