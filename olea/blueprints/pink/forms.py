from flask_jsonform import BaseForm, FieldError, FormError
from jsonform.conditions import InRange
from jsonform.fields import EnumField, IntegerField, ListField, StringField

from models import Dep

from .custom_conditions import Email
from .text_tools import measure_width


class UpdateInfo(BaseForm):
    qq = IntegerField(optional=True,
                      condition=InRange(min_val=100_000_000, max_val=10_000_000_000))
    other = ListField(StringField(), optional=True)
    email = StringField(optional=True, condition=Email())

    def check(self):
        if self.test_empty('qq') and self.test_empty('other'):
            raise FormError('must provide at least one contact method')


class Create(BaseForm):
    name = StringField()
    qq = IntegerField(optional=True,
                      condition=InRange(min_val=100_000_000, max_val=10_000_000_000))
    other = ListField(StringField(), optional=True)
    email = StringField(condition=Email())
    deps = ListField(EnumField(Dep))

    def check_name(self, field):
        if measure_width(field.data) > 16:
            raise FieldError('name is too long')

    def check(self):
        if self.test_empty('qq') and self.test_empty('other'):
            raise FormError('must provide at least one contact method')


class SetPwd(BaseForm):
    pwd = StringField()
