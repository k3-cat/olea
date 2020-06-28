from ..fix_init import fix_init
from ..g import MAIN_PACKAGE
from .fix_error_code import fix_error_code

TARGET = f'{MAIN_PACKAGE}.errors'
IGNORES = ['__init__.py']


def run(changed):
    current = dict()
    for filepath in changed:
        contains = fix_error_code(filepath=filepath)
        current[filepath.stem] = contains

    if 'base_error' in current:
        current['base_error'] = {'BaseError'}

    fix_init(target=TARGET, current=current)
