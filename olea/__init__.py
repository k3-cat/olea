import os

from flask import Flask


def create_app(env=os.getenv('FLASK_ENV') or 'production'):
    from config import load_config

    from .init.command import register_commands
    from .init.hook import hook_hooks
    from .init.shellcontext import set_shellcontext

    from .blueprints import register_blueprints
    from .errors import register_error_handlers
    from .exts import init_extensions

    print(f'\n- - - - - olea [{env}] - - - - -\n')
    app = Flask(__name__)
    app.env = env

    load_config(app, env)
    # configure_logger(app)
    register_error_handlers(app)
    init_extensions(app)
    register_blueprints(app)
    hook_hooks(app)
    set_shellcontext(app)
    register_commands(app)
    return app
