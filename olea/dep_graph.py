from datetime import timedelta
from typing import Dict, Set

from singleton import Singleton

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

    def __init__(self):
        for dep, dependences in self.RULE.items():
            # check circular dependence
            # cannot use dfs
            chain = self.RULE.get(dep, set())
            while True:
                chain_len = len(chain)
                for dep_ in chain:
                    chain = chain | self.RULE.get(dep_, set())
                if len(chain) == chain_len:
                    break
            if dep in chain:
                raise Exception('Circular Dependence')

            # build inverse rule
            for dep_ in dependences:
                if dep_ in self.I_RULE:
                    self.I_RULE[dep_].add(dep)
                else:
                    self.I_RULE[dep_] = {dep}

    def is_depend_on(self, own, target):
        dependencies = {}
        for dep in set(own):
            dependencies = dependencies | self.RULE[dep]
        return target in dependencies

    @staticmethod
    def _dfs(dict_, key):
        result = dict_.get(key, set())
        for key_ in result:
            result = result | _dfs(key_)
        return result

    def get_all_dependents(self, dep):
        return self._dfs(self.I_RULE, dep)

    def get_all_dependences(self, dep):
        return self._dfs(self.RULE, dep)

    def get_duration(self, dep):
        local_max = timedelta(seconds=0)
        for dep_ in self.RULE.get(dep, set()):
            if (time := self.get_duration(dep_)) > local_max:
                local_max = time
        return self.DURATION[dep] + local_max

    def get_start_time(self, base, dep):
        return base + self.get_duration(dep) - self.DURATION[dep]
