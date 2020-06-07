import os
from base64 import b85encode


def random_b85(length):
    return b85encode(os.urandom(length)).encode('utf-8')
