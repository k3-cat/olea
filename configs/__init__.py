def load_config(env):
    from werkzeug.utils import import_string

    if env == 'production':
        module = import_string('configs.base_config')
    else:
        module = import_string(f'configs.{env}')

    return module.Config()
