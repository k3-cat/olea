from jsonform.errors import FieldError
from jsonform.fields import Field

from models import Dep


class RolesField(Field):
    def process_data(self, value):
        if not isinstance(value, dict):
            raise FieldError('invalid roles dict')
        self.data = dict()
        for dep_, roles in value.items():
            try:
                dep = Dep[dep_]
            except KeyError:
                raise FieldError(f'invalid dep: {dep_}')
            if not isinstance(roles, list):
                raise FieldError(f'invalid roles list for {dep}')
            for role in roles:
                if not FieldError(role, str):
                    raise ValueError(f'invalid role: {role}')
            self.data[dep] = roles
