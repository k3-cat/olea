from flask_jsonform import BaseForm
from jsonform.fields import (BooleanField, DateTimeField, EnumField, IntegerField, ListField,
                             SetField, StringField, SubForm)
from models import Ann, Dep


class Search(BaseForm):
    deps = SetField(EnumField(Dep), optional=True)


class Post(BaseForm):
    cat = EnumField(Ann.Cat)
    deps = SetField(EnumField(Dep))
    expired_at = DateTimeField()
    content = StringField()


class Edit(BaseForm):
    content = StringField()
