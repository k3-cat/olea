import os


def load_config(env=os.getenv('FLASK_ENV', 'production')):
    from werkzeug.utils import import_string

    if env == 'production':
        module = import_string('configs.base_config')
    else:
        module = import_string(f'configs.{env}')

    return module.Config()
