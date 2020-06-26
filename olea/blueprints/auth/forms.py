from flask_jsonapi import BaseForm
from json_api.fields import Email, String

from olea.singleton import mailgun


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

    def check_email(self, data):
        result = mailgun.check_adr(data)
        if result['risk'] in ('high', 'medium'):
            return f'{result["risk"]}-risk|{", ".join(result["reason"])}'


class Refresh(BaseForm):
    id = String
    key = String
    device_id = String
