"""Сводная таблица аппаратной реализации с проверкой всех формальных F."""
from ulu.logic import FORMAL_F
from ulu.model import OUTPUTS
from ulu.netlist import evaluate
from ulu.reference import reference_next


# Дуги основного графа. Дерево условия задаёт и запись, и её проверку.
TRANSITIONS = (
    (0, 0, 'F2'),
    (0, 1, ('not', 'F2')),
    (1, 2, 1),
    (2, 3, ('not', 'F2')),
    (2, 4, ('and', 'F2', ('or', 'F3', 'F1'))),
    (2, 5, ('and', 'F2', ('not', 'F3'), ('not', 'F1'))),
    (3, 4, 1),
    (4, 5, 1),
    (5, 3, ('and', ('not', 'F1'), ('not', 'F2'))),
    (5, 4, ('and', ('not', 'F1'), 'F2', 'F3')),
    (5, 5, ('and', ('not', 'F1'), 'F2', ('not', 'F3'))),
    (5, 6, 'F1'),
    (6, 6, 1),
    (7, 0, 1),
)
HEADERS = ('Начальное состояние', 'Код начального состояния',
           'Конечное состояние', 'Код конечного состояния',
           'Входные сигналы Fi', 'Выходные сигналы Yj', 'Функция возбуждения RS')
FIELDS = ('state', 'code', 'next', 'next_code', 'condition', 'outputs', 'excitation')


def condition_value(expr, f):
    if expr == 1:
        return True
    if isinstance(expr, str):
        return bool(f[int(expr[1])-1])
    op, *args = expr
    values = [condition_value(a, f) for a in args]
    if op == 'not':
        return not values[0]
    return all(values) if op == 'and' else any(values)


def condition_text(expr, parent_precedence=0):
    if not isinstance(expr, tuple):
        return str(expr)
    op, *args = expr
    precedence = {'or': 1, 'and': 2, 'not': 3}[op]
    parts = [condition_text(a, precedence) for a in args]
    text = '¬'+parts[0] if op == 'not' else ('∨' if op == 'or' else '').join(parts)
    return '('+text+')' if precedence < parent_precedence else text


def hardware_rows():
    rows, covered = [], set()
    for state, target, condition in TRANSITIONS:
        sr = {}
        for k in (2, 1, 0):
            before, after = state >> k & 1, target >> k & 1
            sr[f'S{k}'] = int(not before and after)
            sr[f'R{k}'] = int(before and not after)
        matching = [f for f in FORMAL_F if condition_value(condition, f)]
        assert matching, (state, target, 'empty condition')
        for f in matching:
            assert (state, f) not in covered, (state, f, 'overlapping rows')
            covered.add((state, f))
            assert target == reference_next(state, f), (state, target, f)
            wires = evaluate(state, f_override=f)
            assert all(wires[name] == value for name, value in sr.items()), (state, target, f)
            assert tuple(wires[f'Y{i}'] for i in range(1, 6)) == OUTPUTS[state]
        rows.append(dict(zip(FIELDS, (
            f'S{state}' if state < 7 else 'Неисп.', f'{state:03b}', f'S{target}', f'{target:03b}',
            condition_text(condition),
            ' '.join(f'Y{i}' for i, value in enumerate(OUTPUTS[state], 1) if value) or '—',
            ' '.join(name for name, value in sr.items() if value) or '—',
        ))))
    assert covered == {(state, f) for state in range(8) for f in FORMAL_F}
    return rows


def markdown_table(rows):
    lines = ['| '+' | '.join(HEADERS)+' |', '| '+' | '.join('---' for _ in HEADERS)+' |']
    lines.extend('| '+' | '.join(row[field] for field in FIELDS)+' |' for row in rows)
    return '\n'.join(lines)
