import enum

from flask_jsonform import BaseForm, FormError
from jsonform.fields import EnumField, SetField, StringField


class Login(BaseForm):
    name = StringField()
    pwd = StringField()
    device_id = StringField()


class Refresh(BaseForm):
    id = StringField()
    key = StringField()
    device_id = StringField()


class GrantedDuck(BaseForm):
    pink_id = StringField()
    node = StringField()
    scopes = SetField(StringField())


class AlterScopes(BaseForm):
    class Method(enum.Emun):
        diff = 'merge diffferences'
        full = 'overwrite full set'

    method = EnumField(AlterScopes.Method)
    positive = SetField(StringField())
    negative = SetField(StringField(), optinal=True)

    def check(self):
        if self.test_empty('positive') and self.test_empty('negative') \
            and (I := self.positive & self.negative):
            raise FormError(f'intersection between + and -: {I}')
