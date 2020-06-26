import enum

from flask_jsonapi import BaseForm, Container
from json_api.fields import String, Set, Enum, Integer, List, Boolean
from json_api.conditions import InRange
from json_api.logic_opt import OneOf, Has, If, Properties, Is

from models import Dep

from .text_tools import measure_width


class SetEmail(BaseForm):
    token = String


class Search(BaseForm):
    deps = Set(Enum(Dep), default=set(Dep))
    name = String(required=False)
    qq = Integer(required=False)


class UpdateInfo(BaseForm):
    qq = Integer(required=False, condition=InRange(min_val=100_000_000, max_val=10_000_000_000))
    other = String(required=False)

    _condition = OneOf(Has('qq'), Has('other'))


class AssignToken(BaseForm):
    deps = Set(Enum(Dep))
    amount = Integer(condition=InRange(min_val=1))


class SignUp(BaseForm):
    name = String
    qq = Integer(required=False, condition=InRange(min_val=100_000_000, max_val=10_000_000_000))
    other = List(String, required=False)
    token_dep = String
    token_email = String

    _condition = OneOf(Has('qq'), Has('other'))

    def check_name(self, data):
        if width := measure_width(data) > 16:
            return f'name of width {width} is too long'


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

    _condition = OneOf(Has('add'), Has('remove'))


class AlterScopes(BaseForm):
    class Method(enum.Enum):
        diff = 'merge diffferences'
        full = 'overwrite full set'

    method = Enum(Method)
    positive = Set(String(), required=False)
    negative = Set(String(), required=False)

    _condition = If(
        if_=Properties(method=Is('diff')),
        then_=OneOf(Has('positive'), Has('negative')),
        else_=Has('positive'),
    )
