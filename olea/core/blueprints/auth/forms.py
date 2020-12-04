from flask_jsonapi import BaseForm
from json_api.fields import Email, String


class Login(BaseForm):
    name = String
    pwd = String
    device_id = String


class ForgetPwd(BaseForm):
    name = String
    email = String


class ResetPwd(BaseForm):
    token = String
    pwd = String
    device_id = String


class SetPwd(BaseForm):
    pwd = String
    device_id = String


class VEmail(BaseForm):
    email = Email


class Refresh(BaseForm):
    id = String
    key = String
    device_id = String
