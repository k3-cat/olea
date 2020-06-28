from .auth_fail import (AccessDenied, AccountDeactivated, InvalidAccessToken, InvalidCredential,
                        InvalidRefreshToken, PermissionDenied)
from .bad_opt import (DoesNotMeetRequirements, InvalidReply, InvalidSource, NotQualifiedToPick,
                      PitStatusLocked, ProjMetaLocked, RoleIsTaken, UnallowedType, WeekPwd)
from .base_error import BaseError
from .common_enums import Dep
from .data_conflict import DuplicatedRecord, FileExist, FileVerConflict, RecordNotFound

__all__ = [
    'AccessDenied', 'AccountDeactivated', 'BaseError', 'DoesNotMeetRequirements',
    'DuplicatedRecord', 'FileExist', 'FileVerConflict', 'InvalidAccessToken', 'InvalidCredential',
    'InvalidRefreshToken', 'InvalidReply', 'InvalidSource', 'NotQualifiedToPick',
    'PermissionDenied', 'PitStatusLocked', 'ProjMetaLocked', 'RecordNotFound', 'RoleIsTaken',
    'UnallowedType', 'WeekPwd', 'register_error_handlers'
]


def register_error_handlers(app):
    from flask_json import json_response

    # - - - - - - - - - - - - - - - - - - - - - - -
    @app.errorhandler(BaseError)
    def handle_olea_exceptions(e: BaseError):
        return json_response(status_=e.http_code, data_=e)

    # - - - - - - - - - - - - - - - - - - - - - - -
    from sentry_sdk import init as sentry_init
    from sentry_sdk.integrations import flask, redis, sqlalchemy

    if not app.config.get('IGNORE_ERRORS', False):
        sentry_init(dsn=app.config['SENTRY_DSN'],
                    integrations=[
                        flask.FlaskIntegration(),
                        sqlalchemy.SqlalchemyIntegration(),
                        redis.RedisIntegration(),
                    ],
                    traces_sample_rate=0.2)
