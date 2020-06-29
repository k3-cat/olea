__all__ = ['Create', 'FullCreate', 'ModifyRoles']

from flask_jsonapi import BaseForm, Container
from json_api.conditions import In
from json_api.fields import Enum, List, Set, String
from json_api.logic_opt import Has, OneOf

from models import Dep, Proj


class Search(BaseForm):
    status_set = Set(Enum(Proj.S), required=False)
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
