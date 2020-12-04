__all__ = ['SQLogger']

from flask import g, request

from .logger import Logger


class SQLogger():
    def __init__(self, app=None):
        self.logger = None
        self.user_key = ''

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.logger = Logger(app.config['SQLOGGER_DIR'])
        self.user_key = app.config['SQLOGGER_USER_KEY']

    def log(self, level, info):
        g.log = (level, info)

    def _log(self, response):
        if not (log := g.get('log', None)):
            return
        level, info = log
        if not (user := g.get(self.user_key, None)):
            user = request.remote_addr
        if request.method == 'POST':
            data = request.get_json()
        elif request.method == 'GET':
            data = request.args

        self.logger.log(ref=g.ref,
                        timestamp=g.now,
                        endpoint=request.endpoint,
                        user=user,
                        level=level,
                        info=info,
                        request=data,
                        response=response)
