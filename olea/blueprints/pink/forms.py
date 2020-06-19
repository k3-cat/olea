import enum

from flask_jsonform import BaseForm, FieldError, FormError, JsonForm
from jsonform.conditions import InRange
from jsonform.fields import (BooleanField, DictField, EnumField, IntegerField, ListField, SetField,
                             StringField, SubForm)

from models import Dep

from .text_tools import measure_width


class SetEmail(BaseForm):
    token = StringField()


class Search(BaseForm):
    deps = SetField(EnumField(Dep), optional=True)
    name = StringField(optional=True)
    qq = IntegerField(optional=True)


class UpdateInfo(BaseForm):
    qq = IntegerField(optional=True, condition=InRange(min_val=100_000_000, max_val=10_000_000_000))
    other = ListField(StringField(), optional=True)

    def check(self):
        if self.test_empty('qq') and self.test_empty('other'):
            raise FormError('must provide at least one contact method')


class AssignToken(BaseForm):
    deps = SetField(EnumField(Dep))
    amount = IntegerField()


class SignUp(BaseForm):
    name = StringField()
    qq = IntegerField(optional=True, condition=InRange(min_val=100_000_000, max_val=10_000_000_000))
    other = ListField(StringField(), optional=True)
    token_dep = StringField()
    token_email = StringField()

    def check_name(self, field):
        if measure_width(field.data) > 16:
            raise FieldError('name is too long')

    def check(self):
        if self.test_empty('qq') and self.test_empty('other'):
            raise FormError('must provide at least one contact method')


class SearchDuck():
    pink_id = StringField(optional=True)
    nodes = SetField(StringField(), optional=True)
    scopes = SetField(StringField(), optional=True)
    allow = BooleanField(optional=True)


class Duck(JsonForm):
    allow = BooleanField(optional=True)
    scopes = SetField(StringField())


class AlterDuck(BaseForm):
    add = DictField(StringField(), SubForm(Duck()), optional=True)
    remove = SetField(StringField(), optional=True)

    def check(self):
        if self.test_empty('add') and self.test_empty('remove'):
            raise FormError('empty form')
        if I := self.add & self.remove:
            raise FormError(f'intersection between add and remove: {I}')


class AlterScopes(BaseForm):
    class Method(enum.Enum):
        diff = 'merge diffferences'
        full = 'overwrite full set'

    method = EnumField(AlterScopes.Method)
    positive = SetField(StringField(), optional=True)
    negative = SetField(StringField(), optional=True)

    def check(self):
        if self.method == AlterScopes.Method.full:
            if self.test_empty('positive'):
                raise FormError('empty form')
        else:
            if self.test_empty('positive') and self.test_empty('negative'):
                raise FormError('empty form')
            if I := self.positive & self.negative:
                raise FormError(f'intersection between + and -: {I}')
