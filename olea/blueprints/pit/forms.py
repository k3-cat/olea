from flask_jsonform import BaseForm
from jsonform.conditions import In
from jsonform.fields import EnumField, SetField, StringField

from models import Dep, Pit


class InDep(BaseForm):
    dep = SetField(EnumField(Dep))
    states = SetField(EnumField(Pit.State),
                      condition=In(Pit.State.working, Pit.State.past_due, Pit.State.delayed,
                                   Pit.State.auditing))


class Search(BaseForm):
    deps = SetField(EnumField(Dep), optional=True, default={Dep.ae, Dep.au, Dep.ps})
    states = SetField(EnumField(Pit.State), optional=True)
    pink_id = StringField(optional=True)


class Checks(BaseForm):
    deps = SetField(EnumField(Dep), optional=True, default={Dep.ae, Dep.au, Dep.ps})


class Submit(BaseForm):
    share_id = StringField()


class ForceSubmit(BaseForm):
    token = StringField()
