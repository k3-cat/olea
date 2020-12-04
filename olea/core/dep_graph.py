from collections import deque
from datetime import timedelta
from functools import lru_cache
from typing import Dict, Set

from singleton import Singleton

from models import Dep, Proj
from .utils import FromConf


class DepGraph(metaclass=Singleton):
    __rule: Dict[Proj.C, Dict[Dep, Set[Dep]]] = dict()
    __i_rule: Dict[Proj.C, Dict[Dep, Set[Dep]]] = dict()
    __duration: Dict[Proj.C, Dict[Dep, timedelta]] = dict()

    def __new__(cls):
        def dfs_check(rule, dep, target):
            deps = rule.get(dep, None)
            if not deps:
                return

            if target in deps:
                raise Exception('Circular Dependence')
            for dep_ in deps:
                dfs_check(rule, dep_, target)

        for proj_cat, rule in FromConf.load('RULE'):
            cat = Proj.C[proj_cat]

            if isinstance(rule, str):
                cls.__rule[cat] = cls.__rule[Proj.C[rule]]
                cls.__i_rule[cat] = cls.__i_rule[Proj.C[rule]]

            cls.__rule[cat] = dict()
            cls.__i_rule[cat] = dict()
            for dep, dependencies in rule.items():
                # check circular dependence
                dfs_check(rule, dep, dep)

                dep_set = Set([Dep[dep] for dep in dependencies])
                cls.__rule[cat][Dep[dep]] = dep_set

                # build inverse rule
                for _dep in dep_set:
                    try:
                        cls.__i_rule[cat][_dep].add(dep)
                    except KeyError:
                        cls.__i_rule[cat][_dep] = {dep}

        for proj_cat, duration in FromConf.load('DURATION'):
            cat = Proj.C[proj_cat]

            if isinstance(duration, str):
                cls.__duration[cat] = cls.__duration[Proj.C[duration]]

            cls.__duration[cat].update({Dep[dep]: timedelta for dep, timedelta in duration.items()})

        return super().__new__(cls)

    def is_depend_on(self, cat: Proj.C, own: Set[Dep], target: Dep) -> bool:
        queue = deque(own)
        dependencies: Set[Dep] = set()
        while queue:
            try:
                dependencies = dependencies | self.__rule[cat].get(queue.popleft(), set())
            except KeyError:
                pass

            if target in dependencies:
                return True

        return False

    def get_dependents(self, cat: Proj.C, dep: Dep):
        return self.__i_rule[cat][dep]

    def get_duration(self, cat: Proj.C, dep: Dep):
        return self.__duration[cat][dep]

    @lru_cache
    def get_period(self, cat: Proj.C, dep: Dep):
        local_max = timedelta(seconds=0)
        for _dep in self.__rule[cat].get(dep, set()):
            if (time := self.get_period(cat, _dep)) > local_max:
                local_max = time
        return self.get_duration(cat, dep) + local_max

    def get_start_time(self, cat: Proj.C, base, dep: Dep):
        return base + self.get_period(cat, dep) - self.get_duration(cat, dep)

    def get_finish_time(self, cat: Proj.C, base, dep: Dep):
        return base + self.get_period(cat, dep)
