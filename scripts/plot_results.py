"""Render committed CSV results with ReportLab. No circuit simulations are run."""
from pathlib import Path
import csv
import math
from reportlab.graphics.shapes import Drawing, String, Line, Rect
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics import renderSVG
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT/'simulations/figures'
OUTPUT.mkdir(exist_ok=True)
PALETTE = [colors.HexColor('#d65b36'), colors.HexColor('#007d83')]


def read(name):
    with (ROOT/'simulations/results'/name).open() as stream:
        return list(csv.DictReader(stream))


def draw(name, title, subtitle, series, x_label, y_label, x_range, y_range, x_format):
    drawing = Drawing(920, 430)
    drawing.add(Rect(0, 0, 920, 430, fillColor=colors.white, strokeColor=None))
    drawing.add(String(62, 401, title, fontName='Helvetica-Bold',fontSize=20,fillColor=colors.HexColor('#17324d')))
    drawing.add(String(62, 379, subtitle, fontSize=10,fillColor=colors.HexColor('#526477')))
    plot = LinePlot()
    plot.x, plot.y, plot.width, plot.height = 66, 77, 800, 260
    plot.data = series
    plot.joinedLines = 1
    for i in range(2):
        plot.lines[i].strokeColor = PALETTE[i]
        plot.lines[i].strokeWidth = 1.8
    for axis in [plot.xValueAxis, plot.yValueAxis]:
        axis.strokeColor = colors.HexColor('#9caab5')
        axis.labels.fontSize = 9
        axis.visibleGrid = True
        axis.gridStrokeColor = colors.HexColor('#e4eaf0')
    plot.xValueAxis.valueMin,plot.xValueAxis.valueMax,plot.xValueAxis.valueStep = x_range
    plot.xValueAxis.labelTextFormat = x_format
    plot.yValueAxis.valueMin,plot.yValueAxis.valueMax,plot.yValueAxis.valueStep = y_range
    drawing.add(plot)
    drawing.add(String(440, 45, x_label,fontSize=11,textAnchor='middle'))
    drawing.add(String(66, 348, y_label,fontSize=10))
    for i, label in enumerate(['Original KiCad circuit','Experimental variant']):
        x = 250+i*250
        drawing.add(Line(x,20,x+25,20,strokeColor=PALETTE[i],strokeWidth=2.5))
        drawing.add(String(x+33,16,label,fontSize=10))
    renderSVG.drawToFile(drawing,str(OUTPUT/name))


ac = []
transient = []
for name in ['baseline','candidate']:
    rows = read(f'{name}-ac-loaded.csv')
    ac.append([(math.log10(float(r['frequency_hz'])),20*math.log10(math.hypot(float(r['vout_real_v']),float(r['vout_imag_v']))))
               for r in rows[::4]])
    rows = read(f'{name}-transient.csv')
    start = float(rows[0]['time_s'])
    transient.append([((float(r['time_s'])-start)*1e6,float(r['vout_v'])) for r in rows[::2]
                      if (float(r['time_s'])-start)*1e6 <= 40.01])
draw('ac-comparison.svg','Loaded voltage gain','ngspice 44 | 27 C | Source AC amplitude 1 V | Original circuit and separate SPICE variant',
     ac,'Frequency (Hz, logarithmic scale)','Voltage gain (dB)',(0,8,1),(-10,80,15),
     lambda value: ['1','10','100','1k','10k','100k','1M','10M','100M'][round(value)])
draw('transient-comparison.svg','Output waveform: distortion remains','100 kHz | Original input: 1 mV peak | Variant input: 0.75 mV peak | Final window of an 80 ms run',
     transient,'Time within final measurement window (us)','Output voltage (V)',(0,40,5),(-1,1,0.5),'%.0f')
print('Generated two figures from committed CSV data.')
