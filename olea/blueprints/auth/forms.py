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


class AlterDuck(BaseForm):
    add = DictField(StringField(), SetField(StringField()), optinal=True)
    remove = SetField(StringField(), optinal=True)

    def check(self):
        if self.test_empty('add') and self.test_empty('remove'):
            raise FormError('empty form')
        if I := self.add & self.remove:
            raise FormError(f'intersection between add and remove: {I}')


class AlterScopes(BaseForm):
    class Method(enum.Emun):
        diff = 'merge diffferences'
        full = 'overwrite full set'

    method = EnumField(AlterScopes.Method)
    positive = SetField(StringField(), optinal=True)
    negative = SetField(StringField(), optinal=True)

    def check(self):
        if self.method == AlterScopes.Method.full:
            if self.test_empty('positive'):
                raise FormError('empty form')
        else:
            if self.test_empty('positive') and self.test_empty('negative'):
                raise FormError('empty form')
            if I := self.positive & self.negative:
                raise FormError(f'intersection between + and -: {I}')
