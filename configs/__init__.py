def load_config(env):
    from werkzeug.utils import import_string

    if env == 'production':
        module = import_string('config.production')
    else:
        module = import_string(f'config.{env}')

    return module.Config()
