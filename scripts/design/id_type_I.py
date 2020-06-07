import random

# ALPHABET = '0123456789aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ_-()!'


class IdTool():
    def __init__(self):
        self.WEIGHT = [(11**i) % 67 for i in range(66)]

    def generate(self, length: int) -> list:
        # random.seed(os.urandom(128))
        pre_id = [random.randint(0, 66) for _ in range(length)]
        result = 0
        for i, a in enumerate(pre_id):
            # length + 1 - (i + 1)
            result += self.WEIGHT[length - i] * a
        pre_id.append((68 - (result % 67)) % 67)
        return pre_id

    def verify(self, id_int: list) -> bool:
        result = 0
        for i, a in enumerate(id_int, start=1):
            result += self.WEIGHT[len(id_int) - i] * a
        if result % 67 == 1:
            return True
        return False


id_tool = IdTool()

count_1 = 0
count_2 = 0
for _ in range(1_000_000):
    id_ = id_tool.generate(12)
    id_1 = id_.copy()
    id_2 = id_.copy()

    k = random.randint(0, 12)
    id_1[k] = 1
    if id_tool.verify(id_1):
        count_1 += 1

    if k == 12:
        k = random.randint(0, 11)
    id_2[k], id_2[k + 1] = id_2[k + 1], id_2[k]
    if id_tool.verify(id_2):
        count_2 += 1

print(count_1 / 1_000_000)
print(count_2 / 1_000_000)
