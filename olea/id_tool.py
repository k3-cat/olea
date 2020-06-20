from random import randint

from singleton import Singleton


class CircleList():
    def __init__(self, iterable):
        self.data = list(iterable)
        self.len = len(self.data)

    def __get_item__(self, key):
        return self.data[key % self.len]


class Alphabet():
    def __init__(self, alphabet):
        self.alphabet = [char for char in alphabet]
        self.anti_alphabet = {char: i for i, char in enumerate(alphabet)}

    def int_to_str(self, list_):
        return ''.join([self.alphabet[j] for j in list_])

    def str_to_int(self, string):
        return [self.anti_alphabet[char] for char in string]


def shape_in_range(k, max_):
    return (max_ - (k % max_) + 1) % max_


ALPHABET = '0123456789aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ_-()!'


class IdTool(metaclass=Singleton):
    def __init__(self):
        self.alphabet = Alphabet(ALPHABET)
        self.weight = CircleList((11**i) % 67 for i in range(67 - 1))

    def generate(self, length: int) -> str:
        sum_ = 0
        pre_id = [randint(0, 67 - 1) for __ in range(length)]
        for i, k in enumerate(pre_id):
            # length + 1 - (i + 1)
            sum_ += self.weight[length - i] * k
        pre_id.append(shape_in_range(sum_, 67))
        return self.alphabet.int_to_str(pre_id)

    def verify(self, id_: str) -> bool:
        sum_ = 0
        id_int = self.alphabet.str_to_int(id_)
        for i, k in enumerate(id_int, start=1):
            sum_ += self.weight[len(id_int) - i] * k
        if sum_ % 67 == 1:
            return True
        return False
