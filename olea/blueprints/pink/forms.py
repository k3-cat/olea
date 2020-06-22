import enum

from flask_jsonapi import BaseForm, Container
from json_api.fields import String, Set, Enum, Integer, List, Boolean
from json_api.conditions import InRange

from models import Dep

from .text_tools import measure_width


class SetEmail(BaseForm):
    token = String


class Search(BaseForm):
    deps = Set(Enum(Dep), default=set([dep.name for dep in Dep]))
    name = String(required=False)
    qq = Integer(required=False)


class UpdateInfo(BaseForm):
    qq = Integer(required=False, condition=InRange(min_val=100_000_000, max_val=10_000_000_000))
    other = String(required=False)

    def check(self):
        if self.test_empty('qq') and self.test_empty('other'):
            raise FormError('must provide at least one contact method')


class AssignToken(BaseForm):
    deps = Set(Enum(Dep))
    amount = Integer(condition=InRange(min_val=1))


class SignUp(BaseForm):
    name = String
    qq = Integer(required=False, condition=InRange(min_val=100_000_000, max_val=10_000_000_000))
    other = List(String, required=False)
    token_dep = String
    token_email = String

    def check_name(self, field):
        if measure_width(field.data) > 16:
            raise FieldError('name is too long')

    def check(self):
        if self.test_empty('qq') and self.test_empty('other'):
            raise FormError('must provide at least one contact method')


class SearchDuck():
    pink_id = String(required=False)
    nodes = Set(String, required=False)
    scopes = Set(String, required=False)
    allow = Boolean(required=False)


class AlterDuck(BaseForm):
    class Duck(Container):
        node = String
        allow = Boolean(required=False)
        scopes = Set(String)

    add = List(Duck, required=False)
    remove = Set(String, required=False)

    def check(self):
        if self.test_empty('add') and self.test_empty('remove'):
            raise FormError('empty form')
        if I := self.add & self.remove:
            raise FormError(f'intersection between add and remove: {I}')


class AlterScopes(BaseForm):
    class Method(enum.Enum):
        diff = 'merge diffferences'
        full = 'overwrite full set'

    method = Enum(Method)
    positive = Set(String(), required=False)
    negative = Set(String(), required=False)

    def check(self):
        if self.method == AlterScopes.Method.full:
            if self.test_empty('positive'):
                raise FormError('empty form')
        else:
            if self.test_empty('positive') and self.test_empty('negative'):
                raise FormError('empty form')
            if I := self.positive & self.negative:
                raise FormError(f'intersection between + and -: {I}')
