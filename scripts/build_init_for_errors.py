import inspect
import json
import os
import sys
from pathlib import Path

from werkzeug.utils import find_modules, import_string

MODULE = 'errors'
DIR = (Path(__file__).parents[1] / 'olea')
PATH = DIR / MODULE / '__init__.py'
sys.path.append(str(DIR))


def split_file(path):
    flag = False
    content = ''
    with path.open('r') as f:
        while line := f.readline():
            if not flag and ('def ' in line or 'class ' in line):
                flag = True
            if flag:
                content += line
    return content


def build_import_statement(module):
    imports = list()
    all_list = list()
    for module_name in find_modules(module):
        all_in_module = list()
        for name, obj in inspect.getmembers(import_string(module_name), inspect.isclass):
            if name == 'ABC' or getattr(obj, 'code', '') == '':
                continue
            all_in_module.append(name)
        if not all_in_module:
            all_in_module.append('BaseError')
        all_list.extend(all_in_module)
        imports.append(
            f'from {module_name.replace(module, "")} import {", ".join(all_in_module)}\n')
    all_list.sort()

    return imports, all_list


if __name__ == "__main__":
    init_content = split_file(PATH)

    ALT_PATH = PATH.parent / 'backup'
    PATH.replace(ALT_PATH)
    try:
        imports, all_list = build_import_statement(MODULE)
        ALT_PATH.unlink()
    except:
        ALT_PATH.replace(PATH)
        raise

    with (PATH).open('w') as f:
        f.writelines(imports)
        f.write('\n__all__ = ')
        f.write(json.dumps(all_list).replace('"', "'"))
        f.write('\n')
        f.write(init_content)
        f.write('\n')
