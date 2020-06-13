import datetime


def hook_hooks(app):
    from flask import g, request

    # ---------------------------------------------------------------
    from olea.auth import init_app
    init_app(app)

    # ---------------------------------------------------------------
    from olea.utils import random_b85
    from sentry_sdk import configure_scope

    @app.before_request
    def add_track():
        g.now = datetime.datetime.utcnow()
        g.ref = random_b85(k=20)
        with configure_scope() as scope:
            scope.set_tag('ref', g.ref)
