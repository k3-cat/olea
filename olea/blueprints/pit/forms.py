from flask_jsonform import BaseForm
from jsonform.fields import EnumField, SetField, StringField

from models import Dep, Pit


class Search(BaseForm):
    deps = SetField(EnumField(Dep), optional=True)
    states = SetField(EnumField(Pit.State), optional=True)
    pink_id = StringField(optional=True)


class Submit(BaseForm):
    share_id = StringField()


class ForceSubmit(BaseForm):
    token = StringField()
