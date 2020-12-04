from functools import wraps

from isort import file as sort_file
from werkzeug.utils import import_string
from yapf.yapflib.style import CreateStyleFromConfig, SetGlobalStyle
from yapf.yapflib.yapf_api import FormatFile

from path import OLEA_DIR

SetGlobalStyle(CreateStyleFromConfig('{based_on_style: pep8, column_limit: 100}'))


def read_write(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        path = kwargs['filepath']
        with path.open('r') as f:
            file_ = ['']
            file_.extend(f)
        kwargs['file_'] = file_

        # run original function
        new_file_, ext = fun(*args, **kwargs)

        alt_path = path.parent / f'{path.name}_backup'
        path.replace(alt_path)
        try:
            with path.open('w') as f:
                f.writelines(new_file_)

            sort_file(path)
            FormatFile(str(path), in_place=True)

            alt_path.unlink()

        except BaseException:
            alt_path.replace(path)
            raise

        return ext

    return wrapper


def add_module(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        path = kwargs['filepath']
        init_path = path.parent / '__init__.py'
        init_alt_path = path.parent / '__init__.py_backup'
        init_path.replace(init_alt_path)
        init_path.open('w').close()

        try:
            relative_path = path.relative_to(OLEA_DIR)
            module_str = str(relative_path).replace('/', '.').replace('\\', '.').replace('.py', '')
            kwargs['module'] = import_string(module_str)
            kwargs.pop('filepath')

            result = fun(*args, **kwargs)

        finally:
            init_alt_path.replace(init_path)

        return result

    return wrapper
