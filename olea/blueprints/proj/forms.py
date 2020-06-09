from flask_jsonform import BaseForm, FieldError
from jsonform.fields import EnumField, ListField, StringField

from models import Dep, ProjType

from .custom_fields import RolesField

__all__ = ['Create', 'FullCreate', 'ModifyRoles']


class FullCreate(BaseForm):
    base = StringField()
    type = EnumField(ProjType)
    suff = StringField()
    leader = StringField()


class Create(BaseForm):
    base = StringField()
    type = EnumField(ProjType)

    def check_type(self, field):
        if field not in (ProjType.doc, ProjType.sub):
            raise FieldError(f'type, {field} is not acceptable')


class ModifyRoles(BaseForm):
    add = RolesField()
    remove = ListField(StringField)

    def check_add(self, field):
        diff = field.data.keys() - {Dep.au, Dep.ps, Dep.ae}
        if diff:
            raise FieldError(f'currently does not allow to add roles into these deps: {diff}')
