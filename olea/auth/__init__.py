__all__ = ['allow_anonymous', 'check_opt_duck', 'check_scopes', 'opt_perm', 'perm']

from flask import request

from .authentication import _anonymous_paths, _check_lemon, allow_anonymous
from .authorization import check_opt_duck, check_scopes
from .authorization import optional_permission as opt_perm
from .authorization import permission_required as perm


def init_app(app):
    @app.before_request
    def login():
        if request.path not in _anonymous_paths:
            _check_lemon()
