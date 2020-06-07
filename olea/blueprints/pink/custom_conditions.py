from jsonform.conditions import BaseCondition
from jsonform.errors import FieldError

from olea.exts import mailgun


class Email(BaseCondition):
    def check(self, field):
        result = mailgun.check_adr(field.data)
        if result['risk'] in ('high', 'medium'):
            raise FieldError(f'{result["risk"]}-risk|{", ".join(result["reason"])}')
