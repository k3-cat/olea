from flask_jsonapi import BaseForm
from json_api.fields import Set, String, Enum, DateTime
from models import Ann, Dep


class Search(BaseForm):
    deps = Set(Enum(Dep), default=set([dep.name for dep in Dep]))


class Post(BaseForm):
    level = Enum(Ann.L)
    deps = Set(Enum(Dep))
    exp = DateTime
    content = String


class Edit(BaseForm):
    content = String
