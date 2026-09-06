"""PDF-альбом всех схем. Необязательная зависимость: reportlab и Pillow."""
import os
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A3, landscape
from PIL import Image
from build_gallery import TITLES

ROOT=Path(__file__).resolve().parents[1]


def font_path():
    candidates=[os.getenv('ALM_FONT_REGULAR',''), 'C:/Windows/Fonts/arial.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/Library/Fonts/Arial.ttf']
    for candidate in candidates:
        if candidate and Path(candidate).is_file():return candidate
    raise RuntimeError('Задайте ALM_FONT_REGULAR: путь к TTF с кириллицей')


def main():
    out=ROOT/'output/ALM_variant5_schemes.pdf'
    out.parent.mkdir(exist_ok=True)
    pdfmetrics.registerFont(TTFont('Alm',font_path()))
    c=canvas.Canvas(str(out),pagesize=A3,invariant=1)
    c.setTitle('АЛМ вариант 5 — альбом схем автомата Мура')
    c.setAuthor('nef1xx')
    width,height=A3
    c.setFont('Alm',29);c.drawString(60,height-110,'АЛМ. Вариант 5. Автомат Мура')
    c.setFont('Alm',17);c.drawString(60,height-152,'Альбом схем к расчётам и Python-модели')
    lines=['Основной вариант: S0…S6, остановка в S6 до RESET.',
           'Листы 04b и 05c: учебный циклический вариант с общим S0.',
           'Формулы, исходные данные и доказательства: README.md и docs/.',
           'SVG для редактирования и PNG: diagrams/.',
           'Таблицы и список вентилей: data/.',
           'Запуск модели: python -m ulu.cli --demo',
           'Проверка: python -m unittest discover -s tests -v']
    for i,line in enumerate(lines):c.drawString(60,height-213-i*35,line)
    c.setFont('Alm',14)
    for i,(stem,title) in enumerate(TITLES.items()):
        c.drawString(60,height-500-i*27,f'{i+2:02d}. {title}')
    c.showPage()
    for number,(stem,title) in enumerate(TITLES.items(),2):
        image=ROOT/'diagrams'/f'{stem}.png'
        with Image.open(image) as im:iw,ih=im.size
        width,height=landscape(A3) if iw>=ih else A3
        c.setPageSize((width,height))
        c.setFont('Alm',17);c.drawString(35,height-30,f'{number:02d}. {title}')
        scale=min((width-60)/iw,(height-100)/ih)
        w,h=iw*scale,ih*scale
        c.drawImage(str(image),(width-w)/2,50+(height-100-h)/2,w,h,mask='auto')
        c.setFont('Alm',10)
        c.drawString(35,25,f'Вариант 5 • {stem}.svg • полный текст: docs/ и README.md')
        c.showPage()
    c.save()
    print(out)


if __name__=='__main__':main()
