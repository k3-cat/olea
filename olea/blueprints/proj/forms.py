from flask_jsonapi import BaseForm, Container
from json_api.fields import List, Enum, Set, String
from json_api.conditions import In
from json_api.logic_opt import OneOf, Has

from models import Dep, Proj

__all__ = ['Create', 'FullCreate', 'ModifyRoles']


class Search(BaseForm):
    states = Set(Enum(Proj.S), required=False)
    cats = Set(Enum(Proj.C), required=False)


class FullCreate(BaseForm):
    base = String
    cat = Enum(Proj.C)
    suff = String
    leader = String


class Create(BaseForm):
    base = String
    cat = Enum(Proj.C, condition=In(Proj.C.doc, Proj.C.sub))


class ModifyRoles(BaseForm):
    class Role(Container):
        dep = Enum(Dep, condition=In(Dep.au, Dep.ps, Dep.ae))
        name = String
        note = String

    add = List(Role, required=False)
    remove = Set(String(), required=False)

    _condition = OneOf(Has('add'), Has('remove'))


class Finish(BaseForm):
    url = String


class Pick(BaseForm):
    pink_id = String


class PostChat(BaseForm):
    reply_to_id = String
    content = String


class Chats(BaseForm):
    chats = Set(String)


class Chat(BaseForm):
    content = String
