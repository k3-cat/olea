import enum

from flask_jsonform import BaseForm, FormError
from jsonform.fields import DictField, EnumField, SetField, StringField


class Login(BaseForm):
    name = StringField()
    pwd = StringField()
    device_id = StringField()


class ForgetPwd(BaseForm):
    name = StringField()
    email = StringField()


class ResetPwd(BaseForm):
    token = StringField()
    pwd = StringField()


class SetPwd(BaseForm):
    pwd = StringField()


class Refresh(BaseForm):
    id = StringField()
    key = StringField()
    device_id = StringField()
