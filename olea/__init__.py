import datetime
import os
import sys
from pathlib import Path

from flask import Flask, g, request

PATH = Path(__file__).parents[1] / 'site-packages'
sys.path.append(str(PATH / 'json_api'))
sys.path.append(str(PATH / 'pypat'))
sys.path.append(str(PATH))


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


def init_extensions(app):
    from olea.auth import init_app as auth_init_app
    from olea.singleton import db, fjson, redis, mailgun, onedrive, ip2loc
    from olea.utils import FromConf

    auth_init_app(app)
    FromConf.init_app(app)

    db.init_app(app)
    fjson.init_app(app)
    ip2loc.init_app(app)
    redis.init_app(app)
    mailgun.init_app(app)
    onedrive.init_app(app)


def hook_hooks(app):
    from olea.utils import random_b85
    from sentry_sdk import configure_scope

    @app.before_request
    def add_track():
        g.now = datetime.datetime.utcnow()
        g.ref = random_b85(k=20)
        with configure_scope() as scope:
            scope.set_tag('ref', g.ref)
