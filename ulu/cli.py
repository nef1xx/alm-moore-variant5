"""python -m ulu.cli --demo; python -m ulu.cli --interactive"""
import argparse
import csv
import json
from pathlib import Path
from .model import Moore
from .netlist import Hardware

DEMO = ['0000', '0100', '0100', '1010', '1000', '1000', '0111', '0100', '1010', '0100', '0100']


def parse_x(text):
    text = text.replace(' ', '').replace(',', '')
    if len(text) != 4 or any(c not in '01' for c in text):
        raise ValueError('Введите четыре бита X1X2X3X4, например 0100')
    return tuple(map(int, text))


def digits(values):
    return ''.join(map(str, values))


def main():
    parser = argparse.ArgumentParser(description='Вариант 5 — автомат Мура, один ввод на такт')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--demo', action='store_true', help='Проверочный сценарий с изменяющимися входами')
    group.add_argument('--sequence', help='Последовательность входов: 0100,0100,1010,...')
    group.add_argument('--interactive', action='store_true', help='Ввод X на каждом такте; r — синхронный сброс; q — выход')
    parser.add_argument('--model', choices=('hardware', 'behavior'), default='hardware')
    parser.add_argument('--cyclic', action='store_true', help='Учебный циклический граф (только behavior)')
    parser.add_argument('--csv', type=Path, help='Сохранить трассу CSV')
    parser.add_argument('--json', type=Path, help='Сохранить трассу JSON')
    args = parser.parse_args()
    if args.cyclic and args.model != 'behavior':
        parser.error('--cyclic требует --model behavior; аппаратная схема реализует основной граф с S6')
    machine = Hardware() if args.model == 'hardware' else Moore(cyclic=args.cyclic)
    traces = []
    print('Такт  X     F    Q до → после   Y до → после    RESET DONE')
    def step(x, reset=False):
        row = machine.tick(x, reset)
        row['tick'] = len(traces)+1
        traces.append(row)
        print(f"{row['tick']:4}  {digits(row['x'])}  {digits(row['f'])}  "
              f"{row['state_before']:03b} → {row['state_after']:03b}       "
              f"{digits(row['y_before'])} → {digits(row['y_after'])}    "
              f"{row['reset']}     {row['done']}")
    if args.interactive:
        while True:
            try:
                command = input('X1X2X3X4 / r / q > ').strip().lower()
                if command == 'q':
                    break
                step((0, 0, 0, 0), True) if command == 'r' else step(parse_x(command))
            except ValueError as error:
                print(error)
            except (EOFError, KeyboardInterrupt):
                break
    else:
        try:
            sequence = args.sequence.split(',') if args.sequence else DEMO
            for item in sequence:
                step(parse_x(item))
        except ValueError as error:
            parser.error(str(error))
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open('w', encoding='utf-8', newline='') as file:
            fields = ['tick', 'x', 'f', 'state_before', 'state_after', 'y_before', 'y_after', 'reset', 'done']
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            for r in traces:
                writer.writerow({k: digits(r[k]) if isinstance(r[k], tuple) else r[k] for k in fields})
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(traces, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
