__all__ = ['FromConf', 'random_b85']

import random
from typing import Any

# from base64 import _b85alphabet
_b85alphabet = ('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                'abcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~')


def random_b85(k):
    # 20 for 128bit
    return ''.join(random.choices(_b85alphabet, k=k))


class FromConf():
    app: Any = None

    @classmethod
    def init_app(cls, app):
        cls.app = app

    def __new__(cls, name) -> Any:
        return cls.app.config[name]
