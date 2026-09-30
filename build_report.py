"""Build report PDF from REPORT.md. Requires reportlab; tool itself does not."""
import csv
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether


def main():
    root = Path(__file__).parent
    source = (root / 'REPORT.md').read_text(encoding='utf-8')
    table_md = (root / 'results' / 'table.md').read_text()
    source = source.replace('<!-- RESULTS_TABLE -->', table_md.strip())
    (root / 'REPORT.md').write_text(source, encoding='utf-8')
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'Helvetica'
    styles['Normal'].fontSize = 10
    styles['Normal'].leading = 14
    styles['Normal'].spaceAfter = 8
    for name in ['Title', 'Heading1', 'Heading2']:
        styles[name].textColor = colors.black
    styles['Title'].fontSize = 22
    styles['Title'].leading = 27
    styles['Heading1'].fontSize = 15
    styles['Heading1'].spaceBefore = 14
    styles['Heading2'].fontSize = 12
    story = []
    lines = source.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1; continue
        if line.startswith('|'):
            rows = []
            while index < len(lines) and lines[index].startswith('|'):
                if not lines[index].startswith('|---'):
                    rows.append([cell.strip().replace('_', ' ') for cell in lines[index].strip('|').split('|')])
                index += 1
            wrapped = [[Paragraph(escape(cell), styles['Normal']) for cell in row] for row in rows]
            table = Table(wrapped, colWidths=[112, 64, 64, 64, 78, 78], repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8edf2')),
                ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#d9d9d9')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.extend([KeepTogether([table]), Spacer(1, 12), comparison_chart(root), Spacer(1, 10)])
            continue
        if line.startswith('# '):
            style, text = styles['Title'], line[2:]
        elif line.startswith('## '):
            style, text = styles['Heading1'], line[3:]
        elif line.startswith('### '):
            style, text = styles['Heading2'], line[4:]
        else:
            style, text = styles['Normal'], line
        story.append(Paragraph(escape(text), style))
        index += 1
    def footer(canvas, document):
        canvas.setFont('Helvetica', 8)
        canvas.drawString(38, 25, '41052 | Canonical Huffman compressor | Benjamin Jones')
        canvas.drawRightString(A4[0] - 38, 25, str(document.page))
    SimpleDocTemplate(str(root / 'REPORT.pdf'), pagesize=A4,
                      leftMargin=38, rightMargin=38, topMargin=38, bottomMargin=42,
                      title='Canonical Huffman file compressor', author='Benjamin Jones').build(story, onFirstPage=footer, onLaterPages=footer)
    print('Built REPORT.pdf')


def comparison_chart(root):
    with (root / 'results' / 'benchmark.csv').open() as source:
        rows = list(csv.DictReader(source))
    names = ['single_symbol', 'repeated_text', 'skewed_symbols', 'uniform_bytes', 'random_bytes', 'source_code']
    lookup = {(row['dataset'], row['codec']): float(row['ratio']) for row in rows if row['ratio']}
    drawing = Drawing(500, 240)
    drawing.add(String(10, 224, 'Total archive size / input size (lower is better)', fontName='Helvetica-Bold', fontSize=11))
    chart = VerticalBarChart()
    chart.x, chart.y, chart.width, chart.height = 40, 62, 440, 140
    chart.data = [[lookup[(name, codec)] for name in names] for codec in ['Huffman', 'gzip']]
    chart.categoryAxis.categoryNames = ['Single byte', 'Repeated text', 'Skewed', 'Uniform', 'Random', 'Source']
    chart.categoryAxis.labels.fontSize = 8
    chart.categoryAxis.labels.angle = 20
    chart.valueAxis.valueMin, chart.valueAxis.valueMax, chart.valueAxis.valueStep = 0, 1.1, 0.2
    chart.valueAxis.labels.fontSize = 8
    chart.bars[0].fillColor = colors.HexColor('#315b86')
    chart.bars[1].fillColor = colors.HexColor('#d49135')
    drawing.add(chart)
    drawing.add(String(40, 20, 'Blue: HUF1     Orange: gzip level 9     Sizes include metadata', fontSize=9))
    return drawing


if __name__ == '__main__':
    main()
