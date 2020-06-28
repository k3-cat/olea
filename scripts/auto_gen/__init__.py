import re
import sys

from werkzeug.utils import find_modules, import_string

from .clean_pycache import clean_pycache
from .g import DIR
from .version import Version

sys.path.append(str(DIR))


def main():
    clean_pycache(DIR, '**/auto_gen/**')
    version = Version()

    for module_str in find_modules(__name__, include_packages=True):
        module = import_string(module_str)
        if not hasattr(module, 'TARGET'):
            continue

        relative_path = module.TARGET.replace('.', '/')
        changed = version.check_dir(relative_path, module.IGNORES)
        if not changed:
            continue

        try:
            module.run(changed)
        except:
            raise
        else:
            version.save(relative_path)

    version.write()
