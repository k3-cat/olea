import os
import sys
from pathlib import Path

from flask import Flask

PATH = Path(__file__).parents[1] / 'site-packages'
sys.path.append(str(PATH / 'jsonform'))
sys.path.append(str(PATH / 'pypat'))
sys.path.append(str(PATH))


def create_app(env=os.getenv('FLASK_ENV', 'production')):
    from configs import load_config
    from .blueprints import register_blueprints
    from .errors import register_error_handlers
    from .exts import init_extensions
    from .hooks import hook_hooks

    print(f'\n- - - - - olea [{env}] - - - - -\n')
    app = Flask(__name__)
    app.env = env
    app.config.from_object(load_config(env))

    # configure_logger(app)
    register_error_handlers(app)
    init_extensions(app)
    register_blueprints(app)
    hook_hooks(app)

    return app
