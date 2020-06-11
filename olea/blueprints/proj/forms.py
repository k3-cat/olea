from flask_jsonform import BaseForm, FormError
from jsonform.fields import DictField, EnumField, SetField, StringField

from models import Dep, Proj

__all__ = ['Create', 'FullCreate', 'ModifyRoles']


class Search(BaseForm):
    states = SetField(EnumField(Proj.State), optinal=True)
    types = SetField(EnumField(Proj.Type), optinal=True)


class FullCreate(BaseForm):
    base = StringField()
    type = EnumField(Proj.Type)
    suff = StringField()
    leader = StringField()


class Create(BaseForm):
    base = StringField()
    type = EnumField(Proj.Type)

    def check_type(self, field):
        if field not in (Proj.Type.doc, Proj.Type.sub):
            raise FormError(f'type, {field} is not acceptable')


class ModifyRoles(BaseForm):
    add = DictField(EnumField(Dep), SetField(StringField()), optinal=True)
    remove = SetField(StringField(), optinal=True)

    def check_add(self, field):
        if self.test_empty('add') and self.test_empty('remove'):
            raise FormError('empty form')
        if diff := field.data.keys() - {Dep.au, Dep.ps, Dep.ae}:
            raise FormError(f'currently does not allow to add roles into these deps: {diff}')
