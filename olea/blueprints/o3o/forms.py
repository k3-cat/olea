from flask_jsonfrom import BaseForm
from jsonform.fields import StringField


class Submit(BaseForm):
    share_id = StringField()


class ForceSubmit(BaseForm):
    token = StringField()


class Pick(BaseForm):
    pink_id = StringField()
