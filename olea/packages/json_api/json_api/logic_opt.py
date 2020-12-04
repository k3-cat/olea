__all__ = ['Is', 'Type', 'Has', 'Properties', 'Grouping', 'AllOf', 'AnyOf', 'OneOf', 'Not', 'If']

from typing import Any, Dict


class HelperCondition():
    def gen_schema(self, field_type) -> Dict[str, Any]:
        pass


class Is(HelperCondition):
    def __init__(self, value):
        self.value = value

    def gen_schema(self, field_type):
        return {'const': self.value}


class Type(HelperCondition):
    def __init__(self, type_):
        self.type = type_

    def gen_schema(self, field_type):
        return {'type': self.type}


class Has(HelperCondition):
    def __init__(self, *keys):
        self.keys = keys

    def gen_schema(self, field_type):
        return {'required': self.keys}


class Properties(HelperCondition):
    def __init__(self, **properties):
        self.properties = properties

    def gen_schema(self, field_type):
        properties = {}
        for name, condition in self.properties.items():
            properties[name] = condition.gen_schema(field_type, dict())
        return {'properties': properties}


class BaseLogic():
    def gen_schema(self, field_type, schema):
        return schema


class Grouping(BaseLogic):
    def __init__(self, *conditions):
        self.conditions = conditions

    def gen_schema(self, field_type, schema):
        for condition in self.conditions:
            schema = condition.gen_schema(field_type, schema)
        return schema


class Combination(BaseLogic):
    key = ''

    def __init__(self, *conditions):
        self.conditions = conditions

    def gen_schema(self, field_type, schema):
        result = dict()
        for condition in self.conditions:
            result.update(condition.gen_schema(field_type, dict()))
        schema.update({self.key: result})
        return schema


class AnyOf(Combination):
    key = 'anyOf'


class AllOf(Combination):
    key = 'allOf'


class OneOf(Combination):
    key = 'oneOf'


class Not(Combination):
    key = 'not'


class If(BaseLogic):
    def __init__(self, if_: BaseLogic, then_: BaseLogic = None, else_: BaseLogic = None):
        self.if_ = if_
        self.then_ = then_
        self.else_ = else_

    def gen_schema(self, field_type, schema):
        schema.update({
            'if': self.if_.gen_schema(field_type),
            'then': self.then_.gen_schema(field_type),
            'else': self.else_.gen_schema(field_type)
        })
        return schema
