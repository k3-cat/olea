import os


def register_commands(app):
    import click

    @click.command()
    @click.option('--length', default=25)
    @click.option('--profile-dir', default=None)
    def profile(length, profile_dir):
        from olea import create_app
        from werkzeug.contrib.profiler import ProfilerMiddleware
        app = create_app()
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                                          restrictions=(length, ),
                                          profile_dir=profile_dir)
        app.run(debug=False)


def set_shellcontext(app):
    from models import Pink, Pit, Proj
    from olea.singleton import db

    def shell_context():
        return {'app': app, 'db': db, 'Pink': Pink, 'Proj': Proj, 'Pit': Pit}

    app.shell_context_processor(shell_context)


def create_manager(env=os.getenv('FLASK_ENV', 'production')):
    from flask import Flask
    from flask_migrate import Migrate

    from configs import load_config
    from olea.singleton import db

    app = Flask(__name__)

    app.config.from_object(load_config(env))

    db.init_app(app)
    migrate = Migrate(app, db)

    set_shellcontext(app)
    register_commands(app)

    return app


application = create_manager()
