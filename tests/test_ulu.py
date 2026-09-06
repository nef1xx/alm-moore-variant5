import unittest
import random
from itertools import product
from ulu.logic import INPUTS, FORMAL_F, original_f, minimized_f
from ulu.model import OUTPUTS, Moore, next_state
from ulu.netlist import GATES, Hardware, clock_sr, evaluate
from ulu.reference import LSA, source_event, lsa_event, reference_next
from ulu.minimize import certificate
from ulu.derived import output_functions, excitation_functions


class LogicTests(unittest.TestCase):
    def test_all_input_functions(self):
        for x in INPUTS:
            with self.subTest(x=x):
                self.assertEqual(original_f(x), minimized_f(x))
                v = evaluate(0, x)
                self.assertEqual(original_f(x), tuple(v[f'F{i}'] for i in (1, 2, 3)))

    def test_exact_minimum_sop(self):
        for i, cost in enumerate(((4, 8), (2, 3), (3, 3))):
            c = certificate(i)
            self.assertEqual((c['minimum_terms'], c['minimum_literals']), cost)

    def test_realizable_inputs(self):
        self.assertEqual({original_f(x) for x in INPUTS}, {(0, 0, 1), (0, 1, 0), (1, 0, 1), (1, 1, 1)})

    def test_bad_inputs(self):
        for x in ((1, 0), (0, 0, 0, 2), (0, 0, 0, -1), '0011'):
            with self.assertRaises(ValueError):
                original_f(x)


class AutomatonTests(unittest.TestCase):
    def test_derived_output_functions(self):
        for state in range(8):
            self.assertEqual(output_functions(state), OUTPUTS[state], state)

    def test_derived_rs_functions(self):
        for state, f, reset in product(range(8), FORMAL_F, (False, True)):
            s, r = excitation_functions(state, f, reset)
            target = reference_next(state, f, reset)
            expected_s, expected_r = [], []
            for k in (2, 1, 0):
                old, new = state >> k & 1, target >> k & 1
                expected_s.append(int(not old and new))
                expected_r.append(int(old and not new))
            self.assertEqual(s, tuple(expected_s), (state,f,reset))
            self.assertEqual(r, tuple(expected_r), (state,f,reset))
            self.assertTrue(all(not (si and ri) for si,ri in zip(s,r)))
            wires = evaluate(state, f_override=f, reset=reset)
            self.assertEqual(s, tuple(wires[f'S{k}'] for k in (2,1,0)))
            self.assertEqual(r, tuple(wires[f'R{k}'] for k in (2,1,0)))

    def test_lsa_against_original(self):
        for index, t in enumerate(LSA):
            if len(t) < 3:
                continue
            for f in FORMAL_F:
                self.assertEqual(lsa_event(index, f), source_event(t[2], f), (t, f))

    def test_behavior_against_original(self):
        for state, f, reset, cyclic in product(range(8), FORMAL_F, (False, True), (False, True)):
            self.assertEqual(next_state(state, f, reset, cyclic), reference_next(state, f, reset, cyclic),
                             (state, f, reset, cyclic))

    def test_hardware_formal_domain(self):
        for state, f, reset in product(range(8), FORMAL_F, (False, True)):
            v = evaluate(state, reset=reset, f_override=f)
            expected = reference_next(state, f, reset)
            self.assertEqual(clock_sr(state, v), expected, (state, f, reset))
            self.assertEqual(sum(v[f'D{k}'] << k for k in (2, 1, 0)), expected)
            self.assertEqual(tuple(v[f'Y{i}'] for i in range(1, 6)), OUTPUTS[state])
            for k in (2, 1, 0):
                self.assertFalse(v[f'S{k}'] and v[f'R{k}'])

    def test_integrated_hardware_all_inputs(self):
        for state, x, reset in product(range(8), INPUTS, (False, True)):
            row = Hardware(state).tick(x, reset)
            self.assertEqual(row['state_after'], reference_next(state, original_f(x), reset))
            self.assertEqual(row['y_before'], OUTPUTS[state])
            self.assertEqual(row['y_after'], OUTPUTS[row['state_after']])

    def test_outputs_do_not_depend_on_inputs(self):
        for state in range(8):
            for x in INPUTS:
                v = evaluate(state, x)
                self.assertEqual(tuple(v[f'Y{i}'] for i in range(1, 6)), OUTPUTS[state])

    def test_terminal_wait_reset_and_invalid(self):
        h = Hardware()
        for _ in range(4):
            self.assertEqual(h.tick((0, 0, 0, 0))['state_after'], 0)
        self.assertEqual(h.tick((0, 1, 0, 0))['state_after'], 1)
        h.state = 6
        for x in INPUTS:
            self.assertEqual(h.tick(x)['state_after'], 6)
        self.assertEqual(h.tick((0, 0, 0, 0), True)['state_after'], 0)
        self.assertEqual(Hardware(7).tick((0, 0, 0, 0))['state_after'], 0)

    def test_long_changing_sequences(self):
        rng = random.Random(5)
        for _ in range(100):
            state = rng.randrange(8)
            behavior, hardware, reference = Moore(state), Hardware(state), state
            for _ in range(100):
                x = INPUTS[rng.randrange(16)]
                reset = rng.random() < 0.08
                ref_next = reference_next(reference, original_f(x), reset)
                a, b = behavior.tick(x, reset), hardware.tick(x, reset)
                self.assertEqual(a['state_after'], ref_next)
                self.assertEqual(b['state_after'], ref_next)
                self.assertEqual(a['y_after'], b['y_after'])
                reference = ref_next

    def test_netlist_is_acyclic_and_has_unique_names(self):
        known = {'X1', 'X2', 'X3', 'X4', 'q2', 'q1', 'q0', 'RESET'}
        for g in GATES:
            self.assertNotIn(g['name'], known)
            self.assertTrue(set(g['inputs']) <= known, g)
            known.add(g['name'])


if __name__ == '__main__':
    unittest.main()
