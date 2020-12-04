import os
from datetime import datetime, timezone

from flask import Flask, g

from olea_path import register_packages

register_packages()


def create_app(env=os.getenv('FLASK_ENV', 'production')):
    from configs import load_config

    from .blueprints import register_blueprints
    from .errors import register_error_handlers

    print(f'\n- - - - - olea [{env}] - - - - -\n')
    app = Flask(__name__)
    app.env = env
    app.config.from_object(load_config(env))

    # configure_logger(app)
    register_error_handlers(app)
    hook_hooks(app)
    init_extensions(app)
    register_blueprints(app)

    return app


def init_extensions(app: Flask):
    from .auth import init_app as auth_init_app
    from .singleton import db, fjson, ip2loc, onedrive, redis, sendgrid, sqlogger
    from .utils import FromConf

    auth_init_app(app)
    FromConf.init_app(app)

    db.init_app(app)
    fjson.init_app(app)
    ip2loc.init_app(app)
    redis.init_app(app)
    onedrive.init_app(app)
    sendgrid.init_app(app)
    sqlogger.init_app(app)


def hook_hooks(app: Flask):
    from sentry_sdk import configure_scope

    from .utils import random_b85

    @app.before_request
    def add_track():
        g.now = datetime.now(timezone.utc)
        g.ref = random_b85(k=20)
        with configure_scope() as scope:
            scope.set_tag('ref', g.ref)

    # ---------------------------------------
    from .singleton import db

    @app.teardown_request
    def auto_commit(response):
        db.session.commit()
        return response

    # ---------------------------------------
    from .singleton import sqlogger

    @app.teardown_request
    def log(response):
        sqlogger._log(response=response)
        return response
