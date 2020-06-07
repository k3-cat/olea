import os
import random

ALPHABET = '0123456789aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ_-()!'


class IdTool():
    def __init__(self):
        self.ALPHABET = [char for char in ALPHABET]
        self.ANTI_ALPHABET = {char: i for i, char in enumerate(ALPHABET)}
        self.WEIGHT = [(11**i) % 67 for i in range(66)]

    def generate(self, length: int) -> str:
        pre_id = [random.randint(0, 66) for _ in range(length)]
        result = 0
        for i, a in enumerate(pre_id):
            # length + 1 - (i + 1)
            result += self.WEIGHT[length - i] * a
        pre_id.append((68 - (result % 67)) % 67)
        return self._int_to_str(pre_id)

    def verify(self, id_: str):
        id_int = self._str_to_int(id_)
        result = 0
        for i, a in enumerate(id_int, start=1):
            result += self.WEIGHT[len(id_int) - i] * a
        if result % 67 == 1:
            return True
        return False

    def _int_to_str(self, list_):
        return ''.join([self.ALPHABET[j] for j in list_])

    def _str_to_int(self, string):
        return [self.ANTI_ALPHABET[char] for char in string]


id_tool = IdTool()
