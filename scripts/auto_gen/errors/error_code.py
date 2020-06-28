import random
import string

CHARS = string.digits + string.ascii_uppercase
ERROR_CODE_LEN = 5


def generate_err_code(k=ERROR_CODE_LEN):
    result = []
    for i in range(k - 1):
        result.append(random.randint(0, 35))
    sum_ = 0
    code = ''
    for order in result:
        sum_ += order
        code += CHARS[order]
    code += CHARS[(36 - (sum_ % 36)) % 36]
    return code


def check_err_code(code):
    result = []
    for char in code:
        result.append(CHARS.index(char))
    sum_ = 0
    for order in result:
        sum_ += order
    if sum_ % 36 != 0:
        return False
    return True


if __name__ == '__main__':
    print(generate_err_code())
