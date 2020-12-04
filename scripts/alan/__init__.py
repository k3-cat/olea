from werkzeug.utils import find_modules, import_string

from path import DIR, register_olea

from .clean_pycache import clean_pycache
from .version import Version

register_olea()


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

        except BaseException:
            raise

        else:
            version.save(relative_path)
