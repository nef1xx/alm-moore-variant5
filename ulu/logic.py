"""Исходные и минимизированные F. Только стандартная библиотека Python."""
from itertools import product

INPUTS = tuple(product((0, 1), repeat=4))
FORMAL_F = tuple(product((0, 1), repeat=3))


def bits(values, count):
    values = tuple(values)
    if len(values) != count or any(v not in (0, 1) for v in values):
        raise ValueError(f"Ожидается {count} двоичных значений 0 или 1")
    return tuple(int(v) for v in values)


def original_f(x):
    a, b, c, d = bits(x, 4)
    f1 = ((a and b and d) or (a and c) or (b and not d)
          or (not a and not c and d) or (not a and not b))
    f2 = ((a and b and not c) or (not b and c)
          or (not a and not b) or (not b and not c))
    f3 = ((a and c) or (b and c) or (not a and not c)
          or (not a and not b and c) or (a and b and not c))
    return tuple(map(int, (f1, f2, f3)))


def minimized_f(x):
    a, b, c, d = bits(x, 4)
    f1 = (not a and not b) or (a and c) or (b and not c) or (b and not d)
    f2 = (not b) or (a and not c)
    f3 = (not a) or b or c
    return tuple(map(int, (f1, f2, f3)))


# 0: отрицание, 1: переменная, None: переменная отсутствует.
SELECTED_COVERS = (
    ((0, 0, None, None), (1, None, 1, None),
     (None, 1, 0, None), (None, 1, None, 0)),
    ((None, 0, None, None), (1, None, 0, None)),
    ((0, None, None, None), (None, 1, None, None), (None, None, 1, None)),
)
