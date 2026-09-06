"""Воспроизводимые таблицы и сертификаты. Запуск из любой директории."""
import csv
import json
import sys
from itertools import product
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ulu.logic import INPUTS, FORMAL_F, original_f, minimized_f
from ulu.minimize import certificate
from ulu.model import OUTPUTS, NAMES, state_bits, next_state
from ulu.netlist import GATES, Hardware, evaluate, clock_sr
from ulu.reference import SOURCE, LSA, reference_next, source_event, lsa_event
from ulu.cli import DEMO, parse_x

DATA = ROOT/'data'
DATA.mkdir(exist_ok=True)


def save_json(name, value):
    (DATA/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def save_csv(name, fields, rows):
    with (DATA/name).open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    save_json('source_algorithm.json', SOURCE)
    save_json('lsa.json', {'jump_when': 1, 'tokens': LSA})
    save_json('gate_netlist.json', {'inputs': ['X1','X2','X3','X4','q2','q1','q0','RESET'],
                                  'clock': 'simultaneous rising edge', 'gates': GATES})
    certificates = [certificate(i) for i in range(3)]
    save_json('minimization.json', certificates)
    truth = []
    for x in INPUTS:
        assert original_f(x) == minimized_f(x)
        truth.append(dict(zip(['X1','X2','X3','X4','F1','F2','F3'], x+original_f(x))))
    save_csv('truth_table.csv', ['X1','X2','X3','X4','F1','F2','F3'], truth)
    save_csv('states.csv', ['state','code','meaning','Y1','Y2','Y3','Y4','Y5'],
             [{'state': f'S{s}' if s < 7 else 'unused', 'code': f'{s:03b}', 'meaning': NAMES[s],
               **dict(zip(['Y1','Y2','Y3','Y4','Y5'], OUTPUTS[s]))} for s in range(8)])
    formal, integrated, excitations = [], [], []
    for state, f in product(range(8), FORMAL_F):
        target = next_state(state, f)
        assert target == reference_next(state, f)
        v = evaluate(state, f_override=f)
        assert clock_sr(state, v) == target
        base = {'state': f'S{state}', 'code': f'{state:03b}',
                **dict(zip(['F1','F2','F3'], f)), 'next': f'S{target}', 'next_code': f'{target:03b}'}
        formal.append(base)
        excitations.append({**base, **{n:v[n] for n in ('N2','N1','N0','S2','R2','S1','R1','S0','R0')}})
    save_csv('transitions_formal.csv', list(formal[0]), formal)
    save_csv('excitation_table.csv', list(excitations[0]), excitations)
    for state, x in product(range(8), INPUTS):
        row = Hardware(state).tick(x)
        assert row['state_after'] == reference_next(state, original_f(x))
        integrated.append({'state': f'S{state}', **dict(zip(['X1','X2','X3','X4'], x)),
                           **dict(zip(['F1','F2','F3'], original_f(x))), 'next': f"S{row['state_after']}"})
    save_csv('transitions_from_x.csv', list(integrated[0]), integrated)
    lsa_checks = 0
    for i, token in enumerate(LSA):
        if len(token) == 3:
            for f in FORMAL_F:
                assert source_event(token[2], f) == lsa_event(i, f)
                lsa_checks += 1
    for state, f, reset in product(range(8), FORMAL_F, (0,1)):
        v = evaluate(state, reset=reset, f_override=f)
        assert clock_sr(state,v) == reference_next(state,f,reset)
        assert all(not (v[f'S{k}'] and v[f'R{k}']) for k in (2,1,0))
    h, trace = Hardware(), []
    for i, x in enumerate(DEMO, 1):
        row = h.tick(parse_x(x))
        row['tick'] = i
        trace.append(row)
    save_json('demo_trace.json', trace)
    save_csv('demo_trace.csv', ['tick','X','F','state_before','state_after','Y_before','Y_after','DONE'],
             [{'tick': r['tick'], 'X': ''.join(map(str,r['x'])), 'F': ''.join(map(str,r['f'])),
               'state_before': f"S{r['state_before']}", 'state_after': f"S{r['state_after']}",
               'Y_before': ''.join(map(str,r['y_before'])), 'Y_after': ''.join(map(str,r['y_after'])),
               'DONE': r['done']} for r in trace])
    save_json('verification.json', {'status': 'PASS', 'input_rows':16,
        'lsa_next_event_cases':lsa_checks, 'formal_state_input_cases':64,
        'formal_state_input_reset_cases':128, 'integrated_state_x_cases':128,
        'reachable_F':sorted({original_f(x) for x in INPUTS}),
        'minimum_sop_costs':[[c['minimum_terms'],c['minimum_literals']] for c in certificates],
        'note':'Детерминированные проверки этого файла; дополнительные 10 000 тактов проверяет unittest.'})
    print('Generated data: truth tables, transitions, netlist, minimum certificates, verified demo.')


if __name__ == '__main__':
    main()
