"""Все редактируемые SVG. Никаких сетевых сервисов или генерации рисунков ИИ."""
import json
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from ulu.logic import INPUTS, SELECTED_COVERS, original_f
from ulu.minimize import covers, format_term
from ulu.netlist import GATES
from ulu.reference import LSA
from svg_tools import SVG

OUT = ROOT/'diagrams'
OUT.mkdir(exist_ok=True)
SUB = str.maketrans('0123456789','₀₁₂₃₄₅₆₇₈₉')
def sub(value): return str(value).translate(SUB)
def fi_term(p): return format_term(p).replace('~','¬').translate(SUB)


def flow(name, labels=True, marked=False, cyclic=False):
    title = 'Вариант 5. '+('Отмеченная ГСА автомата Мура' if marked else 'Блок-схема алгоритма УЛУ')
    if marked: title += ' — циклическая' if cyclic else ' — с состоянием «Конец»'
    s=SVG(1050,1470,title)
    def edge(d): s.path(d,True)
    def label(x,y,t): s.text(x,y,t,20)
    def cond(y,a,f,p):
        s.parts.append(f'<path d="M530 {y-45} L615 {y} L530 {y+45} L445 {y} Z" fill="white" stroke="#17212b" stroke-width="2"/>')
        if labels: s.text(530,y-7,sub('A'+str(a)),18)
        s.text(530,y+19 if labels else y+8,f,24)
        s.text(643,y-28,f'п. {p}',17,'start')
    def state_tag(x,y,n):
        s.rect(x,y-23,70,30,fill='#edf4fb',stroke='#315575',radius=5)
        s.text(x+35,y,sub('S'+str(n)),22,color='#234d70',weight='bold')
    def op(x,y,b,ys,p):
        s.rect(x-110,y-34,220,68)
        if labels: s.text(x,y-9,sub('B'+str(b))+(' / '+sub('S'+str(b)) if marked else ''),18)
        s.text(x,y+20 if labels else y+8,ys,24)
        s.text(x+125,y-15,f'п. {p}',17,'start')
    edge('M530 96 V135'); edge('M615 180 H780 V115 H530 V135');label(660,172,'1');s.circle(530,115,3,fill='#17212b')
    edge('M530 225 V256');label(550,247,'0');edge('M530 324 V356');edge('M530 424 V465')
    edge('M445 510 H180 V856');label(411,499,'1');edge('M530 555 V600');label(550,581,'0')
    edge('M445 645 H360 V1010 H420');label(411,634,'1');edge('M530 690 V735');label(550,719,'0')
    edge('M530 825 V976');label(550,857,'0');s.text(552,907,'п. 8 → п. 10',17,'start')
    edge('M615 780 H890 V1140 H640');label(660,769,'1')
    edge('M180 924 V1010 H420');s.circle(360,1010,3,fill='#17212b')
    edge('M530 1044 V1106');edge('M530 1174 V1225')
    edge('M445 1270 H55 V445 H530 V465');label(411,1258,'1');s.circle(530,445,3,fill='#17212b')
    edge('M530 1315 V1364');label(550,1346,'0')
    s.ellipse(530,70,85,26);s.text(530,78,'Начало',23)
    cond(180,1,'F₂ = 1',2);op(530,290,1,'Y₁, Y₃, Y₅',3);op(530,390,2,'Y₂, Y₄',4)
    cond(510,2,'F₂ = 0',5);cond(645,3,'F₃ = 1',6);cond(780,4,'F₁ = 0',7)
    op(180,890,3,'Y₁, Y₄',9);op(530,1010,4,'Y₁, Y₅',10);op(530,1140,5,'Y₂, Y₃, Y₅',11)
    cond(1270,5,'F₁ = 0',12)
    s.ellipse(530,1390,85,26);s.text(530,1398,'Конец',23)
    if marked:
        state_tag(650,80,0);state_tag(650,1400,0 if cyclic else 6)
    footer='1 — проверка истинна; 0 — проверка ложна.'
    if marked: footer+=' Метки S обозначают состояния.'
    s.text(525,1450,footer,17)
    s.save(OUT/name)


def lsa():
    s=SVG(1540,205,'ЛСА варианта 5 — переход по ↑ при A = 1')
    x=32
    for t in LSA:
        if t[0] in ('A','B'):
            s.text(x,125,sub(t[0]+str(t[1])),43,'start',weight='bold');x+=78
        else:
            if t[0]=='up': d=f'M{x+16} 144 V70 M{x+1} 86 L{x+16} 70 L{x+31} 86'
            else: d=f'M{x+16} 70 V144 M{x+1} 128 L{x+16} 144 L{x+31} 128'
            s.path(d,width=4);s.text(x+33,77,t[1],24,'start');x+=57
    s.text(770,184,'Отдельная ↑⁶ — безусловный переход п. 8. При A₅ = 0 чтение заканчивается.',18)
    s.save(OUT/'03_lsa.svg')


def graph(name, reachable=False, cyclic=False):
    title='Граф Мура — '+('учебный циклический вариант' if cyclic else 'основной вариант с завершением')
    if reachable: title='Граф Мура — только достижимые сочетания F(X)'
    s=SVG(1380,1080,title)
    pos={0:(140,160),1:(450,160),2:(790,160),3:(1130,430),4:(790,720),5:(450,720),6:(140,720)}
    def e(d,txt,x,y): s.path(d,True);s.label(x,y,txt,20)
    e('M92 109 C20 20 250 10 185 104','F₂',130,70)
    e('M210 160 H380','¬F₂',295,143)
    e('M520 160 H720','1',620,143)
    e('M843 207 L1078 383','¬F₂',979,275)
    e('M790 230 V650','F₁F₂F₃' if reachable else 'F₂(F₃ ∨ F₁)',895,447)
    e('M744 214 C680 310 450 270 450 650','¬F₁F₂¬F₃' if reachable else 'F₂¬F₃¬F₁',564,318)
    e('M1077 476 L842 672','1',989,561)
    e('M720 720 H520','1',620,750)
    e('M514 750 C690 1000 1335 1070 1180 480','¬F₁¬F₂',1010,966)
    if not reachable:
        e('M509 683 C570 556 688 565 745 665','¬F₁F₂F₃',637,570)
    e('M425 786 C353 929 594 929 485 781','¬F₁F₂¬F₃',463,943)
    if cyclic:
        e('M381 706 C36 650 39 356 111 224','F₁',91,493)
    else:
        e('M380 720 H210','F₁',295,702)
        e('M92 771 C5 892 274 892 186 773','1',140,886)
    for n,(x,y) in pos.items():
        if cyclic and n==6: continue
        s.circle(x,y,70,fill='#f8fbff' if n in (0,6) else 'white')
        if n==6:s.circle(x,y,63,stroke='#52616f',width=1)
        s.text(x,y-24,sub('S'+str(n)),25,weight='bold')
        s.text(x,y+2,('000' if n==0 else f'{n:03b}'),16,color='#52616f')
        ys=['—','Y₁,Y₃,Y₅','Y₂,Y₄','Y₁,Y₄','Y₁,Y₅','Y₂,Y₃,Y₅','—'][n]
        s.text(x,y+31,ys,19)
    s.path('M140 315 V232',True);s.text(170,313,'Начало / RESET',17,'start')
    s.text(690,1022,'Дуги показаны при RESET = 0. RESET = 1 на фронте CLK переводит любое состояние в S₀.',18)
    s.text(690,1050,'Внутри вершины: состояние, код q₂q₁q₀, активные выходы. Остальные Y равны 0.',18)
    s.save(OUT/name)


def kmap(fi):
    gray=((0,0),(0,1),(1,1),(1,0))
    s=SVG(1120,680,f'Минимизация F{fi+1} — карта Карно')
    ox,oy,c=160,145,90
    s.text(340,92,'X₃X₄ →',22)
    s.text(65,326,'X₁X₂',22)
    for i,g in enumerate(gray):
        s.text(ox+(i+.5)*c,oy-20,''.join(map(str,g)),22)
        s.text(ox-30,oy+(i+.5)*c+8,''.join(map(str,g)),22)
    for r,rg in enumerate(gray):
        for col,cg in enumerate(gray):
            val=original_f(rg+cg)[fi]
            s.rect(ox+col*c,oy+r*c,c,c,fill='#f2f6fa' if val else 'white',stroke='#b2bec9',width=1)
            s.text(ox+(col+.5)*c,oy+(r+.5)*c+10,val,28)
    colors=('#b73437','#2468b0','#16816b','#8c4faa')
    def runs(vals):
        result=[]
        for v in vals:
            if result and v==result[-1][-1]+1: result[-1].append(v)
            else: result.append([v])
        return result
    wraps=[]
    for gi,p in enumerate(SELECTED_COVERS[fi]):
        cells=[(r,col) for r,rg in enumerate(gray) for col,cg in enumerate(gray) if covers(p,rg+cg)]
        rows=sorted({r for r,col in cells});cols=sorted({col for r,col in cells})
        if len(runs(rows))>1 or len(runs(cols))>1: wraps.append(gi+1)
        inset=5+gi*4
        for rs in runs(rows):
            for cs in runs(cols):
                s.rect(ox+cs[0]*c+inset,oy+rs[0]*c+inset,len(cs)*c-2*inset,len(rs)*c-2*inset,
                       fill='none',stroke=colors[gi],radius=12,width=3)
        ly=178+gi*78
        s.rect(610,ly-22,27,27,fill='none',stroke=colors[gi],width=3)
        s.text(654,ly,f'G{gi+1}: {fi_term(p)}',23,'start')
        literals=sum(v is not None for v in p)
        s.text(654,ly+27,f'Клеток: {len(cells)}; литералов: {literals}',17,'start',color='#52616f')
    s.text(560,559,f'F{fi+1} = '+' ∨ '.join(fi_term(p) for p in SELECTED_COVERS[fi]),22)
    s.text(560,603,'Порядок Грея: 00, 01, 11, 10. Противоположные края карты соседствуют.',18)
    if wraps: s.text(560,639,'Группы с переходом через край: '+', '.join(f'G{i}' for i in wraps)+'. Части одного цвета образуют одну группу.',17)
    else: s.text(560,639,'Все группы имеют размер 2ᵏ и содержат только единицы.',17)
    s.save(OUT/f'06{chr(97+fi)}_kmap_F{fi+1}.svg')


def gate_sheet(name,title,names):
    gates=[g for g in GATES if g['name'] in names]
    cols=3;rows=math.ceil(len(gates)/cols)
    s=SVG(1450,155+rows*155,title)
    s.text(725,70,'Именованные цепи: одинаковые подписи означают электрическое соединение, в том числе между листами.',17)
    for i,g in enumerate(gates):
        x=155+(i%cols)*475;y=128+(i//cols)*155
        s.gate(x,y,g['name'],g['op'],g['inputs'])
    s.text(725,s.height-18,'& — И; ≥1 — ИЛИ; кружок на выходе — НЕ; 1 без кружка — повторитель.',17)
    s.save(OUT/name)
    return {g['name'] for g in gates}


def register():
    s=SVG(1330,1120,'Регистр состояния — три синхронных RS-триггера')
    s.text(665,73,'Все три триггера переключаются одновременно по положительному фронту CLK.',19)
    for j,k in enumerate((2,1,0)):
        y=150+j*290
        s.rect(495,y,290,215)
        s.text(640,y+38,f'RS{k}',26,weight='bold')
        for pin,py in ((f'S{k}',y+82),(f'R{k}',y+133)):
            s.path(f'M320 {py} H495',True);s.text(308,py+7,pin,23,'end')
            s.text(511,py+7,pin[0],22,'start')
        s.path(f'M320 {y+183} H495')
        s.path(f'M495 {y+173} L510 {y+183} L495 {y+193}')
        s.text(308,y+190,'CLK',22,'end')
        s.path(f'M785 {y+92} H958',True);s.text(978,y+100,f'q{k}',25,'start')
        s.path(f'M785 {y+153} H958',True);s.text(978,y+161,f'¬q{k}',25,'start')
        s.text(60,y+60,f'Разряд {k}',22,'start')
        s.text(60,y+99,f'S{k}=¬RESET · ¬q{k} · N{k}',18,'start')
        s.text(60,y+134,f'R{k}=q{k} · (RESET ∨ ¬N{k})',18,'start')
    s.text(665,1051,'RESET — синхронный, активный 1; он учтён в логике S и R на соседнем листе.',18)
    s.text(665,1086,'При RESET = 1: S = 0, R = q. На ближайшем фронте все q становятся 0.',18)
    s.save(OUT/'08e_register.svg')


def overview():
    s=SVG(1530,850,'Аппаратная реализация УЛУ — структура и соединения')
    boxes=[(170,180,200,180,['Формирование F','И, ИЛИ, НЕ','лист 07']),
           (480,180,240,180,['Дешифратор q','и логика N','листы 08b, 08c']),
           (830,180,230,180,['Возбуждение S,R','с учётом RESET','лист 08d']),
           (1180,180,220,180,['Регистр q₂q₁q₀','3 RS-триггера','лист 08e']),
           (900,600,340,150,['Формирование Y и DONE','только по состоянию q','лист 08f'])]
    for x,y,w,h,lines in boxes:
        s.rect(x,y,w,h,fill='#f8fbff')
        for i,t in enumerate(lines):s.text(x+w/2,y+52+i*39,t,21 if i<2 else 18)
    s.path('M45 265 H170',True);s.text(87,242,'X₁…X₄',20)
    s.path('M370 235 H480',True);s.text(425,215,'F₁,F₂,F₃',18)
    s.path('M720 265 H830',True);s.text(775,243,'N₂,N₁,N₀',18)
    s.path('M1060 240 H1180',True);s.text(1120,219,'S₂,S₁,S₀',18)
    s.path('M1060 310 H1180',True);s.text(1120,292,'R₂,R₁,R₀',18)
    s.path('M1400 270 H1450 V480 H450 V315 H480',True)
    s.text(1230,468,'Обратная связь q₂,q₁,q₀',20)
    s.path('M945 480 V360',True);s.circle(945,480,4,fill='#17212b');s.text(898,420,'q₂,q₁,q₀',18)
    s.path('M1070 480 V600',True);s.circle(1070,480,4,fill='#17212b')
    s.path('M1240 675 H1440',True);s.text(1340,652,'Y₁…Y₅, DONE',20)
    s.path('M800 108 H945 V180',True);s.text(800,94,'RESET',20)
    s.path('M1140 108 H1290 V180',True);s.text(1140,94,'CLK ↑',20)
    s.text(490,650,'q⁺ = S ∨ (q ∧ ¬R)',26)
    s.text(490,698,'S ∧ R = 0 для каждого разряда',21)
    s.text(765,804,'Каждая линия с перечнем сигналов обозначает группу отдельных проводов. RESET действует на фронте CLK.',18)
    s.save(OUT/'08a_hardware_overview.svg')


def timing():
    trace=json.loads((ROOT/'data/demo_trace.json').read_text(encoding='utf-8'))
    from ulu.model import OUTPUTS
    states=[0]+[r['state_after'] for r in trace]
    s=SVG(1310,795,'Проверочный сценарий — состояния и выходы после фронта CLK')
    ox,w=140,93
    for t in range(len(states)):
        x=ox+t*w
        s.path(f'M{x} 87 V735',color='#d9e1e8',width=1)
        s.text(x+w/2,106,t,17)
        s.text(x+w/2,151,f'S{states[t]}',20,weight='bold')
        s.text(x+w/2,191,'—' if t==0 else ''.join(map(str,trace[t-1]['x'])),18)
        s.text(x+w/2,230,'—' if t==0 else ''.join(map(str,trace[t-1]['f'])),18)
    for y,text in ((106,'Такт'),(151,'Состояние'),(191,'X до ↑'),(230,'F до ↑')):s.text(119,y,text,18,'end')
    for i,name in enumerate(['Y₁','Y₂','Y₃','Y₄','Y₅','DONE']):
        baseline=313+i*77
        vals=[OUTPUTS[q][i] if i<5 else int(q==6) for q in states]
        path=f'M{ox} {baseline-33*vals[0]}'
        for t,v in enumerate(vals):
            if t: path+=f' V{baseline-33*v}'
            path+=f' H{ox+(t+1)*w}'
        s.path(path,color='#205e91',width=2.5)
        s.text(119,baseline-8,name,22,'end')
        s.text(ox-4,baseline+6,'0',12,'end');s.text(ox-4,baseline-30,'1',12,'end')
    s.text(655,772,'На такте 6 повторяется S₅. На такте 7 возврат ведёт к S₃. С такта 10 автомат остаётся в S₆.',18)
    s.save(OUT/'09_timing.svg')


def main():
    flow('01_flowchart.svg',labels=False)
    flow('02_flowchart_labeled.svg')
    lsa()
    flow('04_marked_gsa.svg',marked=True)
    flow('04b_marked_gsa_cyclic.svg',marked=True,cyclic=True)
    graph('05_moore_graph.svg')
    graph('05b_moore_reachable.svg',reachable=True)
    graph('05c_moore_cyclic.svg',cyclic=True)
    for i in range(3):kmap(i)
    names={g['name'] for g in GATES}
    inp={n for n in names if n.startswith(('nX','p1','p2')) or n in ('F1','F2','F3')}
    decoder={n for n in names if n.startswith(('nq','z'))}
    excitation={n for n in names if n.startswith(('nN','S','R','hr','D')) and n!='DONE'}|{'nRESET'}
    outputs={f'Y{i}' for i in range(1,6)}|{'DONE'}
    transition=names-inp-decoder-excitation-outputs
    rendered=set()
    rendered|=gate_sheet('07_input_logic.svg','Формирование входных сигналов F₁, F₂, F₃',inp)
    rendered|=gate_sheet('08b_state_decoder.svg','Дешифратор состояния — z₀…z₇',decoder)
    rendered|=gate_sheet('08c_transition_logic.svg','Логика переходов — t₁…t₆ и N₂,N₁,N₀',transition)
    rendered|=gate_sheet('08d_excitation_logic.svg','Функции возбуждения S,R и эквивалентные входы D',excitation)
    rendered|=gate_sheet('08f_output_logic.svg','Формирование выходов Y₁…Y₅ и DONE',outputs)
    assert rendered==names, names-rendered
    register();overview();timing()
    print(f'Generated {len(list(OUT.glob("*.svg")))} SVG diagrams; every netlist gate is drawn.')


if __name__=='__main__':main()
