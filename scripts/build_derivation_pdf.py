"""PDF решения 08h из Markdown; формулы набирает Matplotlib mathtext."""
import io
import re
from html import escape
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
from matplotlib.font_manager import FontProperties
from matplotlib.mathtext import math_to_image
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, PageBreak, Spacer, Table, TableStyle
from build_pdf import font_path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'docs/08h_output_rs_derivation.md'
OUTPUT = ROOT/'output/pdf/ALM_variant5_output_rs_derivation.pdf'
WIDTH = A4[0]-84


def inline(text):
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', escape(text))
    for symbol in '∨∧':
        text = text.replace(symbol, f'<font name="AlmMath">{symbol}</font>')
    return text


def main():
    regular = Path(font_path())
    pdfmetrics.registerFont(TTFont('Alm', str(regular)))
    candidates = (regular.with_name('arialbd.ttf'), regular.with_name('DejaVuSans-Bold.ttf'),
                  regular.with_name('Arial Bold.ttf'))
    bold = next((p for p in candidates if p.is_file()), regular)
    pdfmetrics.registerFont(TTFont('AlmBold', str(bold)))
    pdfmetrics.registerFont(TTFont('AlmMath', str(Path(matplotlib.get_data_path())/'fonts/ttf/DejaVuSans.ttf')))
    pdfmetrics.registerFontFamily('Alm', normal='Alm', bold='AlmBold')
    styles = {
        'body': ParagraphStyle('Body', fontName='Alm', fontSize=10, leading=14, spaceAfter=7),
        'h1': ParagraphStyle('Title', fontName='AlmBold', fontSize=18, leading=23, spaceAfter=10, keepWithNext=True),
        'h2': ParagraphStyle('Section', fontName='AlmBold', fontSize=15, leading=19, spaceAfter=10, keepWithNext=True),
        'h3': ParagraphStyle('Function', fontName='AlmBold', fontSize=11, leading=15, spaceBefore=9, spaceAfter=5, keepWithNext=True),
        'cell': ParagraphStyle('Cell', fontName='Alm', fontSize=9.2, leading=12),
        'header': ParagraphStyle('Header', fontName='AlmBold', fontSize=9.2, leading=12),
    }
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    story, formula_sizes = [], []

    def formula(text):
        text = text.replace(r'\bigl', r'\left').replace(r'\bigr', r'\right')
        png = io.BytesIO()
        math_to_image('$'+text+'$', png, prop=FontProperties(size=13), dpi=240, format='png')
        png.seek(0)
        with PILImage.open(png) as im:
            width, height = (n*72/240 for n in im.size)
        scale = min(1, WIDTH/width)
        formula_sizes.append(13*scale)
        assert 13*scale >= 10, ('Formula too small', text)
        png.seek(0)
        picture = Image(png, width=width*scale, height=height*scale)
        picture.hAlign = 'LEFT'
        story.extend((picture, Spacer(1, 7)))

    lines = SOURCE.read_text(encoding='utf-8').splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if line == '<!-- pagebreak -->':
            story.append(PageBreak())
        elif line.startswith('$$'):
            assert line.endswith('$$'), 'Display formulas must occupy one source line'
            formula(line[2:-2])
        elif line.startswith('#'):
            level, text = line.split(' ', 1)
            story.append(Paragraph(inline(text), styles['h'+str(len(level))]))
        elif line.startswith('|'):
            rows = [line]
            while i < len(lines) and lines[i].startswith('|'):
                rows.append(lines[i])
                i += 1
            cells = []
            for row in rows:
                values = [c.strip() for c in row.strip('|').split('|')]
                if all(re.fullmatch(r':?-+:?', v) for v in values):
                    continue
                style = styles['header' if not cells else 'cell']
                cells.append([Paragraph(inline(v), style) for v in values])
            table = Table(cells, colWidths=[WIDTH/len(cells[0])]*len(cells[0]), repeatRows=1)
            table.setStyle(TableStyle([
                ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#9ba3ab')),
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#f0f3f5')),
                ('TOPPADDING',(0,0),(-1,-1),3),
                ('BOTTOMPADDING',(0,0),(-1,-1),3),
            ]))
            story.extend((table, Spacer(1,10)))
        else:
            story.append(Paragraph(inline(line), styles['body']))

    pages = []
    def footer(canvas, document):
        pages.append(document.page)
        canvas.setTitle('АЛМ, вариант 5: вывод функций выходов и возбуждения RS')
        canvas.setAuthor('nef1xx')
        canvas.setFont('Alm',8)
        canvas.setFillColor(colors.HexColor('#53606b'))
        canvas.drawString(42,24,'АЛМ. Вариант 5. Основной автомат Мура S0–S6')
        canvas.drawRightString(A4[0]-42,24,str(document.page))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=42, rightMargin=42,
                                 topMargin=36, bottomMargin=42, invariant=1)
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f'{OUTPUT}: {len(pages)} pages, {len(formula_sizes)} formulas; '
          f'minimum formula size {min(formula_sizes):.1f} pt')


if __name__ == '__main__':
    main()
