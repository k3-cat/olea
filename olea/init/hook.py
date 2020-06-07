import datetime
import random
from base64 import _b85alphabet

from sentry_sdk import configure_scope


def hook_hooks(app):
    from flask import g, request

    @app.before_request
    def add_timestamp():
        g.now = datetime.datetime.utcnow()
        g.ref = ''.join(random.choices(_b85alphabet, k=20))
        with configure_scope() as scope:
            scope.set_tag('ref', g.ref)

    @app.after_request
    def check_performance():
        used = datetime.datetime.utcnow() - g.now
        if used.microseconds > 1500:
            print(f'[performance] {request.path} is too slow (1500)')
        elif used.microseconds > 500:
            print(f'[performance] {request.path} is slow (500)')
