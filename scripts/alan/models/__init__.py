from ..fix_init import fix_init
from .detect_classes import detect_classes

TARGET = 'models'
IGNORES = ['__init__.py']


def run(changed):
    current = dict()
    for filepath in changed:
        contains = detect_classes(filepath=filepath)
        current[filepath.stem] = contains

    fix_init(target=TARGET, current=current)
