import random

# from base64 import _b85alphabet
_b85alphabet = ('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                'abcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~')

__all__ = ['FromConf', 'random_b85']


def random_b85(k):
    # 20 for 128bit
    return ''.join(random.choices(_b85alphabet, k=k))


class FromConf():
    app = None

    @classmethod
    def init_app(cls, app):
        cls.app = app

    def __new__(cls, name):
        return cls.app.config[name]
