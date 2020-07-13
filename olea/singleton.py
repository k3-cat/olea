__all__ = ['db', 'fjson', 'ip2loc', 'onedrive', 'redis', 'pat', 'sendgrid', 'sqlogger']

from flask_json import FlaskJSON
from flask_redis import FlaskRedis

from flask_sendgrid import SendGrid
from flask_sqlalchemy_ import SQLAlchemy
from ip2loc import IP2Loc
from onedrive import OneDrive
from pypat import Pat
from sqlalchemy_ import BaseModel
from sqlogger import SQLogger

db = SQLAlchemy(Model=BaseModel)
fjson = FlaskJSON()
ip2loc = IP2Loc()
onedrive = OneDrive()
pat = Pat()
redis = FlaskRedis()
sendgrid = SendGrid()
sqlogger = SQLogger()
