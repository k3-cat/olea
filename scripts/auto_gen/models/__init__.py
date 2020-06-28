TARGET = 'models'
IGNORES = ['__init__.py']

from ..fix_init import fix_init
from ..g import DIR, MAIN_PACKAGE
from .detect_classes import detect_classes


def run(changed):
    current = dict()
    for filepath in changed:
        contains = detect_classes(filepath=filepath)
        current[filepath.stem] = contains

    fix_init(filepath=DIR / MAIN_PACKAGE / 'errors/__init__.py', current=current)
