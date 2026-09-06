"""Небольшие воспроизводимые SVG-примитивы для технических схем."""
from html import escape
from pathlib import Path


class SVG:
    def __init__(self, width, height, title):
        self.width, self.height = width, height
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="#17212b"/></marker></defs>',
            f'<rect width="{width}" height="{height}" fill="white"/>',
            '<style>text{font-family:Arial,sans-serif;fill:#17212b} .wire{fill:none;stroke:#17212b;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}</style>']
        self.text(width/2, 34, title, 24, weight='bold')

    def text(self, x, y, value, size=20, anchor='middle', color=None, weight=None):
        attrs = f'font-size="{size}" text-anchor="{anchor}"'
        if color: attrs += f' style="fill:{color}"'
        if weight: attrs += f' font-weight="{weight}"'
        self.parts.append(f'<text x="{x}" y="{y}" {attrs}>{escape(str(value))}</text>')

    def path(self, d, arrow=False, color=None, dash=None, width=2):
        attrs = f'style="stroke:{color or "#17212b"};stroke-width:{width}"'
        if arrow: attrs += ' marker-end="url(#arrow)"'
        if dash: attrs += f' stroke-dasharray="{dash}"'
        self.parts.append(f'<path class="wire" d="{d}" {attrs}/>')

    def rect(self, x, y, w, h, fill='white', stroke='#17212b', radius=0, width=2):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

    def circle(self, x, y, r, fill='white', stroke='#17212b', width=2):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

    def ellipse(self, x, y, rx, ry):
        self.parts.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="white" stroke="#17212b" stroke-width="2"/>')

    def label(self, x, y, value, size=19):
        w = max(28, len(value)*size*.59+14)
        self.rect(x-w/2, y-size+1, w, size+9, stroke='none')
        self.text(x,y,value,size)

    def save(self, path):
        Path(path).parent.mkdir(parents=True,exist_ok=True)
        Path(path).write_text('\n'.join(self.parts+['</svg>'])+'\n',encoding='utf-8')

    def gate(self, x, y, name, op, inputs, output=None):
        """Вентиль с явно именованными цепями: одинаковое имя = соединение."""
        h = max(54, len(inputs)*23+12)
        self.gate_body(x, y, 78, h, op)
        for i, inp in enumerate(inputs):
            iy = y + (i+1)*h/(len(inputs)+1)
            self.path(f'M{x-32} {iy} H{x}')
            self.text(x-39,iy+5,inp,16,'end')
        end=x+78
        if op=='NOT':
            end+=10
        self.path(f'M{end} {y+h/2} H{x+126}')
        self.text(x+135,y+h/2+5,output or name,17,'start')
        self.text(x+39,y-8,name,15,color='#52616f')
        return h

    def gate_body(self, x, y, w, h, op):
        """Прямоугольное УГО; инверсия обозначена пустым кружком на выходе."""
        self.rect(x,y,w,h)
        self.text(x+w/2,y+h/2+7,{'AND':'&','OR':'1','NOT':'1','BUF':'1'}[op],23)
        if op == 'NOT':
            self.circle(x+w+5,y+h/2,5)
