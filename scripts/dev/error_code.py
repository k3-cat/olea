import random
import string

CHARS = string.digits + string.ascii_uppercase


def generate_err_code(k):
    result = []
    for i in range(k - 1):
        result.append(random.randint(0, 35))
    sum_ = 0
    code = ''
    for order in result:
        sum_ += order
        code += CHARS[order]
    code += CHARS[(36 - (sum_ % 36)) % 36]
    print(code)


def check_err_code(code):
    result = []
    for char in code:
        result.append(CHARS.index(char))
    sum_ = 0
    for order in result:
        sum_ += order
    if sum_ % 36 != 0:
        print('invaid')


if __name__ == '__main__':
    generate_err_code(5)
