import random
from base64 import _b85alphabet, b85encode


def random_b85(k):
    # 20 for 128bit
    return ''.join(random.choices(_b85alphabet, k=k))
