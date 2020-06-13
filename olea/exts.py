from flask_apscheduler import scheduler
from flask_json import FlaskJSON
from flask_redis import FlaskRedis
from mailgun import MailGun
from onedrive import OneDrive
from sqlalchemy_ import db

fjson = FlaskJSON()
mailgun = MailGun()
onerive = OneDrive()
redis = FlaskRedis()

__all__ = ['db', 'mailgun', 'onerive', 'redis', 'scheduler']


def init_extensions(app):
    db.init_app(app)
    fjson.init_app(app)
    redis.init_app(app)
    scheduler.init_app(app)
    mailgun.init_app(app)
    onerive.init_app(app)

    scheduler.start()
