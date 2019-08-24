import time
from typing import Any, Tuple


def a(n: int):
    l = [0] * n
    for i in range(n):
        l[i] = 1


def b(n: int):
    l = [0] * n
    l[0:n] = [1] * n


times = 1000
size = 1000


funcs = (
    a, b
)


def bench(f: callable, times: int, args: Tuple[Any]):
    start = time.time()
    for _ in range(times):
        f(*args)
    duration = time.time() - start
    return duration


for f in funcs:
    print(bench(f, times, (size, )))
