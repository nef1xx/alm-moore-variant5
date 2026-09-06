"""Сокращённые функции из решения 08h: α1=q2, α2=q1, α3=q0.

S/R возвращаются в порядке α1,α2,α3 (в netlist это разряды 2,1,0).
Формулы вычисляются непосредственно, независимо от списка вентилей.
"""
from .logic import bits
from .model import state_bits


def output_functions(state):
    a, b, c = state_bits(state)
    return tuple(map(int, (
        (not a and c) or (a and not b and not c),
        (not a and b and not c) or (a and not b and c),
        not b and c,
        not a and b,
        not b and (a or c),
    )))


def excitation_functions(state, f, reset=False):
    a, b, c = state_bits(state)
    f1, f2, f3 = bits(f, 3)
    set_base = (
        not a and b and (c or f2),
        not b and c and (not a or f1 or not f2),
        not c and ((a and not b) or (not a and (not f2 or (b and not f1 and not f3)))),
    )
    reset_base = (
        a and c and (b or (not f1 and not f2)),
        b and (c or (not a and f2)),
        c and (not a or b or f1 or (f2 and f3)),
    )
    return (tuple(int(not reset and value) for value in set_base),
            tuple(int((reset and old) or value) for old, value in zip((a,b,c), reset_base)))
