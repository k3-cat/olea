import json
import sys
from pathlib import Path

from werkzeug.utils import find_modules, import_string

MODULE = 'models'


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

    return (imports, all_list)


if __name__ == "__main__":
    PROJ_ROOT = (Path(__file__).parents[2])
    PATH = PROJ_ROOT / MODULE / '__init__.py'
    sys.path.append(str(PROJ_ROOT))
    # able to import sqlalchemy_
    sys.path.append(str(PROJ_ROOT / 'site-packages'))

    ALT_PATH = PATH.parent / 'backup'
    PATH.replace(ALT_PATH)
    try:
        imports, all_list = build_import_statement(MODULE)
        ALT_PATH.unlink()
    except:
        ALT_PATH.replace(PATH)
        raise

    with (PROJ_ROOT / 'models/__init__.py').open('w') as f:
        f.writelines(imports)
        f.write('\n__all__ = ')
        f.write(json.dumps(all_list).replace('"', "'"))
        f.write('\n')
