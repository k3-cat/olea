import timeit

from passlib.hash import argon2

timer = timeit.Timer(
    "pwd_hasher.hash('12312312313131231')",
    "pwd_hasher = argon2.using(time_cost=50, memory_cost=1024 * 16, parallelism=2)",
    globals=globals())

print(timer.timeit(10))
