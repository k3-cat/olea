from flask_apscheduler import scheduler
from flask_json import FlaskJson
from flask_redis import FlaskRedis
from mailgun import MailGun
from onedrive import OneDrive
from pypat import Pat
from sqlalchemy_ import db

fjson = FlaskJson()
mailgun = MailGun()
onerive = OneDrive()
redis = FlaskRedis()

pat = Pat()

__all__ = ['db', 'pat', 'mailgun', 'onerive', 'redis', 'scheduler']


def init_extensions(app):
    db.init_app(app)
    fjson.init_app(app)
    redis.init_app(app)
    scheduler.init_app(app)
    mailgun.init_app(app)
    onerive.init_app(app)

    scheduler.start()
