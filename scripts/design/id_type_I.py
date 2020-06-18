import random
import sys
from pathlib import Path


def test(id_tool):
    count_1 = 0
    count_2 = 0
    for __ in range(1_000_000):
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


if __name__ == '__main__':
    PROJ_ROOT = (Path(__file__).parents[2])
    sys.path.append(str(PROJ_ROOT / 'site-packages'))

    from id_tool import IdTool

    id_tool = IdTool()
    test(id_tool)
