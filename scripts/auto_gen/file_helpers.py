import inspect
from functools import wraps

from isort import SortImports
from werkzeug.utils import import_string
from yapf.yapflib.yapf_api import FormatFile

from .g import DIR


def py_rw(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        path = kwargs['filepath']
        with path.open('r') as f:
            file_ = ['']
            file_.extend(f)

        kwargs['file_'] = file_

        flag = False
        init_path = path.parent / '__init__.py'
        if path != init_path:
            flag = True
            init_alt_path = path.parent / f'{init_path.name}_backup'
            init_path.replace(init_alt_path)
            init_path.open('w').close()

        try:
            relative_path = path.relative_to(DIR)
            module_str = str(relative_path).replace('/', '.').replace('\\', '.').replace('.py', '')
            kwargs['module'] = import_string(module_str)
            kwargs.pop('filepath')

            new_file_, ext = fun(*args, **kwargs)

            try:
                alt_path = path.parent / f'{path.name}_backup'
                path.replace(alt_path)

                with path.open('w') as f:
                    f.writelines(new_file_)

                SortImports(path)
                FormatFile(str(path), in_place=True)

                alt_path.unlink()

            except:
                alt_path.replace(path)
                raise

        finally:
            if flag:
                init_alt_path.replace(init_path)

        return ext

    return wrapper
