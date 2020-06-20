from flask_jsonform import BaseForm
from jsonform.conditions import In
from jsonform.fields import EnumField, SetField, StringField

from models import Dep, Pit


class InDep(BaseForm):
    dep = SetField(EnumField(Dep))
    states = SetField(EnumField(Pit.S),
                      condition=In(Pit.S.working, Pit.S.past_due, Pit.S.delayed, Pit.S.auditing))


class Search(BaseForm):
    deps = SetField(EnumField(Dep), optional=True, default={Dep.ae, Dep.au, Dep.ps})
    states = SetField(EnumField(Pit.S), optional=True)
    pink_id = StringField(optional=True)


class Checks(BaseForm):
    deps = SetField(EnumField(Dep), optional=True, default={Dep.ae, Dep.au, Dep.ps})


class Submit(BaseForm):
    share_id = StringField()


class ForceSubmit(BaseForm):
    token = StringField()
