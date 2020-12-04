import pickle
from math import log2
from typing import Set

from core.errors import WeekPwd
from core.utils import FromConf

common_pwd: Set[str] = set()
with FromConf.load('PWDDB_PATH').open('rb') as f:
    common_pwd = pickle.load(f)


def is_common_pwd(pwd: str) -> bool:
    return pwd in common_pwd


# modified from
# https://github.com/kolypto/py-password-strength/blob/master/password_strength/stats.py

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
    if is_common_pwd(pwd):
        raise WeekPwd(rsn=WeekPwd.Rsn.common)

    strength = measure_strength(pwd)
    if strength < WEAK_MAX:
        raise WeekPwd(rsn=WeekPwd.Rsn.strength, strength=strength)
