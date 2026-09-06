"""Поведенческая модель. Один вызов tick — один фронт CLK."""
from dataclasses import dataclass
from .logic import bits, minimized_f

OUTPUTS = (
    (0, 0, 0, 0, 0),  # S0: начало / ожидание
    (1, 0, 1, 0, 1),  # S1: B1, пункт 3
    (0, 1, 0, 1, 0),  # S2: B2, пункт 4
    (1, 0, 0, 1, 0),  # S3: B3, пункт 9
    (1, 0, 0, 0, 1),  # S4: B4, пункт 10
    (0, 1, 1, 0, 1),  # S5: B5, пункт 11
    (0, 0, 0, 0, 0),  # S6: конец
    (0, 0, 0, 0, 0),  # 111: неиспользуемый код, восстановление в S0
)
NAMES = ('Ожидание', 'B1', 'B2', 'B3', 'B4', 'B5', 'Конец', 'Недопустимый код')


def state_bits(state):
    if type(state) is not int or not 0 <= state < 8:
        raise ValueError('Код состояния должен быть целым числом от 0 до 7')
    return (state >> 2 & 1, state >> 1 & 1, state & 1)


def next_state(state, f, reset=False, cyclic=False):
    state_bits(state)
    f1, f2, f3 = bits(f, 3)
    if reset:
        return 0
    if state == 0:
        return 0 if f2 else 1
    if state == 1:
        return 2
    if state == 2:
        if not f2:
            return 3
        return 4 if (f3 or f1) else 5
    if state == 3:
        return 4
    if state == 4:
        return 5
    if state == 5:
        if f1:
            return 0 if cyclic else 6
        if not f2:
            return 3
        return 4 if f3 else 5
    if state == 6:
        return 0 if cyclic else 6
    return 0


@dataclass
class Moore:
    state: int = 0
    cyclic: bool = False

    def __post_init__(self):
        state_bits(self.state)

    @property
    def outputs(self):
        return OUTPUTS[self.state]

    @property
    def done(self):
        return not self.cyclic and self.state == 6

    def tick(self, x, reset=False):
        x = bits(x, 4)
        f = minimized_f(x)
        old = self.state
        self.state = next_state(old, f, reset, self.cyclic)
        return {'x': x, 'f': f, 'state_before': old, 'state_after': self.state,
                'y_before': OUTPUTS[old], 'y_after': self.outputs,
                'reset': int(bool(reset)), 'done': int(self.done),
                'cycle_completed': int(not reset and old == 5 and f[0] == 1)}
