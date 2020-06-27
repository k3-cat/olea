from collections import deque
from datetime import timedelta
from functools import lru_cache
from typing import Dict, Set

from singleton import Singleton

from models import Dep
from olea.utils import FromConf


class DepGraph(metaclass=Singleton):
    RULE: Dict[Dep, Set[Dep]] = FromConf('RULE')
    I_RULE: Dict[Dep, Set[Dep]] = dict()
    DURATION = FromConf('DURATION')

    def __new__(cls):
        def dfs_check(dep, target):
            deps = cls.RULE.get(dep, None)
            if not deps:
                return

            if target in deps:
                raise Exception('Circular Dependence')
            for dep_ in deps:
                dfs_check(dep_, target)

        for dep, dependences in cls.RULE.items():
            # check circular dependence
            dfs_check(dep, dep)

            # build inverse rule
            for _dep in dependences:
                try:
                    cls.I_RULE[_dep].add(dep)
                except KeyError:
                    cls.I_RULE[_dep] = {dep}

        return super().__new__(cls)

    def is_depend_on(self, own: Set[Dep], target: Dep) -> bool:
        queue = deque(own)
        dependencies: Set[Dep] = set()
        while queue:
            dependencies = dependencies | self.RULE.get(queue.popleft(), set())
            if target in dependencies:
                return True
        return False

    @lru_cache
    def get_duration(self, dep):
        local_max = timedelta(seconds=0)
        for _dep in self.RULE.get(dep, set()):
            if (time := self.get_duration(_dep)) > local_max:
                local_max = time
        return self.DURATION[dep] + local_max

    def get_start_time(self, base, dep):
        return base + self.get_duration(dep) - self.DURATION[dep]

    def get_finish_time(self, base, dep):
        return base + self.get_duration(dep)
