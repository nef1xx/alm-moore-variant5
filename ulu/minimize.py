"""Полный поиск минимальной ДНФ четырёх переменных, без SymPy.

Критерий: сначала число конъюнкций, затем суммарное число литералов.
Это не утверждение о минимуме транзисторов или многоуровневых схем.
"""
from itertools import combinations, product
from .logic import INPUTS, original_f, SELECTED_COVERS


def covers(pattern, x):
    return all(v is None or v == b for v, b in zip(pattern, x))


def format_term(pattern):
    return ' '.join(('~' if v == 0 else '')+f'X{k+1}' for k, v in enumerate(pattern) if v is not None) or '1'


def certificate(fi):
    on = {i for i, x in enumerate(INPUTS) if original_f(x)[fi]}
    valid = {}
    for p in product((0, 1, None), repeat=4):
        support = {i for i, x in enumerate(INPUTS) if covers(p, x)}
        if support and support <= on:
            valid[p] = support
    primes = {p: support for p, support in valid.items()
              if not any(support < other for other in valid.values())}
    optimal = []
    literal_min = None
    for size in range(1, len(primes)+1):
        found = [c for c in combinations(primes, size)
                 if set().union(*(primes[p] for p in c)) == on]
        if found:
            literal_min = min(sum(v is not None for p in c for v in p) for c in found)
            optimal = [c for c in found if sum(v is not None for p in c for v in p) == literal_min]
            break
    selected = SELECTED_COVERS[fi]
    if not any(set(selected) == set(c) for c in optimal):
        raise AssertionError('Выбранное покрытие не оптимально')
    return {'function': f'F{fi+1}', 'on_set': sorted(on),
            'off_set': sorted(set(range(16))-on),
            'minimum_terms': len(optimal[0]), 'minimum_literals': literal_min,
            'prime_implicants': [{'pattern': p, 'term': format_term(p), 'minterms': sorted(s)} for p, s in primes.items()],
            'all_optimal_sop': [' OR '.join(map(format_term, c)) for c in optimal],
            'selected': [{'pattern': p, 'term': format_term(p),
                          'minterms': [i for i, x in enumerate(INPUTS) if covers(p, x)]} for p in selected]}
