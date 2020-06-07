def set_shellcontext(app):
    '''set shell context objects.'''

    from ..exts import db
    from models import Pink, Pit, Proj

    def shell_context():
        return {'app': app, 'db': db, 'Pink': Pink, 'Proj': Proj, 'Pit': Pit}

    app.shell_context_processor(shell_context)
