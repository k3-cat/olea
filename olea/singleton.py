from flask_json import FlaskJSON
from flask_redis import FlaskRedis
from ip2loc import IP2Loc
from mailgun import MailGun
from onedrive import OneDrive
from pypat import Pat
from sqlalchemy_ import BaseModel, SQLAlchemy

__all__ = ['db', 'fjson', 'ip2loc,' 'mailgun', 'onedrive', 'redis', 'pat']

db = SQLAlchemy(Model=BaseModel)
fjson = FlaskJSON()
ip2loc = IP2Loc()
mailgun = MailGun()
onedrive = OneDrive()
redis = FlaskRedis()
pat = Pat()