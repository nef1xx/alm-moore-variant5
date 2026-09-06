"""Навигация по рисункам и проверка локальных ссылок документации."""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TITLES={
'01_flowchart':'Исходная блок-схема',
'02_flowchart_labeled':'Блок-схема с обозначениями A и B',
'03_lsa':'ЛСА',
'04_marked_gsa':'Отмеченная ГСА с остановкой в S6',
'04b_marked_gsa_cyclic':'Учебная циклическая отмеченная ГСА',
'05_moore_graph':'Основной граф Мура',
'05b_moore_reachable':'Граф с учётом достижимых F(X)',
'05c_moore_cyclic':'Учебный циклический граф Мура',
'06a_kmap_F1':'Карта Карно F1',
'06b_kmap_F2':'Карта Карно F2',
'06c_kmap_F3':'Карта Карно F3',
'07_input_logic':'Схема формирования F1,F2,F3',
'08a_hardware_overview':'Общая аппаратная схема',
'08b_state_decoder':'Дешифратор состояний',
'08g_hardware_table':'Аппаратная реализация управляющего автомата УЛУ — таблица',
'08c_transition_logic':'Логика переходов',
'08d_excitation_logic':'Функции возбуждения RS и альтернативные D',
'08e_register':'Три синхронных RS-триггера',
'08f_output_logic':'Формирование Y и DONE',
'09_timing':'Временная диаграмма тестового сценария',
}


def main():
    out=['# Все схемы варианта 5','',
         'Каждый рисунок доступен в PNG для просмотра и SVG для редактирования. '
         'Основная аппаратная схема соответствует остановке в S6. Циклические варианты явно подписаны.', '',
         '[Скачать единый PDF-альбом](../output/ALM_variant5_schemes.pdf)', '',
         '| Схема | Просмотр | Редактирование |','|---|---|---|']
    for stem,title in TITLES.items():
        out.append(f'| {title} | [PNG](../diagrams/{stem}.png) | [SVG](../diagrams/{stem}.svg) |')
    for stem,title in TITLES.items():
        out.extend(['',f'## {title}','',f'![{title}](../diagrams/{stem}.png)'])
    (ROOT/'docs/SCHEMES.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
    broken=[]
    for p in [ROOT/'README.md',ROOT/'AGENTS.md',*sorted((ROOT/'docs').glob('*.md'))]:
        text=p.read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if target.startswith(('http:', 'https:', '#', 'mailto:')):continue
            target=target.split('#')[0]
            if not (p.parent/target).exists():broken.append(f'{p.name}: {target}')
    if broken: raise RuntimeError('Неразрешённые ссылки:\n'+'\n'.join(broken))
    print(f'Gallery: {len(TITLES)} diagrams. All Markdown local links resolve.')


if __name__=='__main__':main()
