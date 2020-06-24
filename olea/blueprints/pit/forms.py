from flask_jsonapi import BaseForm
from json_api.conditions import In
from json_api.fields import Enum, Set, String

from models import Dep, Pit


class InDep(BaseForm):
    dep = Set(Enum(Dep))
    status_set = Set(Enum(Pit.S),
                     condition=In(Pit.S.working, Pit.S.past_due, Pit.S.delayed, Pit.S.auditing))


class Search(BaseForm):
    deps = Set(Enum(Dep), default={Dep.ae, Dep.au, Dep.ps})
    status_set = Set(Enum(Pit.S), required=False)
    pink_id = String(required=False)


class Checks(BaseForm):
    deps = Set(Enum(Dep), default={Dep.ae, Dep.au, Dep.ps})


class Submit(BaseForm):
    share_id = String


class ForceSubmit(BaseForm):
    token = String
