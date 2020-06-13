def register_commands(app):
    import click
    from flask.cli import with_appcontext

    @click.command()
    @click.option('--length', default=25)
    @click.option('--profile-dir', default=None)
    def profile(length, profile_dir):
        from werkzeug.contrib.profiler import ProfilerMiddleware
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                                          restrictions=(length, ),
                                          profile_dir=profile_dir)
        app.run(debug=False)


def set_shellcontext(app):
    from models import Pink, Pit, Proj
    from olea.exts import db

    def shell_context():
        return {'app': app, 'db': db, 'Pink': Pink, 'Proj': Proj, 'Pit': Pit}

    app.shell_context_processor(shell_context)


if __name__ == '__main__':
    from olea import create_app

    app = create_app()

    set_shellcontext(app)
