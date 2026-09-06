"""Независимый интерпретатор исходных 13 пунктов и ЛСА.

Он не вызывает next_state или функции возбуждения. Проверки между двумя
операторными вершинами используют один снимок F на текущем такте.
"""
from .logic import bits

SOURCE = {
    1: 2, 2: {'f': 2, 'eq': 1, 'yes': 2, 'no': 3}, 3: 4, 4: 5,
    5: {'f': 2, 'eq': 0, 'yes': 9, 'no': 6},
    6: {'f': 3, 'eq': 1, 'yes': 10, 'no': 7},
    7: {'f': 1, 'eq': 0, 'yes': 11, 'no': 8},
    8: 10, 9: 10, 10: 11, 11: 12,
    12: {'f': 1, 'eq': 0, 'yes': 5, 'no': 13},
}
OP_STATE = {3: 1, 4: 2, 9: 3, 10: 4, 11: 5}
AFTER_STATE = {0: 2, 1: 4, 2: 5, 3: 10, 4: 11, 5: 12, 6: 13}
LSA = [
    ['down', 1], ['A', 1, 2], ['up', 1], ['B', 1, 3], ['B', 2, 4],
    ['down', 2], ['A', 2, 5], ['up', 3], ['A', 3, 6], ['up', 4],
    ['A', 4, 7], ['up', 5], ['up', 6, 8], ['down', 3], ['B', 3, 9],
    ['down', 4], ['down', 6], ['B', 4, 10], ['down', 5], ['B', 5, 11],
    ['A', 5, 12], ['up', 2],
]


def source_event(pc, f):
    f = bits(f, 3)
    seen = set()
    while pc != 13:
        if pc in seen:
            return 0  # пустой цикл ожидания в пункте 2
        seen.add(pc)
        if pc in OP_STATE:
            return OP_STATE[pc]
        n = SOURCE[pc]
        pc = n if isinstance(n, int) else n['yes'] if f[n['f']-1] == n['eq'] else n['no']
    return 6


def reference_next(state, f, reset=False, cyclic=False):
    if reset or state == 7 or (cyclic and state == 6):
        return 0
    target = source_event(AFTER_STATE[state], f)
    return 0 if cyclic and target == 6 else target


def lsa_event(index, f):
    f = bits(f, 3)
    labels = {t[1]: i for i, t in enumerate(LSA) if t[0] == 'down'}
    seen = set()
    while index < len(LSA):
        if index in seen:
            return 0
        seen.add(index)
        t = LSA[index]
        if t[0] == 'B':
            return t[1]
        if t[0] == 'down':
            index += 1
        elif t[0] == 'up':
            index = labels[t[1]]
        else:
            n = SOURCE[t[2]]
            index = labels[LSA[index+1][1]] if f[n['f']-1] == n['eq'] else index+2
    return 6
