#!/usr/bin/env python3
"""
HALYK PETROLEUM LLP – Approved Official Scope of Work
Professional corporate document generator using ReportLab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, Frame, PageTemplate, BaseDocTemplate,
    ListFlowable, ListItem, PageBreak, NextPageTemplate, FrameBreak,
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, Line, Circle, String
from reportlab.graphics import renderPDF
import os

# ─── Color Palette (Corporate Oil & Gas Theme) ──────────────────────────────
DARK_BLUE    = HexColor("#0a1628")   # Deep navy (header bg)
NAVY         = HexColor("#102a5c")   # Primary navy
MED_BLUE     = HexColor("#1e4d8c")   # Medium blue
LIGHT_BLUE   = HexColor("#2c7be5")   # Accent blue
SKY          = HexColor("#e8f1fd")   # Very light blue bg
GOLD         = HexColor("#c8952e")   # Gold accent
DARK_GOLD    = HexColor("#a07825")   # Darker gold
WHITE         = HexColor("#ffffff")
OFF_WHITE    = HexColor("#f7f9fc")
DARK_TEXT     = HexColor("#1a1a2e")
MED_TEXT      = HexColor("#4a5568")
LIGHT_TEXT    = HexColor("#718096")
DIVIDER       = HexColor("#d1d9e6")
TABLE_HEAD_BG = HexColor("#102a5c")
TABLE_ALT_BG  = HexColor("#f0f4fa")
GREEN         = HexColor("#27823b")
RED_ACCENT    = HexColor("#c53030")

PAGE_W, PAGE_H = A4


# ─── Company & Document Data ────────────────────────────────────────────────
COMPANY = {
    "name": "HALYK PETROLEUM LLP",
    "tagline": "Dependable Energy, Unmatched Quality",
    "address": "Astana, Baykokyr District, Akzhol Avenue, Building 44, Kazakhstan",
    "phone": "+7 775 218 5914",
    "email": "info@halykpetroleum.kz",
    "website": "www.halykpetroleum.kz",
    "bin": "240640030507",
}

DOC = {
    "title": "APPROVED OFFICIAL SCOPE OF WORK",
    "subtitle": "Oil & Gas Exploration, Refining, and Petroleum Products Supply",
    "doc_no": "HP-SCO-2025-001",
    "revision": "Rev. 03",
    "date": "September 21, 2026",
    "prepared_by": "Engineering & Operations Division",
    "approved_by": "Board of Directors – Halyk Petroleum LLP",
    "classification": "CONFIDENTIAL – INTERNAL USE ONLY",
    "client_ref": "Multiple International Clients",
    "contract_type": "Framework Supply Agreement (FSA)",
    "validity": "24 months from date of approval",
}


# ─── Custom Page Drawing ─────────────────────────────────────────────────────
def draw_cover_page(c, doc):
    """Draw the cover page with dark header block and gold accents."""
    w, h = PAGE_W, PAGE_H

    # Full dark blue header block (top 45%)
    block_h = h * 0.48
    c.setFillColor(DARK_BLUE)
    c.rect(0, h - block_h, w, block_h, fill=1, stroke=0)

    # Gold accent stripe
    c.setFillColor(GOLD)
    c.rect(0, h - block_h - 4 * mm, w, 4 * mm, fill=1, stroke=0)

    # Thin light blue line below gold
    c.setFillColor(LIGHT_BLUE)
    c.rect(0, h - block_h - 5 * mm, w, 1 * mm, fill=1, stroke=0)

    # Company name in white
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(WHITE)
    c.drawCentredString(w / 2, h - 45 * mm, COMPANY["name"])

    # Tagline
    c.setFont("Helvetica-Oblique", 13)
    c.setFillColor(GOLD)
    c.drawCentredString(w / 2, h - 55 * mm, COMPANY["tagline"])

    # Divider line
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(w / 2 - 60 * mm, h - 62 * mm, w / 2 + 60 * mm, h - 62 * mm)

    # Document title
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(WHITE)
    c.drawCentredString(w / 2, h - 80 * mm, DOC["title"])

    # Subtitle
    c.setFont("Helvetica", 12)
    c.setFillColor(HexColor("#b0c4de"))
    c.drawCentredString(w / 2, h - 92 * mm, DOC["subtitle"])

    # Document info box
    box_y = h - block_h + 30 * mm
    box_x = 30 * mm
    box_w = w - 60 * mm
    box_h_info = 55 * mm

    # Info box background
    c.setFillColor(HexColor("#0d1f3c"))
    c.roundRect(box_x, box_y - box_h_info, box_w, box_h_info, 3 * mm, fill=1, stroke=0)

    # Info box border
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.roundRect(box_x, box_y - box_h_info, box_w, box_h_info, 3 * mm, fill=0, stroke=1)

    # Info text
    info_items = [
        ("Document No:", DOC["doc_no"]),
        ("Revision:", DOC["revision"]),
        ("Date:", DOC["date"]),
        ("Classification:", DOC["classification"]),
    ]
    y_pos = box_y - 10 * mm
    for label, value in info_items:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(GOLD)
        c.drawString(box_x + 8 * mm, y_pos, label)
        c.setFont("Helvetica", 10)
        c.setFillColor(WHITE)
        c.drawString(box_x + 50 * mm, y_pos, value)
        y_pos -= 10 * mm

    # Bottom section - approval block
    bottom_y = 45 * mm
    c.setFont("Helvetica", 9)
    c.setFillColor(MED_TEXT)

    # Approval info
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(NAVY)
    c.drawString(30 * mm, bottom_y + 20 * mm, "Prepared By:")
    c.setFont("Helvetica", 10)
    c.setFillColor(MED_TEXT)
    c.drawString(30 * mm, bottom_y + 12 * mm, DOC["prepared_by"])

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(NAVY)
    c.drawString(w / 2 + 10 * mm, bottom_y + 20 * mm, "Approved By:")
    c.setFont("Helvetica", 10)
    c.setFillColor(MED_TEXT)
    c.drawString(w / 2 + 10 * mm, bottom_y + 12 * mm, DOC["approved_by"])

    # Signature lines
    c.setStrokeColor(DIVIDER)
    c.setLineWidth(0.5)
    c.line(30 * mm, bottom_y + 8 * mm, 90 * mm, bottom_y + 8 * mm)
    c.line(w / 2 + 10 * mm, bottom_y + 8 * mm, w / 2 + 70 * mm, bottom_y + 8 * mm)

    c.setFont("Helvetica", 8)
    c.setFillColor(LIGHT_TEXT)
    c.drawString(30 * mm, bottom_y + 3 * mm, "Signature & Date")
    c.drawString(w / 2 + 10 * mm, bottom_y + 3 * mm, "Signature & Date")

    # Footer
    c.setFont("Helvetica", 7)
    c.setFillColor(LIGHT_TEXT)
    c.drawCentredString(w / 2, 12 * mm, f"{COMPANY['name']}  •  {COMPANY['website']}  •  {DOC['doc_no']}  •  {DOC['classification']}")


def draw_content_page(c, doc):
    """Draw header/footer for content pages."""
    w, h = PAGE_W, PAGE_H

    # Top header bar
    c.setFillColor(NAVY)
    c.rect(0, h - 14 * mm, w, 14 * mm, fill=1, stroke=0)

    # Gold accent under header
    c.setFillColor(GOLD)
    c.rect(0, h - 15 * mm, w, 1 * mm, fill=1, stroke=0)

    # Header text
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(WHITE)
    c.drawString(20 * mm, h - 10 * mm, COMPANY["name"])

    c.setFont("Helvetica", 8)
    c.setFillColor(GOLD)
    c.drawRightString(w - 20 * mm, h - 10 * mm, f"{DOC['doc_no']}  |  {DOC['revision']}  |  {DOC['date']}")

    # Left gold accent bar
    c.setFillColor(GOLD)
    c.rect(0, 20 * mm, 3 * mm, h - 35 * mm, fill=1, stroke=0)

    # Footer
    c.setStrokeColor(DIVIDER)
    c.setLineWidth(0.3)
    c.line(20 * mm, 16 * mm, w - 20 * mm, 16 * mm)

    c.setFont("Helvetica", 7)
    c.setFillColor(LIGHT_TEXT)
    c.drawString(20 * mm, 10 * mm, f"{DOC['classification']}")
    c.drawCentredString(w / 2, 10 * mm, f"{COMPANY['name']}")
    c.drawRightString(w - 20 * mm, 10 * mm, f"Page {doc.page}")

    # Bottom accent line
    c.setFillColor(NAVY)
    c.rect(0, 0, w, 3 * mm, fill=1, stroke=0)


# ─── Styles ──────────────────────────────────────────────────────────────────
def get_styles():
    return {
        "h1": ParagraphStyle(
            "H1", fontName="Helvetica-Bold", fontSize=16, leading=22,
            textColor=NAVY, spaceBefore=8 * mm, spaceAfter=3 * mm,
        ),
        "h2": ParagraphStyle(
            "H2", fontName="Helvetica-Bold", fontSize=13, leading=18,
            textColor=NAVY, spaceBefore=6 * mm, spaceAfter=2.5 * mm,
        ),
        "h3": ParagraphStyle(
            "H3", fontName="Helvetica-Bold", fontSize=11, leading=15,
            textColor=MED_BLUE, spaceBefore=4 * mm, spaceAfter=2 * mm,
        ),
        "body": ParagraphStyle(
            "Body", fontName="Helvetica", fontSize=9.5, leading=14,
            textColor=DARK_TEXT, alignment=TA_JUSTIFY, spaceAfter=2 * mm,
        ),
        "body_bold": ParagraphStyle(
            "BodyBold", fontName="Helvetica-Bold", fontSize=9.5, leading=14,
            textColor=DARK_TEXT, alignment=TA_JUSTIFY, spaceAfter=2 * mm,
        ),
        "bullet": ParagraphStyle(
            "Bullet", fontName="Helvetica", fontSize=9.5, leading=14,
            textColor=MED_TEXT, leftIndent=14, bulletIndent=0,
            spaceBefore=1 * mm, spaceAfter=1 * mm,
        ),
        "bullet_bold_prefix": ParagraphStyle(
            "BulletBold", fontName="Helvetica", fontSize=9.5, leading=14,
            textColor=MED_TEXT, leftIndent=14, bulletIndent=0,
            spaceBefore=1 * mm, spaceAfter=1 * mm,
        ),
        "note": ParagraphStyle(
            "Note", fontName="Helvetica-Oblique", fontSize=9, leading=13,
            textColor=LIGHT_TEXT, leftIndent=10 * mm, rightIndent=10 * mm,
            spaceBefore=3 * mm, spaceAfter=3 * mm,
            borderColor=LIGHT_BLUE, borderWidth=0.5, borderPadding=4,
        ),
        "table_head": ParagraphStyle(
            "TableHead", fontName="Helvetica-Bold", fontSize=9, leading=13,
            textColor=WHITE,
        ),
        "table_cell": ParagraphStyle(
            "TableCell", fontName="Helvetica", fontSize=9, leading=13,
            textColor=DARK_TEXT,
        ),
        "table_cell_bold": ParagraphStyle(
            "TableCellBold", fontName="Helvetica-Bold", fontSize=9, leading=13,
            textColor=DARK_TEXT,
        ),
        "footer_text": ParagraphStyle(
            "Footer", fontName="Helvetica", fontSize=7, leading=10,
            textColor=LIGHT_TEXT, alignment=TA_CENTER,
        ),
        "center": ParagraphStyle(
            "Center", fontName="Helvetica", fontSize=10, leading=14,
            textColor=DARK_TEXT, alignment=TA_CENTER,
        ),
        "gold_box": ParagraphStyle(
            "GoldBox", fontName="Helvetica-Bold", fontSize=10, leading=14,
            textColor=NAVY, alignment=TA_CENTER,
        ),
    }


# ─── Helper Functions ────────────────────────────────────────────────────────
def section_header(text, styles):
    """Create a styled section header with gold underline accent."""
    elements = []
    elements.append(Paragraph(text, styles["h2"]))
    # Gold accent line under section header
    elements.append(HRFlowable(
        width="100%", thickness=1.5, color=GOLD,
        spaceBefore=0, spaceAfter=4 * mm
    ))
    return elements


def gold_highlight_box(text):
    """Create a gold-accented highlight box."""
    data = [[Paragraph(text, ParagraphStyle(
        "GoldInner", fontName="Helvetica-Bold", fontSize=10, leading=15,
        textColor=NAVY, alignment=TA_CENTER,
    ))]]
    t = Table(data, colWidths=[PAGE_W - 50 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#fdf6e3")),
        ("BOX", (0, 0), (-1, -1), 1, GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return t


def info_table(rows, col_widths=None):
    """Create a styled key-value info table."""
    if col_widths is None:
        col_widths = [45 * mm, 115 * mm]
    styled_rows = []
    for key, val in rows:
        styled_rows.append([
            Paragraph(f"<b>{key}</b>", ParagraphStyle(
                "InfoKey", fontName="Helvetica-Bold", fontSize=9.5, leading=14, textColor=NAVY
            )),
            Paragraph(val, ParagraphStyle(
                "InfoVal", fontName="Helvetica", fontSize=9.5, leading=14, textColor=DARK_TEXT
            )),
        ])
    t = Table(styled_rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("LEFTPADDING", (1, 0), (1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, DIVIDER),
    ]))
    return t


def data_table(headers, rows, col_widths=None):
    """Create a professional data table."""
    if col_widths is None:
        col_widths = [None] * len(headers)

    header_style = ParagraphStyle(
        "TH", fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=WHITE,
    )
    cell_style = ParagraphStyle(
        "TD", fontName="Helvetica", fontSize=9, leading=13, textColor=DARK_TEXT,
    )
    cell_bold = ParagraphStyle(
        "TDB", fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=DARK_TEXT,
    )

    table_data = [[Paragraph(h, header_style) for h in headers]]
    for row in rows:
        table_data.append([
            Paragraph(str(cell), cell_bold if i == 0 else cell_style)
            for i, cell in enumerate(row)
        ])

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEAD_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.4, DIVIDER),
        ("BOX", (0, 0), (-1, -1), 0.8, NAVY),
    ]
    # Alternate row colors
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), TABLE_ALT_BG))

    t.setStyle(TableStyle(style_cmds))
    return t


# ─── Build the Document ──────────────────────────────────────────────────────
def build_document(output_path):
    margin_left = 20 * mm
    margin_right = 20 * mm
    margin_top = 20 * mm
    margin_bottom = 22 * mm

    content_top = 20 * mm  # extra space for header bar

    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=margin_left,
        rightMargin=margin_right,
        topMargin=margin_top,
        bottomMargin=margin_bottom,
        title=DOC["title"],
        author=COMPANY["name"],
    )

    # Cover page frame (full page, no margins needed for custom drawing)
    cover_frame = Frame(
        margin_left, margin_bottom,
        PAGE_W - margin_left - margin_right,
        PAGE_H - margin_top - margin_bottom,
        id="cover",
    )

    # Content frame (with extra top margin for header)
    content_frame = Frame(
        margin_left + 3 * mm, margin_bottom,  # +3mm for gold left bar
        PAGE_W - margin_left - margin_right - 3 * mm,
        PAGE_H - margin_top - margin_bottom - content_top,
        id="content",
    )

    cover_template = PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover_page)
    content_template = PageTemplate(id="content", frames=[content_frame], onPage=draw_content_page)

    doc.addPageTemplates([cover_template, content_template])

    styles = get_styles()
    story = []

    # ══════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════════════════
    # The cover frame is mostly empty since draw_cover_page handles visuals
    # Add a spacer to push content down
    story.append(Spacer(1, PAGE_H * 0.6))
    story.append(NextPageTemplate("content"))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════════════════
    story.extend(section_header("TABLE OF CONTENTS", styles))

    toc_items = [
        ("1.", "Document Control & Revision History"),
        ("2.", "Company Overview"),
        ("3.", "Purpose & Objectives"),
        ("4.", "Scope of Work – Exploration Services"),
        ("5.", "Scope of Work – Oil Refining & Processing"),
        ("6.", "Scope of Work – Petroleum Products Supply"),
        ("7.", "Scope of Work – Logistics & Delivery"),
        ("8.", "Quality Assurance & Compliance"),
        ("9.", "Health, Safety & Environment (HSE)"),
        ("10.", "Project Timeline & Milestones"),
        ("11.", "Commercial Terms"),
        ("12.", "Approval & Signatures"),
    ]
    for num, title in toc_items:
        story.append(Paragraph(
            f'<b>{num}</b>&nbsp;&nbsp;&nbsp;{title}',
            ParagraphStyle(
                "TOC", fontName="Helvetica", fontSize=10, leading=18,
                textColor=NAVY, leftIndent=8 * mm,
            )
        ))
    story.append(Spacer(1, 6 * mm))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 1. DOCUMENT CONTROL
    # ══════════════════════════════════════════════════════════════════════
    story.extend(section_header("1. DOCUMENT CONTROL & REVISION HISTORY", styles))

    story.append(info_table([
        ("Document Title:", DOC["title"]),
        ("Document Number:", DOC["doc_no"]),
        ("Revision:", DOC["revision"]),
        ("Date of Issue:", DOC["date"]),
        ("Prepared By:", DOC["prepared_by"]),
        ("Approved By:", DOC["approved_by"]),
        ("Classification:", DOC["classification"]),
        ("Validity Period:", DOC["validity"]),
        ("Client Reference:", DOC["client_ref"]),
        ("Contract Type:", DOC["contract_type"]),
    ]))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("Revision History", styles["h3"]))
    story.append(data_table(
        ["Rev.", "Date", "Description", "Author"],
        [
            ["01", "2025-01-15", "Initial issue – Draft scope definition", "Engineering Division"],
            ["02", "2025-04-20", "Updated refining capacity & product specifications", "Operations Division"],
            ["03", "2026-09-21", "Final approved version – Full scope alignment with board strategy", "Board of Directors"],
        ],
        col_widths=[15 * mm, 25 * mm, 70 * mm, 50 * mm],
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 2. COMPANY OVERVIEW
    # ══════════════════════════════════════════════════════════════════════
    story.extend(section_header("2. COMPANY OVERVIEW", styles))

    story.append(Paragraph(
        f"<b>{COMPANY['name']}</b> is a Kazakhstan-based integrated oil and gas company, primarily "
        "specialized in oil refining, exploration and development of oil and gas fields, and the "
        "production and sale of petroleum products. The company is one of the Kazakhstan oil "
        "industry's leading enterprises in efficiency and service delivery.",
        styles["body"]
    ))
    story.append(Paragraph(
        "Halyk Petroleum operates a modern refinery complex producing a wide range of "
        "environmentally friendly, highly competitive products including Crude Oil, Aviation Oil, "
        "Motor Fuel, MAZUT M100, Bitumen, LPG, Pet Coke, NPK, Sulfur Granular, Liquefied "
        "Natural Gas (LNG), Urea 46%, and Aviation Kerosene.",
        styles["body"]
    ))
    story.append(Spacer(1, 2 * mm))

    story.append(info_table([
        ("Registered Name:", COMPANY["name"]),
        ("Business ID (BIN):", COMPANY["bin"]),
        ("Headquarters:", COMPANY["address"]),
        ("Contact Phone:", COMPANY["phone"]),
        ("Email:", COMPANY["email"]),
        ("Website:", COMPANY["website"]),
        ("Geographic Reach:", "Kazakhstan (Asia), Europe, Americas"),
        ("Core Competencies:", "Exploration, Refining, Production, Sales & Marketing"),
    ]))

    story.append(gold_highlight_box(
        "★  Halyk Petroleum holds 13 exploration licenses in the Caspian Sea, Far Eastern, "
        "and Southern seas of Kazakhstan  ★"
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 3. PURPOSE & OBJECTIVES
    # ══════════════════════════════════════════════════════════════════════
    story.extend(section_header("3. PURPOSE & OBJECTIVES", styles))

    story.append(Paragraph(
        "This Approved Official Scope of Work defines the comprehensive range of services, "
        "deliverables, and operational standards that Halyk Petroleum LLP commits to providing "
        "under its framework supply agreements with international clients. The document serves "
        "as the authoritative reference for all project execution, quality benchmarks, and "
        "contractual obligations.",
        styles["body"]
    ))
    story.append(Spacer(1, 2 * mm))

    story.append(Paragraph("Primary Objectives:", styles["h3"]))
    objectives = [
        "Define the complete scope of exploration, refining, and supply services with measurable deliverables",
        "Establish quality assurance benchmarks aligned with international standards (ISO, API, ASTM)",
        "Outline HSE protocols ensuring zero-incident operations across all project phases",
        "Set clear commercial terms, delivery schedules, and performance metrics",
        "Ensure regulatory compliance with Kazakhstan petroleum laws and international trade requirements",
        "Provide a transparent framework for client engagement, reporting, and dispute resolution",
    ]
    for obj in objectives:
        story.append(Paragraph(f'<bullet>&bull;</bullet> {obj}', styles["bullet"]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 4. EXPLORATION SERVICES
    # ══════════════════════════════════════════════════════════════════════
    story.extend(section_header("4. SCOPE OF WORK – EXPLORATION SERVICES", styles))

    story.append(Paragraph(
        "Halyk Petroleum provides comprehensive oil and gas exploration services across "
        "Kazakhstan, utilizing cutting-edge technology and geological expertise to identify "
        "and develop high-potential oil reserves. Our exploration strategies ensure efficient "
        "resource discovery while adhering to environmental and safety standards.",
        styles["body"]
    ))

    story.append(Paragraph("4.1 Seismic Surveys & Geological Assessment", styles["h3"]))
    seismic_items = [
        "2D and 3D seismic data acquisition, processing, and interpretation",
        "Field seismic surveys for optimal surveillance system procurement",
        "Geological and geophysical modeling of subsurface formations",
        "Reservoir characterization and volumetric estimation",
        "Risk assessment and prospectivity mapping of licensed blocks",
    ]
    for item in seismic_items:
        story.append(Paragraph(f'<bullet>&bull;</bullet> {item}', styles["bullet"]))

    story.append(Paragraph("4.2 Drilling & Well Testing", styles["h3"]))
    drilling_items = [
        "Exploratory and appraisal well planning, design, and execution",
        "Directional and horizontal drilling operations",
        "Well logging, coring, and formation evaluation",
        "Production testing and flow rate assessment",
        "Well completion and integrity assurance",
    ]
    for item in drilling_items:
        story.append(Paragraph(f'<bullet>&bull;</bullet> {item}', styles["bullet"]))

    story.append(Paragraph("4.3 Reservoir Development Planning", styles["h3"]))
    story.append(Paragraph(
        "Comprehensive field development plans including production forecasting, facility sizing, "
        "and economic modeling to ensure optimal resource recovery and commercial viability.",
        styles["body"]
    ))

    story.append(data_table(
        ["Service Area", "Technology/Method", "Deliverable"],
        [
            ["Seismic Acquisition", "2D/3D/4D Seismic", "Processed seismic volumes & interpretation reports"],
            ["Geological Modeling", "Petrel / RMS", "Static & dynamic reservoir models"],
            ["Well Planning", "Directional Drilling Software", "Well trajectories & drilling programs"],
            ["Formation Evaluation", "LWD / Wireline Logging", "Petrophysical analysis & pay zone identification"],
            ["Production Testing", "Multi-rate / DST", "Flow test reports & reservoir parameters"],
        ],
        col_widths=[35 * mm, 40 * mm, 85 * mm],
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 5. OIL REFINING & PROCESSING
    # ══════════════════════════════════════════════════════════════════════
    story.extend(section_header("5. SCOPE OF WORK – OIL REFINING & PROCESSING", styles))

    story.append(Paragraph(
        "Halyk Petroleum delivers high-quality oil refining services utilizing state-of-the-art "
        "technology to produce premium petroleum products. Our refinery operates with advanced "
        "processing techniques ensuring maximum efficiency, safety, and environmental compliance.",
        styles["body"]
    ))

    story.append(Paragraph("5.1 Crude Oil Processing", styles["h3"]))
    refining_items = [
        "Atmospheric and vacuum distillation of crude oil feedstocks",
        "Catalytic cracking and reforming for gasoline and diesel production",
        "Hydroprocessing (hydrotreating and hydrocracking) for product quality enhancement",
        "Sulfur recovery and amine treatment for environmental compliance",
        "Blending and additive injection to meet product specifications",
    ]
    for item in refining_items:
        story.append(Paragraph(f'<bullet>&bull;</bullet> {item}', styles["bullet"]))

    story.append(Paragraph("5.2 Gas Processing", styles["h3"]))
    story.append(Paragraph(
        "The company processes a range of gas types including dry gas, wet gas, shale gas, "
        "stripped gas, and marketable gas. Advanced separation and treatment technologies ensure "
        "optimal recovery of valuable hydrocarbon components.",
        styles["body"]
    ))

    story.append(Paragraph("5.3 Product Specifications", styles["h3"]))
    story.append(data_table(
        ["Product", "Standard", "Key Specification", "Application"],
        [
            ["Euro-5 Diesel", "EN 590", "Sulfur < 10 mg/kg, Cetane ≥ 51", "Automotive & industrial"],
            ["Aviation Kerosene (Jet A-1)", "ASTM D1655", "Flash point ≥ 38°C, Freeze point ≤ -47°C", "Aviation fuel"],
            ["RT / TS-1 Aviation Fuel", "GOST 10227", "Thermal stability, low sulfur", "Military & commercial aviation"],
            ["MAZUT M100", "GOST 10585", "Viscosity, ash content, sulfur limits", "Industrial & marine fuel"],
            ["Bitumen", "ASTM D946", "Penetration grade 60/70", "Road construction"],
            ["LPG", "EN 589", "Propane/Butane mix specifications", "Heating & automotive"],
            ["High-Index Base Oils", "API Group II/III", "VI ≥ 120, low sulfur & aromatics", "Lubricant manufacturing"],
            ["Sulfur (Granular)", "ISO 26950", "Purity ≥ 99.5%", "Chemical industry & agriculture"],
            ["Urea 46%", "ISO 27536", "Nitrogen content ≥ 46%", "Agriculture & SCR systems"],
        ],
        col_widths=[32 * mm, 25 * mm, 48 * mm, 45 * mm],
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 6. PETROLEUM PRODUCTS SUPPLY
    # ══════════════════════════════════════════════════════════════════════
    story.extend(section_header("6. SCOPE OF WORK – PETROLEUM PRODUCTS SUPPLY", styles))

    story.append(Paragraph(
        "Halyk Petroleum is a trusted leader in petroleum product sales and marketing, "
        "delivering high-quality refined products to local and international markets. Our "
        "strategic supply chain, competitive pricing, and commitment to excellence ensure "
        "reliable distribution across Asia, Europe, and the Americas.",
        styles["body"]
    ))

    story.append(Paragraph("6.1 Supply Framework", styles["h3"]))
    supply_items = [
        "Supply of petroleum products on FOB (Free on Board) and CIF (Cost, Insurance, Freight) basis",
        "Flexible contract structures: spot, short-term, and long-term supply agreements",
        "Volume commitments from 10,000 MT to 500,000+ MT per annum per product",
        "Dedicated account management with 24/7 order processing capability",
        "Multi-product bundling with competitive volume-based pricing tiers",
    ]
    for item in supply_items:
        story.append(Paragraph(f'<bullet>&bull;</bullet> {item}', styles["bullet"]))

    story.append(Paragraph("6.2 Products Portfolio", styles["h3"]))
    story.append(data_table(
        ["Product Category", "Products", "Delivery Terms", "Min. Order Qty"],
        [
            ["Fuels", "Diesel (Euro-5), Gasoline (RON 92/95), Jet A-1, MAZUT M100", "FOB / CIF / DAP", "10,000 MT"],
            ["Gases", "LPG, LNG, Propane, Butane", "FOB / CIF", "5,000 MT"],
            ["Bitumen & Heavy", "Bitumen 60/70, Vacuum Residue", "FOB / CIF", "5,000 MT"],
            ["Petrochemicals", "Sulfur Granular, Urea 46%, NPK Fertilizer", "FOB / CIF / CFR", "5,000 MT"],
            ["Base Oils", "Group II / Group III Base Stocks", "FOB / CIF", "2,000 MT"],
            ["Specialty", "Pet Coke, Solvents, Aviation Oil", "FOB / CIF", "3,000 MT"],
        ],
        col_widths=[28 * mm, 52 * mm, 35 * mm, 30 * mm],
    ))

    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("6.3 Quality Guarantee", styles["h3"]))
    story.append(Paragraph(
        "All products supplied by Halyk Petroleum are accompanied by Certificates of Analysis "
        "(COA) issued by accredited third-party laboratories. Products are guaranteed to meet "
        "or exceed the specifications outlined in Section 5.3. Any non-conforming product will "
        "be replaced or refunded at Halyk Petroleum's sole discretion and cost.",
        styles["body"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 7. LOGISTICS & DELIVERY
    # ══════════════════════════════════════════════════════════════════════
    story.extend(section_header("7. SCOPE OF WORK – LOGISTICS & DELIVERY", styles))

    story.append(Paragraph(
        "Halyk Petroleum maintains a robust logistics infrastructure to ensure timely and "
        "secure delivery of petroleum products to global destinations.",
        styles["body"]
    ))

    logistics_items = [
        "Coordination with certified tanker fleets for maritime and overland transport",
        "Port operations management at key Caspian, Black Sea, and Baltic terminals",
        "Customs clearance and export documentation support",
        "Real-time shipment tracking and ETA updates for all consignments",
        "Insurance coverage (marine cargo) for full transit period",
        "Demurrage management and laytime optimization",
    ]
    for item in logistics_items:
        story.append(Paragraph(f'<bullet>&bull;</bullet> {item}', styles["bullet"]))

    story.append(Paragraph("Delivery Performance Targets:", styles["h3"]))
    story.append(data_table(
        ["Metric", "Target", "Measurement"],
        [
            ["On-Time Delivery Rate", "≥ 98%", "Per quarter, measured from confirmed delivery date"],
            ["Product Quality Compliance", "100%", "Zero non-conforming shipments per contract period"],
            ["Documentation Accuracy", "100%", "Error-free COA, B/L, and customs documents"],
            ["Customer Response Time", "< 4 hours", "Inquiry to quotation turnaround during business days"],
            ["Shipment Tracking Updates", "Real-time", "GPS-enabled tracking with automated status notifications"],
        ],
        col_widths=[40 * mm, 25 * mm, 85 * mm],
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 8. QUALITY ASSURANCE
    # ══════════════════════════════════════════════════════════════════════
    story.extend(section_header("8. QUALITY ASSURANCE & COMPLIANCE", styles))

    story.append(Paragraph(
        "Halyk Petroleum maintains a comprehensive Quality Management System (QMS) aligned "
        "with international standards to ensure consistent product quality and operational excellence.",
        styles["body"]
    ))

    story.append(Paragraph("8.1 Certifications & Standards", styles["h3"]))
    qa_items = [
        "ISO 9001:2015 – Quality Management System",
        "ISO 14001:2015 – Environmental Management System",
        "ISO 45001:2018 – Occupational Health & Safety Management",
        "API Q1 / Q2 – Quality Management for Petroleum Industry",
        "ASTM, EN, and GOST product specification compliance",
        "Kazakhstan Republic petroleum regulatory standards",
    ]
    for item in qa_items:
        story.append(Paragraph(f'<bullet>&bull;</bullet> {item}', styles["bullet"]))

    story.append(Paragraph("8.2 Inspection & Testing Protocol", styles["h3"]))
    story.append(Paragraph(
        "All products undergo rigorous testing at multiple stages: incoming crude assay, "
        "in-process quality monitoring, and final product certification. Third-party inspection "
        "by SGS, Bureau Veritas, or Intertek is available upon client request.",
        styles["body"]
    ))

    story.append(Paragraph("8.3 Regulatory Compliance", styles["h3"]))
    compliance_items = [
        "Full compliance with Kazakhstan Export Control regulations",
        "Adherence to EU REACH and CLP regulations for European-bound products",
        "Compliance with MARPOL Annex VI for marine fuel sulfur content limits",
        "Environmental impact assessments for all exploration and refining operations",
    ]
    for item in compliance_items:
        story.append(Paragraph(f'<bullet>&bull;</bullet> {item}', styles["bullet"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 9. HSE
    # ══════════════════════════════════════════════════════════════════════
    story.extend(section_header("9. HEALTH, SAFETY & ENVIRONMENT (HSE)", styles))

    story.append(Paragraph(
        "Halyk Petroleum is committed to achieving zero-incident operations through a proactive "
        "safety culture, rigorous risk management, and continuous environmental stewardship.",
        styles["body"]
    ))

    story.append(Paragraph("9.1 Safety Management", styles["h3"]))
    hse_items = [
        "Implementation of Process Safety Management (PSM) across all facilities",
        "Regular HAZOP studies, risk assessments, and emergency response drills",
        "Mandatory safety training for all personnel – minimum 40 hours per annum",
        "Personal Protective Equipment (PPE) compliance monitoring",
        "Incident reporting, investigation, and root cause analysis protocols",
    ]
    for item in hse_items:
        story.append(Paragraph(f'<bullet>&bull;</bullet> {item}', styles["bullet"]))

    story.append(Paragraph("9.2 Environmental Protection", styles["h3"]))
    env_items = [
        "Emissions monitoring and reduction programs (SOx, NOx, CO₂, VOC)",
        "Wastewater treatment and zero-discharge targets",
        "Spill prevention and containment systems at all facilities",
        "Waste management hierarchy: reduce, reuse, recycle, dispose",
        "Biodiversity protection measures for exploration license areas",
    ]
    for item in env_items:
        story.append(Paragraph(f'<bullet>&bull;</bullet> {item}', styles["bullet"]))

    story.append(gold_highlight_box(
        "HALYK PETROLEUM TARGET: ZERO FATALITIES  •  ZERO MAJOR INCIDENTS  •  ZERO ENVIRONMENTAL RELEASES"
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 10. TIMELINE
    # ══════════════════════════════════════════════════════════════════════
    story.extend(section_header("10. PROJECT TIMELINE & MILESTONES", styles))

    story.append(data_table(
        ["Phase", "Activity", "Duration", "Deliverable"],
        [
            ["1", "Contract execution & kick-off", "Week 1–2", "Signed agreement, project plan"],
            ["2", "Crude oil sourcing & procurement", "Week 3–6", "Supply chain confirmed, crude assay"],
            ["3", "Refinery scheduling & production", "Week 7–14", "Production run, batch testing"],
            ["4", "Quality certification & inspection", "Week 15–16", "COA, third-party inspection reports"],
            ["5", "Logistics coordination & loading", "Week 17–18", "B/L, shipping documents, ETA confirmed"],
            ["6", "Transit & delivery", "Week 19–22", "Delivery confirmation, customer acceptance"],
            ["7", "Post-delivery support & reconciliation", "Week 23–24", "Final invoice, performance report"],
        ],
        col_widths=[12 * mm, 45 * mm, 30 * mm, 63 * mm],
    ))

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "<b>Note:</b> Timeline is indicative for a standard FOB supply cycle of 50,000 MT. "
        "Actual timelines may vary based on product type, volume, destination, and market conditions.",
        styles["note"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 11. COMMERCIAL TERMS
    # ══════════════════════════════════════════════════════════════════════
    story.extend(section_header("11. COMMERCIAL TERMS", styles))

    story.append(info_table([
        ("Pricing Basis:", "Platt's / Argus benchmark ± negotiated discount/premium"),
        ("Currency:", "USD (United States Dollar)"),
        ("Payment Terms:", "Irrevocable SBLC or confirmed DLC, 30 days from B/L date"),
        ("Incoterms:", "FOB, CIF, CFR, DAP – as agreed per contract"),
        ("Minimum Order:", "Per product category – see Section 6.2"),
        ("Contract Duration:", "12–36 months, with renewal option"),
        ("Force Majeure:", "As per ICC Force Majeure Clause 2020"),
        ("Governing Law:", "Laws of the Republic of Kazakhstan / English Law (by agreement)"),
        ("Dispute Resolution:", "ICC Arbitration, London or Singapore"),
        ("Insurance:", "Marine cargo insurance at 110% CIF value (Institute Cargo Clauses A)"),
    ]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # 12. APPROVAL & SIGNATURES
    # ══════════════════════════════════════════════════════════════════════
    story.extend(section_header("12. APPROVAL & SIGNATURES", styles))

    story.append(Paragraph(
        "This Approved Official Scope of Work has been reviewed and authorized by the "
        "undersigned representatives of Halyk Petroleum LLP. This document is effective "
        f"from <b>{DOC['date']}</b> and shall remain valid for the period specified herein.",
        styles["body"]
    ))
    story.append(Spacer(1, 6 * mm))

    # Signature block
    sig_data = [
        [Paragraph("<b>PREPARED BY</b>", ParagraphStyle("SigHead", fontName="Helvetica-Bold", fontSize=10, textColor=NAVY, alignment=TA_CENTER)),
         Paragraph("<b>REVIEWED BY</b>", ParagraphStyle("SigHead", fontName="Helvetica-Bold", fontSize=10, textColor=NAVY, alignment=TA_CENTER)),
         Paragraph("<b>APPROVED BY</b>", ParagraphStyle("SigHead", fontName="Helvetica-Bold", fontSize=10, textColor=NAVY, alignment=TA_CENTER))],
        [Paragraph("Chief Operations Officer", ParagraphStyle("SigRole", fontName="Helvetica", fontSize=9, textColor=LIGHT_TEXT, alignment=TA_CENTER)),
         Paragraph("VP Engineering", ParagraphStyle("SigRole", fontName="Helvetica", fontSize=9, textColor=LIGHT_TEXT, alignment=TA_CENTER)),
         Paragraph("Chief Executive Officer", ParagraphStyle("SigRole", fontName="Helvetica", fontSize=9, textColor=LIGHT_TEXT, alignment=TA_CENTER))],
        [Spacer(1, 25 * mm), Spacer(1, 25 * mm), Spacer(1, 25 * mm)],
        [Paragraph("_" * 35, ParagraphStyle("SigLine", fontSize=9, textColor=DIVIDER, alignment=TA_CENTER)),
         Paragraph("_" * 35, ParagraphStyle("SigLine", fontSize=9, textColor=DIVIDER, alignment=TA_CENTER)),
         Paragraph("_" * 35, ParagraphStyle("SigLine", fontSize=9, textColor=DIVIDER, alignment=TA_CENTER))],
        [Paragraph("Name: ________________________", ParagraphStyle("SigName", fontName="Helvetica", fontSize=9, textColor=MED_TEXT, alignment=TA_CENTER)),
         Paragraph("Name: ________________________", ParagraphStyle("SigName", fontName="Helvetica", fontSize=9, textColor=MED_TEXT, alignment=TA_CENTER)),
         Paragraph("Name: ________________________", ParagraphStyle("SigName", fontName="Helvetica", fontSize=9, textColor=MED_TEXT, alignment=TA_CENTER))],
        [Paragraph("Date: ________________________", ParagraphStyle("SigDate", fontName="Helvetica", fontSize=9, textColor=MED_TEXT, alignment=TA_CENTER)),
         Paragraph("Date: ________________________", ParagraphStyle("SigDate", fontName="Helvetica", fontSize=9, textColor=MED_TEXT, alignment=TA_CENTER)),
         Paragraph("Date: ________________________", ParagraphStyle("SigDate", fontName="Helvetica", fontSize=9, textColor=MED_TEXT, alignment=TA_CENTER))],
    ]

    sig_table = Table(sig_data, colWidths=[50 * mm, 50 * mm, 50 * mm])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (-1, -1), 0.8, NAVY),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, DIVIDER),
        ("BACKGROUND", (0, 0), (-1, 0), SKY),
    ]))
    story.append(sig_table)

    story.append(Spacer(1, 8 * mm))
    story.append(gold_highlight_box(
        "END OF DOCUMENT  •  " + DOC["doc_no"] + "  •  " + DOC["revision"]
    ))

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        f"{COMPANY['name']}  •  {COMPANY['address']}  •  {COMPANY['phone']}  •  {COMPANY['email']}",
        ParagraphStyle("FinalFooter", fontName="Helvetica", fontSize=8, textColor=LIGHT_TEXT, alignment=TA_CENTER)
    ))

    # ── Build ─────────────────────────────────────────────────────────────
    doc.build(story)
    print(f"✅ Halyk Petroleum Scope of Work PDF generated: {output_path}")
    print(f"   File size: {os.path.getsize(output_path) / 1024:.1f} KB")


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(__file__), "HALYK_PETROLEUM_SCO.pdf")
    build_document(output)
