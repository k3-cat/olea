from flask_jsonform import BaseForm
from jsonform.fields import StringField


class Login(BaseForm):
    name = StringField()
    pwd = StringField()
    device_id = StringField()


class Refresh(BaseForm):
    id = StringField()
    key = StringField()
