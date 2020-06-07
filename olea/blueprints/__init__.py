def register_blueprints(app):
    '''Register Flask blueprints.'''
    from werkzeug.utils import find_modules, import_string

    for module_str in find_modules(__name__):
        module = import_string(module_str)
        if hasattr(module, 'bp'):
            app.register_blueprint(module.bp)
            import_string(f'{module_str}.views')
