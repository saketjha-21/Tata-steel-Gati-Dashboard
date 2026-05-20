"""Programmatically builds a boardroom-style leadership deck for Krsnaa Diagnostics.

Output: Krsnaa_Leadership_Presentation.pptx (title + 6 content slides)
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR

# -----------------------------------------------------------------------------
# 1) DESIGN SYSTEM (MBB-inspired, corporate, restrained)
# -----------------------------------------------------------------------------
COLORS = {
    "navy": RGBColor(0, 45, 98),
    "blue": RGBColor(0, 102, 179),
    "sky": RGBColor(232, 242, 252),
    "aqua": RGBColor(0, 153, 204),
    "text": RGBColor(66, 72, 77),
    "muted": RGBColor(117, 126, 135),
    "line": RGBColor(200, 212, 225),
    "panel": RGBColor(246, 249, 253),
    "white": RGBColor(255, 255, 255),
}

FONT_MAIN = "Calibri"
FONT_ANNOTATION = "Segoe Script"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)


def set_text_style(paragraph, size=12, bold=False, color=None, align=None, font=FONT_MAIN, italic=False):
    paragraph.font.name = font
    paragraph.font.size = Pt(size)
    paragraph.font.bold = bold
    paragraph.font.italic = italic
    paragraph.font.color.rgb = color or COLORS["text"]
    if align is not None:
        paragraph.alignment = align


def add_header(slide, title, subtitle=None):
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.72))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS["navy"]
    header.line.fill.background()
    tf = header.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = title
    set_text_style(p, size=20, bold=True, color=COLORS["white"], align=PP_ALIGN.LEFT)

    if subtitle:
        tag = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.4), Inches(0.1), Inches(2.8), Inches(0.48))
        tag.fill.solid(); tag.fill.fore_color.rgb = COLORS["aqua"]
        tag.line.fill.background()
        tag.text_frame.text = subtitle
        set_text_style(tag.text_frame.paragraphs[0], size=11, bold=True, color=COLORS["white"], align=PP_ALIGN.CENTER)


def add_text(slide, x, y, w, h, text, size=12, bold=False, color=None, align=PP_ALIGN.LEFT, italic=False, font=FONT_MAIN):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = text
    set_text_style(p, size=size, bold=bold, color=color, align=align, italic=italic, font=font)
    return box


def panel(slide, x, y, w, h, title=None, fill="white", border="line"):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid(); shp.fill.fore_color.rgb = COLORS[fill]
    shp.line.color.rgb = COLORS[border]
    shp.line.width = Pt(1)
    if title:
        shp.text_frame.text = title
        set_text_style(shp.text_frame.paragraphs[0], size=12, bold=True, color=COLORS["navy"])
    return shp


def add_annotation(slide, x, y, text):
    # Subtle handwritten-style annotation used selectively
    b = add_text(slide, x, y, 2.6, 0.4, text, size=11, color=COLORS["aqua"], italic=True, font=FONT_ANNOTATION)
    return b


# -----------------------------------------------------------------------------
# Title slide
# -----------------------------------------------------------------------------
s = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s, "Observations & Organizational Analysis", "Leadership Brief")
add_text(s, 0.9, 1.45, 8.0, 0.8, "Management Trainee Review", 28, True, COLORS["navy"])
add_text(s, 0.9, 2.2, 8.0, 1.0, "Krsnaa Diagnostics Ltd\nSaket Jha", 16, False, COLORS["text"])

hero = panel(s, 8.9, 1.35, 3.8, 5.2, fill="sky", border="blue")
hero.text_frame.clear()
hero.text_frame.text = "Healthcare Operations\nDiagnostic Network\nExecution Consistency"
for p in hero.text_frame.paragraphs:
    set_text_style(p, size=16, bold=True, color=COLORS["navy"], align=PP_ALIGN.CENTER)

# -----------------------------------------------------------------------------
# Slide 1
# -----------------------------------------------------------------------------
s = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s, "1. Underlying Organizational Frictions")

outside = panel(s, 8.55, 0.95, 4.55, 1.85, fill="panel", border="blue")
outside.text_frame.text = (
    "Factors largely outside operational influence\n"
    "• Long receivable cycles\n"
    "• Dependence on PPP model\n"
    "• Limited retail contribution\n"
    "• PAT growth inconsistency"
)
for i, p in enumerate(outside.text_frame.paragraphs):
    set_text_style(p, size=11 if i else 12, bold=(i == 0), color=COLORS["text"])

add_text(s, 0.85, 1.02, 7.2, 0.7, "Observed challenges appear linked to fragmented execution structures", 16, True, COLORS["navy"])

nodes = [
    "Technology\nfragmentation",
    "Multiple\nsystems",
    "Manual\nworkarounds",
    "Process\ninconsistency",
    "Operational\nvariability",
]
start_x = 0.85
for idx, n in enumerate(nodes):
    card = panel(s, start_x + idx * 2.45, 2.45, 2.2, 1.1, fill="white", border="blue")
    card.text_frame.clear(); card.text_frame.text = n
    for p in card.text_frame.paragraphs:
        set_text_style(p, size=12, bold=True, color=COLORS["navy"], align=PP_ALIGN.CENTER)

for i in range(4):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(3.03 + i * 2.45), Inches(3.0), Inches(3.3 + i * 2.45), Inches(3.0))
    c.line.color.rgb = COLORS["aqua"]
    c.line.width = Pt(2.5)

add_text(s, 0.85, 3.95, 12.2, 0.7, "• Slow or incomplete automation implementation   • Teams relying on multiple systems", 11)
add_text(s, 0.85, 4.35, 12.2, 0.7, "• Gaps between systems and workflows   • Software adoption inconsistency", 11)
add_annotation(s, 9.95, 3.55, "root friction")

foot = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.42), Inches(12.0), Inches(0.62))
foot.fill.solid(); foot.fill.fore_color.rgb = COLORS["sky"]
foot.line.fill.background()
foot.text_frame.text = "Recurring theme across departments: technology exists, but implementation depth varies."
set_text_style(foot.text_frame.paragraphs[0], size=12, bold=True, color=COLORS["navy"], align=PP_ALIGN.LEFT)

# -----------------------------------------------------------------------------
# Slide 2
# -----------------------------------------------------------------------------
s = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s, "2. Execution Inefficiencies + Resistance to Change")
add_text(s, 0.85, 1.02, 6.2, 0.5, "Operational Inefficiencies", 16, True, COLORS["navy"])

steps = ["Duplicate efforts", "Escalation of routine tasks", "Decision layers for small actions", "Uneven process ownership"]
for i, t in enumerate(steps):
    y = 1.58 + i * 1.02
    chevron = s.shapes.add_shape(MSO_SHAPE.CHEVRON, Inches(0.85), Inches(y), Inches(6.1), Inches(0.78))
    chevron.fill.solid(); chevron.fill.fore_color.rgb = COLORS["sky"]
    chevron.line.color.rgb = COLORS["blue"]
    chevron.text_frame.text = t
    set_text_style(chevron.text_frame.paragraphs[0], size=11.5, bold=True, color=COLORS["navy"])

add_annotation(s, 5.45, 5.7, "friction loops")

add_text(s, 7.1, 1.02, 5.4, 0.5, "Resistance to Change", 16, True, COLORS["navy"])
tri = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(8.0), Inches(2.0), Inches(3.45), Inches(3.1))
tri.fill.solid(); tri.fill.fore_color.rgb = COLORS["panel"]
tri.line.color.rgb = COLORS["blue"]

add_text(s, 9.12, 2.22, 2.2, 0.35, "Leadership", 11, True)
add_text(s, 8.62, 3.1, 3.2, 0.35, "Middle management", 11, True)
add_text(s, 8.93, 3.95, 2.7, 0.35, "Ground teams", 11, True)
add_text(s, 7.05, 5.12, 5.7, 1.2, "• Information silos\n• Change uncertainty\n• Limited cross-level alignment\n• Need stronger communication loops", 11)
add_text(s, 7.1, 4.72, 5.5, 0.32, "Different perspectives create execution gaps", 10.5, False, COLORS["aqua"], italic=True)
add_text(s, 0.85, 6.7, 12.0, 0.35, "Execution barriers often appear behavioral as much as structural.", 11.5, True, COLORS["text"])

# -----------------------------------------------------------------------------
# Slide 3
# -----------------------------------------------------------------------------
s = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s, "3. Revenue Variability and Referral Dependence")
add_text(s, 0.85, 1.0, 12.0, 0.5, "Infrastructure strength is not translating uniformly into utilization", 16, True, COLORS["navy"])

funnel = [("Machine utilization", 4.8), ("Referral flow", 4.1), ("Patient inflow", 3.3), ("Revenue consistency", 2.6)]
for i, (label, width) in enumerate(funnel):
    y = 1.75 + i * 0.82
    f = s.shapes.add_shape(MSO_SHAPE.TRAPEZOID, Inches(1.1 + (4.8 - width) / 2), Inches(y), Inches(width), Inches(0.72))
    f.fill.solid(); f.fill.fore_color.rgb = COLORS["sky"]
    f.line.color.rgb = COLORS["blue"]
    f.text_frame.text = label
    set_text_style(f.text_frame.paragraphs[0], size=11.5, bold=True, color=COLORS["navy"], align=PP_ALIGN.CENTER)

right = panel(s, 6.2, 1.75, 6.35, 4.95, fill="white", border="blue")
right.text_frame.text = (
    "Doctor Referral Challenge\n\n"
    "Current market perception often positions Krsnaa primarily as affordability-led.\n\n"
    "Directional ideas:\n"
    "• Clinical partnerships\n"
    "• Doctor ecosystem engagement\n"
    "• Digital consultation alliances\n"
    "• Sales capability enhancement"
)
for i, p in enumerate(right.text_frame.paragraphs):
    set_text_style(p, size=11 if i else 12, bold=(i == 0), color=COLORS["navy"] if i == 0 else COLORS["text"])

add_annotation(s, 2.0, 5.22, "utilization gap")
add_text(s, 0.85, 6.62, 12.0, 0.36, "Current ideas are directional observations rather than recommendations.", 11, True, COLORS["muted"])

# -----------------------------------------------------------------------------
# Slide 4
# -----------------------------------------------------------------------------
s = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s, "4. Retail Presence and Market Awareness")
add_text(s, 0.85, 1.0, 12.0, 0.5, "Infrastructure scale exists ahead of brand recall", 16, True, COLORS["navy"])

retail = panel(s, 0.85, 1.82, 5.25, 3.95, fill="panel", border="blue")
retail.text_frame.text = "Retail challenge\n• Limited public awareness\n• Strong local players\n• Dependence on partnerships"

mkt = panel(s, 7.1, 1.82, 5.45, 3.95, fill="white", border="blue")
mkt.text_frame.text = (
    "Marketing observations\n"
    "• Awareness efforts still evolving\n"
    "• Opportunity in radiology positioning\n"
    "• Local market visibility opportunities\n"
    "• External support may accelerate execution"
)
for shp in (retail, mkt):
    for i, p in enumerate(shp.text_frame.paragraphs):
        set_text_style(p, size=11 if i else 12, bold=(i == 0), color=COLORS["navy"] if i == 0 else COLORS["text"])

arrow = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(6.12), Inches(3.74), Inches(7.05), Inches(3.74))
arrow.line.color.rgb = COLORS["aqua"]; arrow.line.width = Pt(2.7)
add_annotation(s, 5.62, 3.18, "awareness bridge")

add_text(s, 0.85, 6.5, 12.0, 0.4, "Growth infrastructure exists; awareness and positioning remain the constraint.", 12, True, COLORS["text"])

# -----------------------------------------------------------------------------
# Slide 5
# -----------------------------------------------------------------------------
s = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s, "5. Scorecard Analysis — Key Findings", subtitle="Data Snapshot")

metric = panel(s, 0.85, 1.2, 4.05, 2.3, fill="navy", border="navy")
metric.text_frame.clear()
metric.text_frame.text = "Revenue Risk\nContribution\n42%"
for i, p in enumerate(metric.text_frame.paragraphs):
    set_text_style(p, size=16 if i < 2 else 30, bold=True, color=COLORS["white"], align=PP_ALIGN.CENTER)

kpi1 = panel(s, 0.85, 3.7, 1.95, 1.05, fill="sky", border="line")
kpi1.text_frame.text = "Material Cost\n11.6%"
kpi2 = panel(s, 2.95, 3.7, 1.95, 1.05, fill="sky", border="line")
kpi2.text_frame.text = "Process KPIs\n7.1%"
for box in (kpi1, kpi2):
    for i, p in enumerate(box.text_frame.paragraphs):
        set_text_style(p, size=11 if i == 0 else 18, bold=True, color=COLORS["navy"], align=PP_ALIGN.CENTER)

var = panel(s, 5.15, 1.2, 3.25, 3.55, fill="panel", border="blue")
var.text_frame.text = "Variability by role\n\nDistrict Coordinator CV: 0.58\nCluster Manager CV: 0.37"
for i, p in enumerate(var.text_frame.paragraphs):
    set_text_style(p, size=12 if i == 0 else 11, bold=(i == 0), color=COLORS["text"])

find = panel(s, 8.65, 1.2, 3.9, 4.95, fill="white", border="blue")
find.text_frame.text = (
    "Findings\n"
    "• High variability rather than weak capability\n"
    "• Revenue performance differs significantly across centers\n"
    "• Technology adoption instability observed\n"
    "• Execution often dependent on individuals"
)
for i, p in enumerate(find.text_frame.paragraphs):
    set_text_style(p, size=12 if i == 0 else 11, bold=(i == 0), color=COLORS["navy"] if i == 0 else COLORS["text"])

add_annotation(s, 9.55, 6.22, "consistency over heroics")
add_text(s, 0.85, 6.52, 12.0, 0.36, "Challenge appears to be standardization and consistency—not capability.", 12, True, COLORS["text"])

# -----------------------------------------------------------------------------
# Slide 6
# -----------------------------------------------------------------------------
s = prs.slides.add_slide(prs.slide_layouts[6])
add_header(s, "6. Summary and Management Trainee Observations")

for i, label in enumerate(["Technology", "Execution", "Revenue"]):
    b = panel(s, 1.15 + i * 3.35, 1.52, 2.65, 0.98, fill="sky", border="blue")
    b.text_frame.text = label
    set_text_style(b.text_frame.paragraphs[0], size=14, bold=True, color=COLORS["navy"], align=PP_ALIGN.CENTER)

cons = panel(s, 9.45, 1.42, 2.75, 1.2, fill="navy", border="navy")
cons.text_frame.text = "Consistency"
set_text_style(cons.text_frame.paragraphs[0], size=18, bold=True, color=COLORS["white"], align=PP_ALIGN.CENTER)

for x in [3.8, 7.15, 10.45]:
    link = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(2.01), Inches(9.45), Inches(2.01))
    link.line.color.rgb = COLORS["aqua"]; link.line.width = Pt(2.2)

obs = panel(s, 0.85, 3.05, 12.35, 2.9, fill="white", border="blue")
obs.text_frame.text = (
    "Management trainee observations\n"
    "• Program structure remained highly flexible\n"
    "• Practical exposure varied by department\n"
    "• Department expectations were not always aligned\n"
    "• Timelines and ownership structures could improve"
)
for i, p in enumerate(obs.text_frame.paragraphs):
    set_text_style(p, size=12 if i == 0 else 11, bold=(i == 0), color=COLORS["navy"] if i == 0 else COLORS["text"])

add_text(s, 0.85, 6.42, 12.0, 0.45,
         "The organization appears fundamentally strong; greater standardization may unlock more consistent execution at scale.",
         12, True, COLORS["text"])

out = "Krsnaa_Leadership_Presentation.pptx"
prs.save(out)
print(f"Created {out}")
