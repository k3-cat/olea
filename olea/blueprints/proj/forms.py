from flask_jsonform import BaseForm, FormError
from jsonform.fields import DictField, EnumField, SetField, StringField

from models import Dep, Proj

__all__ = ['Create', 'FullCreate', 'ModifyRoles']


class Search(BaseForm):
    states = SetField(EnumField(Proj.S), optional=True)
    cats = SetField(EnumField(Proj.C), optional=True)


class FullCreate(BaseForm):
    base = StringField()
    cat = EnumField(Proj.C)
    suff = StringField()
    leader = StringField()


class Create(BaseForm):
    base = StringField()
    cat = EnumField(Proj.C)

    def check_cat(self, field):
        if field not in (Proj.C.doc, Proj.C.sub):
            raise FormError(f'cat, {field} is not acceptable')


class ModifyRoles(BaseForm):
    # TODO: add note
    add = DictField(EnumField(Dep), SetField(StringField()), optional=True)
    remove = SetField(StringField(), optional=True)

    def check_add(self, field):
        if self.test_empty('add') and self.test_empty('remove'):
            raise FormError('empty form')
        if diff := field.data.keys() - {Dep.au, Dep.ps, Dep.ae}:
            raise FormError(f'currently does not allow to add roles into these deps: {diff}')


class Finish(BaseForm):
    url = StringField()


class Pick(BaseForm):
    pink_id = StringField()


class PostChat(BaseForm):
    reply_to_id = StringField()
    content = StringField()


class Chats(BaseForm):
    chats = SetField(StringField())


class Chat(BaseForm):
    content = StringField()
