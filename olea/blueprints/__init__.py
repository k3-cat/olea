def register_blueprints(app):
    import inspect
    from werkzeug.utils import find_modules, import_string

    from olea.utils import FromConf

    for module_str in find_modules(__name__, include_packages=True):
        module = import_string(module_str)
        if not hasattr(module, 'bp'):
            continue

        app.register_blueprint(module.bp)
        import_string(f'{module_str}.views')

        services = inspect.getmembers(import_string(f'{module_str}.services'), inspect.isclass)
        for __, service in services:
            if not getattr(service, '__module__').startswith(module_str):
                continue

            for name, obj in service.__dict__.items():
                if not isinstance(obj, FromConf):
                    continue

                setattr(service, name, obj.bind(app))
