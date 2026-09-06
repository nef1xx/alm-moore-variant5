"""Синхронная схема на RS-триггерах: явный список вентилей и их вычисление.

Входы: X1..X4, q2,q1,q0, RESET. CLK представлен методом tick. RESET
синхронный и активен уровнем 1. Выходы строятся только по текущим q.
"""
from dataclasses import dataclass
from .logic import bits
from .model import state_bits


def make_netlist():
    gates = []
    def add(name, op, *args):
        gates.append({'name': name, 'op': op, 'inputs': list(args)})
        return name
    for v in ('X1', 'X2', 'X3', 'X4', 'q2', 'q1', 'q0', 'RESET'):
        add('n'+v, 'NOT', v)
    add('p11', 'AND', 'nX1', 'nX2')
    add('p12', 'AND', 'X1', 'X3')
    add('p13', 'AND', 'X2', 'nX3')
    add('p14', 'AND', 'X2', 'nX4')
    add('F1', 'OR', 'p11', 'p12', 'p13', 'p14')
    add('p21', 'AND', 'X1', 'nX3')
    add('F2', 'OR', 'nX2', 'p21')
    add('F3', 'OR', 'nX1', 'X2', 'X3')
    for i in (1, 2, 3):
        add(f'nF{i}', 'NOT', f'F{i}')
    for s in range(8):
        add(f'z{s}', 'AND', *[('q'+str(k)) if s >> k & 1 else ('nq'+str(k)) for k in (2, 1, 0)])
    add('t1', 'AND', 'z0', 'nF2')
    add('t2', 'BUF', 'z1')
    add('h53', 'AND', 'z5', 'nF1')
    add('h3', 'OR', 'z2', 'h53')
    add('t3', 'AND', 'nF2', 'h3')
    add('h41', 'OR', 'F3', 'F1')
    add('h42', 'AND', 'z2', 'F2', 'h41')
    add('h43', 'AND', 'z5', 'nF1', 'F2', 'F3')
    add('t4', 'OR', 'z3', 'h42', 'h43')
    add('h51', 'OR', 'z2', 'z5')
    add('h52', 'AND', 'F2', 'nF3', 'nF1', 'h51')
    add('t5', 'OR', 'z4', 'h52')
    add('h61', 'AND', 'z5', 'F1')
    add('t6', 'OR', 'z6', 'h61')
    add('N2', 'OR', 't4', 't5', 't6')
    add('N1', 'OR', 't2', 't3', 't6')
    add('N0', 'OR', 't1', 't3', 't5')
    for k in (2, 1, 0):
        add(f'nN{k}', 'NOT', f'N{k}')
        add(f'S{k}', 'AND', 'nRESET', f'nq{k}', f'N{k}')
        add(f'hr{k}', 'OR', 'RESET', f'nN{k}')
        add(f'R{k}', 'AND', f'q{k}', f'hr{k}')
        add(f'D{k}', 'AND', 'nRESET', f'N{k}')  # эквивалентная реализация на D
    for i, states in enumerate(((1, 3, 4), (2, 5), (1, 5), (2, 3), (1, 4, 5)), 1):
        add(f'Y{i}', 'OR', *[f'z{s}' for s in states])
    add('DONE', 'BUF', 'z6')
    return gates


GATES = make_netlist()


def evaluate(state, x=(0, 0, 0, 0), reset=False, f_override=None):
    q = state_bits(state)
    x = bits(x, 4)
    values = dict(zip(('X1', 'X2', 'X3', 'X4'), x))
    values.update(zip(('q2', 'q1', 'q0'), q))
    values['RESET'] = int(bool(reset))
    overrides = dict(zip(('F1', 'F2', 'F3'), bits(f_override, 3))) if f_override is not None else {}
    for gate in GATES:
        name, op = gate['name'], gate['op']
        a = [values[n] for n in gate['inputs']]
        if name in overrides:
            result = overrides[name]
        elif op == 'NOT':
            result = not a[0]
        elif op == 'AND':
            result = all(a)
        elif op == 'OR':
            result = any(a)
        elif op == 'BUF':
            result = a[0]
        else:
            raise ValueError(f'Неизвестный вентиль {op}')
        values[name] = int(result)
    return values


def clock_sr(state, values):
    new = 0
    for k in (2, 1, 0):
        s, r = values[f'S{k}'], values[f'R{k}']
        if s and r:
            raise ValueError(f'Запрещённое сочетание S{k}=R{k}=1')
        old = state >> k & 1
        bit = int(s or (old and not r))
        new |= bit << k
    return new


@dataclass
class Hardware:
    state: int = 0

    def __post_init__(self):
        state_bits(self.state)

    def tick(self, x, reset=False):
        x = bits(x, 4)
        old = self.state
        wires = evaluate(old, x, reset)
        self.state = clock_sr(old, wires)
        after = evaluate(self.state, x, reset)
        return {'x': x, 'f': tuple(wires[f'F{i}'] for i in (1, 2, 3)),
                'state_before': old, 'state_after': self.state,
                'y_before': tuple(wires[f'Y{i}'] for i in range(1, 6)),
                'y_after': tuple(after[f'Y{i}'] for i in range(1, 6)),
                'reset': int(bool(reset)), 'done': after['DONE'],
                'cycle_completed': int(not reset and old == 5 and wires['F1']),
                'S': tuple(wires[f'S{k}'] for k in (2, 1, 0)),
                'R': tuple(wires[f'R{k}'] for k in (2, 1, 0))}
