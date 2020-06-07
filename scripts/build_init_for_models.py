import json
import os
import sys
from pathlib import Path

from werkzeug.utils import find_modules, import_string

MODULE = 'models'
DIR = (Path(__file__).parents[1])
PATH = DIR / MODULE / '__init__.py'
sys.path.append(str(DIR))
sys.path.append(str(DIR / 'site-packages'))


def build_import_statement(module):
    imports = list()
    all_list = list()
    for module_name in find_modules(module):
        all_in_module = import_string(module_name).__all__.copy()
        all_in_module.sort()
        all_list.extend(all_in_module)
        imports.append(
            f'from {module_name.replace(module, "")} import {", ".join(all_in_module)}\n')
    all_list.sort()

    return imports, all_list


if __name__ == "__main__":
    ALT_PATH = PATH.parent / 'backup'
    PATH.replace(ALT_PATH)
    try:
        imports, all_list = build_import_statement(MODULE)
        ALT_PATH.unlink()
    except:
        ALT_PATH.replace(PATH)
        raise

    with (DIR / 'models/__init__.py').open('w') as f:
        f.writelines(imports)
        f.write('\n__all__ = ')
        f.write(json.dumps(all_list).replace('"', "'"))
        f.write('\n')
