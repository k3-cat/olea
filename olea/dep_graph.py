from datetime import timedelta
from typing import Dict, Set

from singleton import Singleton
from collections import deque

from models import Dep


class DepGraph(metaclass=Singleton):
    RULE: Dict[Dep, Set[Dep]] = {
        Dep.ae: {Dep.au, Dep.ps},
    }
    I_RULE: Dict[Dep, Set[Dep]] = dict()

    DURATION = {
        Dep.au: timedelta(days=7),
        Dep.ps: timedelta(days=7),
        Dep.ae: timedelta(days=14),
    }

    def __new__(cls):
        for dep, dependences in cls.RULE.items():
            # check circular dependence
            queue = deque([dep])
            chain = set()
            while queue:
                deps = cls.RULE.get(queue.pop_left(), set())
                queue.extend(deps)
                chain = chain | deps
                if dep in chain:
                    raise Exception('Circular Dependence')

            # build inverse rule
            for _dep in dependences:
                if _dep in cls.I_RULE:
                    cls.I_RULE[_dep].add(dep)
                else:
                    cls.I_RULE[_dep] = {dep}

        return super().__new__(cls)

    def is_depend_on(self, own, target):
        dependencies = {}
        for dep in set(own):
            dependencies = dependencies | self.RULE[dep]
        return target in dependencies

    def get_duration(self, dep):
        local_max = timedelta(seconds=0)
        for _dep in self.RULE.get(dep, set()):
            if (time := self.get_duration(_dep)) > local_max:
                local_max = time
        return self.DURATION[dep] + local_max

    def get_start_time(self, base, dep):
        return base + self.get_duration(dep) - self.DURATION[dep]
