from abc import ABC, abstractmethod

from .errors import FieldError

__all__ = ['BaseLogicOpt', 'All', 'Any']


class BaseLogicOpt():
    def __init__(self, *conditions, simple=False):
        self.simple = simple
        self.conditions = conditions

    @abstractmethod
    def check(self, field):
        pass


class All(BaseLogicOpt):
    def check(self, field):
        e = FieldError()
        for condition in self.conditions:
            try:
                condition.check(field)
            except FieldError as e_:
                e.extend(e_.error)
                if self.simple:
                    break
        if e:
            raise e


class Any(BaseLogicOpt):
    def check(self, field):
        e = FieldError()
        count = 0
        for condition in self.conditions:
            try:
                condition.check(field)
                if self.simple:
                    break
            except FieldError as e_:
                e.extend(e_.error)
                count += 1
        if count == len(self.conditions):
            raise e
