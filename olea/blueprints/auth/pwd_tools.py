import pickle
import random
from math import log2
from typing import Set

from flask import current_app
from singleton import Singleton

from olea.errors import WeekPwd


class CommonPwd(metaclass=Singleton):
    common_pwd: Set[str] = set()

    def __init__(self):
        with current_app.config['PWDDB_PATH'].open('rb') as f:
            self.common_pwd = pickle.load(f)

    def is_common_pwd(self, pwd: str) -> bool:
        return pwd in self.common_pwd


# about pwd stength
# modified from
# https://github.com/kolypto/py-password-strength/blob/master/password_strength/stats.py

# Here, we want a function that:
# 1. f(x)=0.333 at x=weak_bits
# 2. f(x)=0.950 at x=weak_bits*3 (great estimation for a perfect password)
# 3. f(x) is almost linear in range{weak_bits .. weak_bits*2}: doubling the bits should double the strength
# 4. f(x) has an asymptote of 1.0 (normalization)

# First, the function:
#       f(x) = 1 - (1-WEAK_MAX)*2^( -k*x)

# Now, the equation:
#       f(HARD_BITS) = HARD_VAL
#       1 - (1-WEAK_MAX)*2^( -k*HARD_BITS) = HARD_VAL
#                        2^( -k*HARD_BITS) = (1 - HARD_VAL) / (1-WEAK_MAX)
#       k = -log2((1 - HARD_VAL) / (1-WEAK_MAX)) / HARD_BITS

WEAK_BITS: int = 30
WEAK_MAX: float = 1 / 3
HARD_BITS: int = WEAK_BITS * 3
HARD_VAL: float = 0.950
K: float = -log2((1 - HARD_VAL) / (1 - WEAK_MAX)) / HARD_BITS


def measure_strength(pwd: str) -> float:
    ''' Get password strength as a number normalized to range {0 .. 1}.
    Normalization is done in the following fashion:
    1. If entropy_bits <= weak_bits   -- linear in range{0.0 .. 0.33} (weak)
    2. If entropy_bits <= weak_bits*2 -- almost linear in range{0.33 .. 0.66} (medium)
    3. If entropy_bits > weak_bits*3  -- asymptotic towards 1.0 (strong)
    '''

    # https://en.wikipedia.org/wiki/Password_strength
    entropy_bits: float = len(pwd) * log2(len(set(pwd)))

    if entropy_bits <= WEAK_BITS:
        return WEAK_MAX * entropy_bits / WEAK_BITS

    return 1 - (1 - WEAK_MAX) * pow(2, -K * (entropy_bits - WEAK_BITS))  # with offset


def check_pwd(pwd):
    if CommonPwd().is_common_pwd(pwd):
        raise WeekPwd(rsn=WeekPwd.Rsn.common)
    strength = measure_strength(pwd)
    if strength < WEAK_MAX:
        raise WeekPwd(rsn=WeekPwd.Rsn.strength, strength=strength)
