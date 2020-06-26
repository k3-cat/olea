import random

# from base64 import _b85alphabet
_b85alphabet = ('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                'abcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~')

__all__ = ['FromConf', 'random_b85']


def random_b85(k):
    # 20 for 128bit
    return ''.join(random.choices(_b85alphabet, k=k))


class FromConf():
    def __init__(self, name):
        self.name = name

    def bind(self, app):
        return app.config[self.name]
