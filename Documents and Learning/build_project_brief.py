from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path


OUTPUT = Path(__file__).with_name("Project_Overview_and_Learning_Plan.docx")
NAVY = "17365D"
TEAL = "147D84"
PALE = "EAF2F8"


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_text(cell, text, bold=False, color=None, size=9):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    run.bold = bold
    run.font.name = "Aptos"
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    p.add_run(text)
    return p


def numbered(doc, text):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.space_after = Pt(3)
    p.add_run(text)
    return p


doc = Document()
section = doc.sections[0]
section.top_margin = Inches(0.65)
section.bottom_margin = Inches(0.65)
section.left_margin = Inches(0.75)
section.right_margin = Inches(0.75)

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Aptos"
normal.font.size = Pt(10)
normal.font.color.rgb = RGBColor.from_string("263238")
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.08
for style_name, size in (("Title", 25), ("Heading 1", 16), ("Heading 2", 12)):
    style = styles[style_name]
    style.font.name = "Aptos Display" if style_name != "Normal" else "Aptos"
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = RGBColor.from_string(NAVY if style_name != "Heading 2" else TEAL)
    style.paragraph_format.space_before = Pt(12 if style_name != "Title" else 0)
    style.paragraph_format.space_after = Pt(5)

# restrained running footer
footer = section.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
f = footer.add_run("ECE-055  |  Learning brief  |  22 October 2026")
f.font.name = "Aptos"
f.font.size = Pt(8)
f.font.color.rgb = RGBColor.from_string("617080")

p = doc.add_paragraph(style="Title")
p.add_run("E-Waste Collection and Recycling Credit Engine")
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(14)
r = p.add_run("Project overview, demo walkthrough, and learning plan")
r.font.size = Pt(12)
r.font.color.rgb = RGBColor.from_string(TEAL)

callout = doc.add_table(rows=1, cols=1)
callout.autofit = True
shade(callout.cell(0, 0), PALE)
set_cell_text(callout.cell(0, 0),
    "Purpose of this note: help our team understand the assignment and the learning demo we explored. "
    "The files created so far are prototypes for learning; they are not the official project submission.",
    bold=True, color=NAVY, size=10)

doc.add_heading("1. What the project does", level=1)
doc.add_paragraph(
    "An authorised recycler collects discarded electronics from colleges, offices, and households. "
    "This program acts as the recycler's operations engine: it records pickup requests, calculates credits "
    "or amounts payable, assigns accepted pickups to vehicle days, and prints the records and monthly totals."
)
doc.add_paragraph(
    "The required interface is a command-line program driven by input files, with no user interface. "
    "So we plan to use Python 3.10+ and CSV files. A website or front end is not required by the brief."
)

doc.add_heading("2. What goes in and what comes out", level=1)
tbl = doc.add_table(rows=1, cols=2)
tbl.style = "Light Shading Accent 1"
for cell, text in zip(tbl.rows[0].cells, ["Input files", "Program output"]):
    set_cell_text(cell, text, bold=True, color="FFFFFF", size=10)
    shade(cell, NAVY)
row = tbl.add_row().cells
set_cell_text(row[0], "sources.csv: source ID, BULK or HOUSEHOLD, distance from depot\nrates.csv: category, credit per kg, hazardous flag\nrequests.csv: request ID, source ID, item lines")
set_cell_text(row[1], "Credit notes per request\nPickup schedule by vehicle day\nMonthly summary, including certificate lines when eligible")
doc.add_paragraph("Overall flow", style="Heading 2")
flow = doc.add_paragraph()
flow.alignment = WD_ALIGN_PARAGRAPH.CENTER
rr = flow.add_run("CSV files  →  validate  →  calculate  →  schedule  →  print reports")
rr.bold = True
rr.font.color.rgb = RGBColor.from_string(TEAL)

doc.add_heading("3. Business rules in plain language", level=1)
doc.add_paragraph("Business rules are the operating instructions the software must follow. We number them so each can be tied to code, a design decision, and an example.")
rules = [
    ("BR-01", "Category credit", "Weight × the category's rate-card credit per kg."),
    ("BR-02", "Household hazardous handling", "For HOUSEHOLD BATTERY and CRT items, deduct Rs 15/kg instead of credit. BULK gets the rate-card credit for these categories."),
    ("BR-03", "Pickup charge", "Free through 10 km. Beyond that, Rs 12 per km, rounding distance up to a whole km. Waive the charge at 200 kg or more."),
    ("BR-04", "Household minimum", "Refuse HOUSEHOLD requests below 5 kg with BELOW_MINIMUM. Exactly 5 kg qualifies. BULK has no minimum."),
    ("BR-05", "Vehicle day capacity", "At most 1,200 kg and 8 stops per day. Process requests in order and select the earliest day that fits."),
    ("BR-06", "Hazard capacity", "At most 300 kg hazardous material per day. Check this together with weight and stops."),
    ("BR-07", "Net amount", "Credits − handling deductions − pickup charge. Round to whole rupees. A negative net is shown as AMOUNT_PAYABLE by the source."),
    ("BR-08", "Monthly certificate", "A source reaching at least 500 kg collected in the month receives a RECYCLING_CERTIFICATE line."),
]
rule_table = doc.add_table(rows=1, cols=3)
rule_table.style = "Table Grid"
for c, text in zip(rule_table.rows[0].cells, ["ID", "Rule", "Meaning"]):
    set_cell_text(c, text, bold=True, color="FFFFFF", size=9)
    shade(c, NAVY)
for rid, title, desc in rules:
    cells = rule_table.add_row().cells
    set_cell_text(cells[0], rid, bold=True, color=TEAL)
    set_cell_text(cells[1], title, bold=True)
    set_cell_text(cells[2], desc)

doc.add_heading("4. Demo walkthrough", level=1)
doc.add_paragraph(
    "The learning demo used three small CSV files and a Python script. Each request contains item lines written as "
    "CATEGORY:COUNT:TOTAL_WEIGHT_KG, separated by semicolons. For example, IT:2:10 means two IT items with 10 kg total line weight."
)
examples = [
    ("R001: household, 5 kg total, exactly 10 km", "Meets the 5 kg minimum; 10 km is free. The 1 kg battery is deducted at Rs 15/kg. IT credit Rs 400 − battery deduction Rs 15 = Rs 385."),
    ("R002: bulk, 10 kg, 13.2 km", "Distance rounds up to 14 km. Four km beyond the free 10 km costs Rs 48. Rs 1,000 credit − Rs 48 charge = Rs 952."),
    ("R003: bulk, exactly 200 kg", "Pickup charge is waived because the total weight reaches 200 kg."),
    ("R004: household, 4 kg", "Refused with BELOW_MINIMUM."),
    ("R005: household, 5 kg of batteries", "Meets the minimum. The Rs 15/kg handling deduction exceeds the category credit, so Rs 75 is shown as AMOUNT_PAYABLE."),
]
ex_table = doc.add_table(rows=1, cols=2)
ex_table.style = "Light Shading Accent 1"
for c, text in zip(ex_table.rows[0].cells, ["Example", "What the rules do"]):
    set_cell_text(c, text, bold=True, color="FFFFFF", size=9)
    shade(c, TEAL)
for left, right in examples:
    cells = ex_table.add_row().cells
    set_cell_text(cells[0], left, bold=True)
    set_cell_text(cells[1], right)

doc.add_heading("5. How scheduling checks capacity", level=1)
doc.add_paragraph(
    "For every accepted request, the scheduler scans days from earliest to latest. A request fits only when adding it keeps "
    "all three totals within limits: stop count ≤ 8, total weight ≤ 1,200 kg, and hazardous weight ≤ 300 kg. "
    "If even one limit would be exceeded, try the next day. This is the key scheduling idea to explain in the viva."
)
doc.add_paragraph(
    "The brief's 350 kg all-battery edge case is larger than the 300 kg hazardous limit for an entire day. "
    "If requests must stay whole, moving it to another day cannot help. The demo provisionally refuses it as "
    "EXCEEDS_DAILY_HAZARD_LIMIT; we will confirm that policy with the instructor before treating it as final."
)

doc.add_heading("6. Learning status and decisions to confirm", level=1)
bullet(doc, "All code and files created so far are practice prototypes, not the official submission. Keep them separate from the official version once that work begins.")
bullet(doc, "Python is our current preference because it is easier for us to read, understand, and explain; the assignment permits Python 3.10+.")
bullet(doc, "CSV is a proposed input format, not yet confirmed against the instructor's Week 2 files.")
bullet(doc, "We need to confirm whether item weight is total line weight or per-item weight, how exact output should be formatted, and how an indivisible request above a daily limit should be handled.")
bullet(doc, "The brief says amounts are rounded to whole rupees; the exact midpoint rounding convention should be confirmed if sample outputs expose it.")
bullet(doc, "The community demo uses shared household collection points: nearby homes pool small contributions before one pickup request is submitted. This does not remove BR-04; the combined request must still reach 5 kg.")
bullet(doc, "The five holdout requests are not hidden computer files. They are R016-R020 in community_demo/requests.csv; only their expected answers are withheld from the visible answer file.")

doc.add_heading("7. Community collection demo", level=1)
doc.add_paragraph(
    "The larger learning demo has 15 sources: 9 shared household collection points across 3 residential areas and 6 BULK locations. "
    "It contains 20 requests for one illustrative month. The first 15 have visible expected output; the last 5 are practice holdouts. "
    "The values and rate card are synthetic examples, not measured local data."
)
doc.add_paragraph(
    "The first seven visible requests total 1,150 kg over 7 stops. The next 60 kg request cannot fit that day, so it moves to Day 2. "
    "Later, the scheduler may still place a request on an earlier day if all stop, weight, and hazardous limits fit. "
    "The visible monthly summary also demonstrates a certificate when one source reaches 550 kg."
)
doc.add_paragraph(
    "To read the terminal report more easily, run the command with --friendly. It prints full source names and labels each value. "
    "The compact report remains available for comparison with the assignment's exact-output expectations."
)

doc.add_heading("8. Planned next steps", level=1)
for text in [
    "Continue learning the demo code line by line, starting with its data classes and CSV loading; practice reading the friendly report.",
    "Ask the instructor about the unresolved interpretations and obtain the provided sample files and visible expected outputs.",
    "Complete the Week 1 design: numbered business rules, entities and relationships, request state flow, and a short decision log.",
    "Only after the design is understood, create the real project separately from the learning demo.",
    "Implement each rule in small, explainable pieces; check each rule and edge case against expected results.",
    "Compare the final printed reports with the instructor's expected output, then prepare the GitHub submission phase by phase.",
    "After core requirements match, consider optional stretch goals such as multiple vehicle capacities or an EPR category-tonnage report.",
]:
    numbered(doc, text)

doc.add_paragraph()
closing = doc.add_paragraph()
closing.paragraph_format.space_before = Pt(5)
run = closing.add_run("Shared understanding: first learn the problem and the code; then build the official version from confirmed requirements.")
run.bold = True
run.font.color.rgb = RGBColor.from_string(NAVY)

doc.save(OUTPUT)
print(OUTPUT)
