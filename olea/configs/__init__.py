import os


def load_config(env=os.getenv('FLASK_ENV', 'production')):
    from werkzeug.utils import import_string

    module = import_string(f'configs.{env}')

    return module.Config()
