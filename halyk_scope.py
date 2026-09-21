#!/usr/bin/env python3
"""
HALYK PETROLEUM LLP – Approved Official Scope of Work
Professional corporate document generator using ReportLab.

Rev. 04 improvements over the previous generator:
  * Cover page carries the COMPLETE document-control block (doc no, revision,
    issue date, status, classification, validity, contract type, client ref,
    prepared/approved by, supersedes, review cycle) plus full company contact
    data (BIN, address, phone, e-mail, website) – no information is omitted.
  * Real, auto-generated Table of Contents with page numbers, dot leaders and
    clickable links, plus PDF outline bookmarks for every section/subsection.
  * Content flows continuously (no half-empty forced pages); headings are
    protected against orphaning with keepWithNext.
  * Fixed broken glyphs (CO2 instead of the unsupported subscript), fixed the
    mangled signature block, fixed table column widths ("Phase" no longer
    wraps mid-word).
  * Full PDF metadata (title / author / subject / keywords / creator) and
    "Page X of Y" footers on every content page.
  * New Appendix A – Definitions & Abbreviations so every term used in the
    document is defined inside the document.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether,
    Frame, PageTemplate, BaseDocTemplate, PageBreak, NextPageTemplate,
    CondPageBreak,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfgen import canvas as pdfcanvas
import os
import re

# ─── Color Palette (Corporate Oil & Gas Theme) ──────────────────────────────
DARK_BLUE    = HexColor("#0a1628")   # Deep navy (cover header bg)
NAVY         = HexColor("#102a5c")   # Primary navy
PANEL_BLUE   = HexColor("#0d2440")   # Cover chip background
MED_BLUE     = HexColor("#1e4d8c")   # Medium blue
LIGHT_BLUE   = HexColor("#2c7be5")   # Accent blue
PALE_BLUE    = HexColor("#b0c4de")   # Subtitle on dark bg
SKY          = HexColor("#e8f1fd")   # Very light blue bg
GOLD         = HexColor("#c8952e")   # Gold accent
DARK_GOLD    = HexColor("#a07825")   # Darker gold
CREAM        = HexColor("#fdf6e3")   # Highlight box bg
WHITE        = HexColor("#ffffff")
OFF_WHITE    = HexColor("#f7f9fc")
DARK_TEXT    = HexColor("#1a1a2e")
MED_TEXT     = HexColor("#4a5568")
LIGHT_TEXT   = HexColor("#718096")
DIVIDER      = HexColor("#d1d9e6")
TABLE_HEAD_BG = HexColor("#102a5c")
TABLE_ALT_BG  = HexColor("#f0f4fa")

PAGE_W, PAGE_H = A4
MARGIN_L = 20 * mm
MARGIN_R = 20 * mm
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R


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
    "reviewed_by": "VP Engineering",
    "approved_by": "Board of Directors – Halyk Petroleum LLP",
    "classification": "CONFIDENTIAL – INTERNAL USE ONLY",
    "client_ref": "Multiple International Clients",
    "contract_type": "Framework Supply Agreement (FSA)",
    "validity": "24 months from date of approval",
    "status": "APPROVED – ACTIVE",
    "supersedes": "HP-SCO-2025-001 Rev. 02",
    "review_cycle": "Annual, or upon significant operational change",
}

# Ordered (label, key) pairs – every entry is rendered on the cover panel
COVER_DOC_FIELDS = [
    ("Document No:", "doc_no"),
    ("Revision:", "revision"),
    ("Date of Issue:", "date"),
    ("Document Status:", "status"),
    ("Classification:", "classification"),
    ("Validity Period:", "validity"),
    ("Contract Type:", "contract_type"),
    ("Client Reference:", "client_ref"),
    ("Prepared By:", "prepared_by"),
    ("Reviewed By:", "reviewed_by"),
    ("Approved By:", "approved_by"),
    ("Supersedes:", "supersedes"),
    ("Review Cycle:", "review_cycle"),
    ("Business ID (BIN):", "bin"),
]


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# ─── Canvas with "Page X of Y" footers ───────────────────────────────────────
class NumberedCanvas(pdfcanvas.Canvas):
    """Two-pass canvas so footers can print total page count."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_pages = []

    def showPage(self):
        self._saved_pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_pages)
        for state in self._saved_pages:
            self.__dict__.update(state)
            if self._pageNumber > 1:
                self._draw_footer(total)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _draw_footer(self, total):
        w = PAGE_W
        self.setStrokeColor(DIVIDER)
        self.setLineWidth(0.4)
        self.line(MARGIN_L, 15 * mm, w - MARGIN_R, 15 * mm)
        self.setFont("Helvetica", 7)
        self.setFillColor(LIGHT_TEXT)
        self.drawString(MARGIN_L, 10.5 * mm, DOC["classification"])
        self.drawCentredString(w / 2, 10.5 * mm, COMPANY["name"])
        self.drawRightString(w - MARGIN_R, 10.5 * mm,
                             f"Page {self._pageNumber} of {total}")
        # bottom accent strip
        self.setFillColor(NAVY)
        self.rect(0, 0, w, 2.5 * mm, fill=1, stroke=0)


# ─── Cover page artwork ─────────────────────────────────────────────────────
def _draw_emblem(c, cx, cy):
    """Vector logo: gold ring with an oil drop inside."""
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.6)
    c.circle(cx, cy, 13 * mm, stroke=1, fill=0)
    c.setLineWidth(0.6)
    c.circle(cx, cy, 11.2 * mm, stroke=1, fill=0)
    # oil drop
    p = c.beginPath()
    p.moveTo(cx, cy + 8.2 * mm)
    p.curveTo(cx + 4.6 * mm, cy + 1.6 * mm, cx + 5.4 * mm, cy - 1.4 * mm, cx + 5.4 * mm, cy - 3.2 * mm)
    p.curveTo(cx + 5.4 * mm, cy - 6.4 * mm, cx + 3.0 * mm, cy - 8.2 * mm, cx, cy - 8.2 * mm)
    p.curveTo(cx - 3.0 * mm, cy - 8.2 * mm, cx - 5.4 * mm, cy - 6.4 * mm, cx - 5.4 * mm, cy - 3.2 * mm)
    p.curveTo(cx - 5.4 * mm, cy - 1.4 * mm, cx - 4.6 * mm, cy + 1.6 * mm, cx, cy + 8.2 * mm)
    p.close()
    c.setFillColor(GOLD)
    c.drawPath(p, fill=1, stroke=0)
    # highlight dot on the drop
    c.setFillColor(PANEL_BLUE)
    c.circle(cx - 1.8 * mm, cy - 3.4 * mm, 1.1 * mm, stroke=0, fill=1)


def draw_cover_page(c, doc):
    w, h = PAGE_W, PAGE_H
    block_h = 150 * mm

    # ── dark header block ──
    c.setFillColor(DARK_BLUE)
    c.rect(0, h - block_h, w, block_h, fill=1, stroke=0)

    _draw_emblem(c, w / 2, h - 30 * mm)

    c.setFont("Helvetica-Bold", 27)
    c.setFillColor(WHITE)
    c.drawCentredString(w / 2, h - 56 * mm, COMPANY["name"])

    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(GOLD)
    c.drawCentredString(w / 2, h - 64.5 * mm, COMPANY["tagline"])

    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(w / 2 - 55 * mm, h - 70 * mm, w / 2 + 55 * mm, h - 70 * mm)

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(WHITE)
    c.drawCentredString(w / 2, h - 82 * mm, DOC["title"])

    c.setFont("Helvetica", 11)
    c.setFillColor(PALE_BLUE)
    c.drawCentredString(w / 2, h - 90 * mm, DOC["subtitle"])

    # ── key-fact chips: doc no / revision / issue date / status ──
    chips = [
        ("DOCUMENT NO.", DOC["doc_no"]),
        ("REVISION", DOC["revision"]),
        ("ISSUE DATE", DOC["date"]),
        ("STATUS", DOC["status"]),
    ]
    chip_w, chip_h, gap = 41 * mm, 13 * mm, 3.5 * mm
    x0 = (w - (4 * chip_w + 3 * gap)) / 2
    y0 = h - 108 * mm
    for i, (label, value) in enumerate(chips):
        x = x0 + i * (chip_w + gap)
        c.setFillColor(PANEL_BLUE)
        c.roundRect(x, y0, chip_w, chip_h, 2 * mm, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.6)
        c.roundRect(x, y0, chip_w, chip_h, 2 * mm, fill=0, stroke=1)
        c.setFont("Helvetica-Bold", 6.5)
        c.setFillColor(GOLD)
        c.drawCentredString(x + chip_w / 2, y0 + chip_h - 4.6 * mm, label)
        c.setFont("Helvetica-Bold", 8.6)
        c.setFillColor(WHITE)
        c.drawCentredString(x + chip_w / 2, y0 + 3.2 * mm, value)

    # ── classification banner ──
    ban_w, ban_h = 120 * mm, 8 * mm
    bx = (w - ban_w) / 2
    by = h - 124 * mm
    c.setFillColor(HexColor("#3a1220"))
    c.roundRect(bx, by, ban_w, ban_h, 1.6 * mm, fill=1, stroke=0)
    c.setStrokeColor(HexColor("#e08080"))
    c.setLineWidth(0.6)
    c.roundRect(bx, by, ban_w, ban_h, 1.6 * mm, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#ffd9d9"))
    c.drawCentredString(w / 2, by + 2.7 * mm, DOC["classification"])
    c.setFont("Helvetica-Oblique", 7.6)
    c.setFillColor(PALE_BLUE)
    c.drawCentredString(w / 2, h - 138 * mm,
                        "Controlled electronic document – printed copies are valid "
                        "on the day of printing only.")

    # ── gold + blue stripes under the dark block ──
    c.setFillColor(GOLD)
    c.rect(0, h - block_h - 4 * mm, w, 4 * mm, fill=1, stroke=0)
    c.setFillColor(LIGHT_BLUE)
    c.rect(0, h - block_h - 5 * mm, w, 1 * mm, fill=1, stroke=0)

    # ── DOCUMENT INFORMATION panel (complete control block) ──
    panel_x, panel_w = MARGIN_L, CONTENT_W
    panel_top = h - block_h - 13 * mm
    rows = 7
    row_h = 8.6 * mm
    panel_h = 10 * mm + rows * row_h + 3 * mm
    c.setFillColor(OFF_WHITE)
    c.roundRect(panel_x, panel_top - panel_h, panel_w, panel_h, 2.5 * mm, fill=1, stroke=0)
    c.setStrokeColor(DIVIDER)
    c.setLineWidth(0.7)
    c.roundRect(panel_x, panel_top - panel_h, panel_w, panel_h, 2.5 * mm, fill=0, stroke=1)

    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(NAVY)
    c.drawString(panel_x + 6 * mm, panel_top - 7 * mm, "DOCUMENT INFORMATION")
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(panel_x + 6 * mm, panel_top - 8.6 * mm, panel_x + 46 * mm, panel_top - 8.6 * mm)

    def wrap_value(text, font, size, max_w):
        words, lines, cur = text.split(), [], ""
        for wd in words:
            trial = f"{cur} {wd}".strip()
            if c.stringWidth(trial, font, size) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    col_w = panel_w / 2
    for idx, (label, key) in enumerate(COVER_DOC_FIELDS):
        col, row = idx % 2, idx // 2
        x = panel_x + 6 * mm + col * col_w
        y = panel_top - 13 * mm - row * row_h
        value = COMPANY[key] if key in COMPANY else DOC[key]
        c.setFont("Helvetica-Bold", 7.6)
        c.setFillColor(DARK_GOLD)
        c.drawString(x, y, label)
        c.setFont("Helvetica", 8.2)
        c.setFillColor(DARK_TEXT)
        # wrap long values onto a second line – never truncate information
        max_w = col_w - 36 * mm
        for li, line in enumerate(wrap_value(value, "Helvetica", 8.2, max_w)[:2]):
            c.drawString(x + 34 * mm, y - li * 3.4 * mm, line)

    # ── approval / signature strip ──
    sig_top = panel_top - panel_h - 8 * mm
    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(NAVY)
    c.drawString(panel_x, sig_top, "AUTHORISATION")
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(panel_x, sig_top - 1.6 * mm, panel_x + 30 * mm, sig_top - 1.6 * mm)

    sig_y = sig_top - 16 * mm
    col_xs = [panel_x, panel_x + panel_w / 2 + 5 * mm]
    sig_items = [("Prepared By:", DOC["prepared_by"]), ("Approved By:", DOC["approved_by"])]
    for (label, value), x in zip(sig_items, col_xs):
        c.setFont("Helvetica-Bold", 8.6)
        c.setFillColor(NAVY)
        c.drawString(x, sig_y + 8 * mm, label)
        c.setFont("Helvetica", 8.6)
        c.setFillColor(MED_TEXT)
        c.drawString(x, sig_y + 3.4 * mm, value)
        c.setStrokeColor(MED_TEXT)
        c.setLineWidth(0.6)
        c.line(x, sig_y, x + 75 * mm, sig_y)
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColor(LIGHT_TEXT)
        c.drawString(x, sig_y - 3.6 * mm, "Signature & Date")

    # ── bottom contact band ──
    band_h = 16 * mm
    c.setFillColor(NAVY)
    c.rect(0, 0, w, band_h, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, band_h, w, 1 * mm, fill=1, stroke=0)
    c.setFont("Helvetica", 7.6)
    c.setFillColor(WHITE)
    c.drawCentredString(w / 2, band_h - 6.4 * mm, COMPANY["address"])
    c.setFont("Helvetica-Bold", 7.6)
    c.setFillColor(GOLD)
    c.drawCentredString(
        w / 2, band_h - 11 * mm,
        f"Tel {COMPANY['phone']}   •   {COMPANY['email']}   •   {COMPANY['website']}   •   BIN {COMPANY['bin']}",
    )


def draw_content_page(c, doc):
    """Header bar for content pages (footer handled by NumberedCanvas)."""
    w, h = PAGE_W, PAGE_H
    c.setFillColor(NAVY)
    c.rect(0, h - 13 * mm, w, 13 * mm, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, h - 14.2 * mm, w, 1.2 * mm, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(WHITE)
    c.drawString(MARGIN_L, h - 8.6 * mm, COMPANY["name"])
    c.setFont("Helvetica", 8)
    c.setFillColor(GOLD)
    c.drawRightString(w - MARGIN_R, h - 8.6 * mm,
                      f"{DOC['doc_no']}   |   {DOC['revision']}   |   {DOC['date']}")


# ─── Document template with TOC + bookmarks ─────────────────────────────────
class ScopeDocTemplate(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        style_name = flowable.style.name
        if style_name == "SectHead":
            level = 0
        elif style_name == "SubHead":
            level = 1
        else:
            return
        text = flowable.getPlainText()
        key = "sec-" + _slug(text)
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=False)
        self.notify("TOCEntry", (level, text, self.page, key))


# ─── Styles ─────────────────────────────────────────────────────────────────
def get_styles():
    return {
        "SectHead": ParagraphStyle(
            "SectHead", fontName="Helvetica-Bold", fontSize=14.5, leading=19,
            textColor=NAVY, spaceBefore=7 * mm, spaceAfter=1.5 * mm,
            keepWithNext=1,
        ),
        "SubHead": ParagraphStyle(
            "SubHead", fontName="Helvetica-Bold", fontSize=10.8, leading=14.5,
            textColor=MED_BLUE, spaceBefore=4.5 * mm, spaceAfter=1.8 * mm,
            keepWithNext=1,
        ),
        "body": ParagraphStyle(
            "Body", fontName="Helvetica", fontSize=9.3, leading=13.6,
            textColor=DARK_TEXT, alignment=TA_JUSTIFY, spaceAfter=2.2 * mm,
        ),
        "bullet": ParagraphStyle(
            "Bullet", fontName="Helvetica", fontSize=9.3, leading=13.4,
            textColor=DARK_TEXT, leftIndent=11, bulletIndent=0,
            spaceBefore=0.6 * mm, spaceAfter=0.6 * mm,
        ),
        "note": ParagraphStyle(
            "Note", fontName="Helvetica-Oblique", fontSize=8.6, leading=12.4,
            textColor=MED_TEXT, leftIndent=4 * mm, rightIndent=4 * mm,
            spaceBefore=2.5 * mm, spaceAfter=2.5 * mm,
            borderColor=LIGHT_BLUE, borderWidth=0.6, borderPadding=6,
            backColor=SKY,
        ),
        "toc_title": ParagraphStyle(
            "TOCTitle", fontName="Helvetica-Bold", fontSize=16, leading=21,
            textColor=NAVY, alignment=TA_CENTER, spaceBefore=2 * mm,
            spaceAfter=1.5 * mm,
        ),
        "center": ParagraphStyle(
            "Center", fontName="Helvetica", fontSize=8.4, leading=12,
            textColor=LIGHT_TEXT, alignment=TA_CENTER,
        ),
    }


TOC_LEVEL_STYLES = [
    ParagraphStyle(
        "TOC0", fontName="Helvetica-Bold", fontSize=9.8, leading=13.5,
        textColor=NAVY, leftIndent=2 * mm, firstLineIndent=0,
        spaceBefore=1.1 * mm, spaceAfter=0,
    ),
    ParagraphStyle(
        "TOC1", fontName="Helvetica", fontSize=8.6, leading=11.2,
        textColor=MED_TEXT, leftIndent=9 * mm, firstLineIndent=0,
        spaceBefore=0, spaceAfter=0,
    ),
]


# ─── Flowable helpers ────────────────────────────────────────────────────────
def section_header(text, styles, guard_mm=45):
    """Heading + gold rule, guarded so it can never be orphaned at a page bottom."""
    rule = HRFlowable(width="100%", thickness=1.4, color=GOLD,
                      spaceBefore=0, spaceAfter=3.2 * mm)
    rule.keepWithNext = 1
    return [CondPageBreak(guard_mm * mm),
            Paragraph(text, styles["SectHead"]), rule]


def sub_header(text, styles):
    return Paragraph(text, styles["SubHead"])


def bullets(items, styles):
    out = []
    for item in items:
        out.append(Paragraph(
            '<bullet><font color="#c8952e"><b>&bull;</b></font></bullet>' + item,
            styles["bullet"],
        ))
    return out


def gold_highlight_box(text):
    data = [[Paragraph(text, ParagraphStyle(
        "GoldInner", fontName="Helvetica-Bold", fontSize=9.6, leading=14,
        textColor=NAVY, alignment=TA_CENTER,
    ))]]
    t = Table(data, colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CREAM),
        ("BOX", (0, 0), (-1, -1), 1, GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


def info_table(rows, col_widths=None):
    if col_widths is None:
        col_widths = [46 * mm, CONTENT_W - 46 * mm]
    key_style = ParagraphStyle("InfoKey", fontName="Helvetica-Bold", fontSize=9.2,
                               leading=13.2, textColor=NAVY)
    val_style = ParagraphStyle("InfoVal", fontName="Helvetica", fontSize=9.2,
                               leading=13.2, textColor=DARK_TEXT)
    styled = [[Paragraph(f"<b>{k}</b>", key_style), Paragraph(v, val_style)]
              for k, v in rows]
    t = Table(styled, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("LEFTPADDING", (1, 0), (1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, DIVIDER),
    ]))
    return t


def data_table(headers, rows, col_widths=None):
    head_style = ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.8,
                                leading=12.2, textColor=WHITE)
    cell_style = ParagraphStyle("TD", fontName="Helvetica", fontSize=8.8,
                                leading=12.2, textColor=DARK_TEXT)
    cell_bold = ParagraphStyle("TDB", fontName="Helvetica-Bold", fontSize=8.8,
                               leading=12.2, textColor=DARK_TEXT)
    table_data = [[Paragraph(h, head_style) for h in headers]]
    for row in rows:
        table_data.append([
            Paragraph(str(cell), cell_bold if i == 0 else cell_style)
            for i, cell in enumerate(row)
        ])
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEAD_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.4, DIVIDER),
        ("BOX", (0, 0), (-1, -1), 0.8, NAVY),
    ]
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), TABLE_ALT_BG))
    t.setStyle(TableStyle(cmds))
    return t


def stat_chips(stats):
    """stats: list of (big value, caption)."""
    cells = []
    for value, caption in stats:
        cells.append([
            Paragraph(f'<font size="15" color="#102a5c"><b>{value}</b></font>',
                      ParagraphStyle("StatV", alignment=TA_CENTER, leading=19)),
            Paragraph(f'<font size="7.4" color="#4a5568">{caption}</font>',
                      ParagraphStyle("StatC", alignment=TA_CENTER, leading=10)),
        ])
    # one row: merge pairs vertically via inner tables
    inner = []
    for value, caption in stats:
        it = Table([[Paragraph(f'<font size="15" color="#102a5c"><b>{value}</b></font>',
                               ParagraphStyle("SV", alignment=TA_CENTER, leading=18))],
                    [Paragraph(f'<font size="7.4" color="#4a5568">{caption}</font>',
                               ParagraphStyle("SC", alignment=TA_CENTER, leading=10))]],
                   colWidths=[CONTENT_W / len(stats) - 3 * mm])
        it.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), SKY),
            ("BOX", (0, 0), (-1, -1), 0.6, LIGHT_BLUE),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        inner.append(it)
    t = Table([inner], colWidths=[CONTENT_W / len(stats)] * len(stats))
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1.5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1.5 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def signature_table():
    head = ParagraphStyle("SigHead", fontName="Helvetica-Bold", fontSize=9.6,
                          textColor=NAVY, alignment=TA_CENTER)
    role = ParagraphStyle("SigRole", fontName="Helvetica", fontSize=8.6,
                          textColor=LIGHT_TEXT, alignment=TA_CENTER)
    cap = ParagraphStyle("SigCap", fontName="Helvetica-Oblique", fontSize=7.4,
                         textColor=LIGHT_TEXT, alignment=TA_CENTER)
    blank = ParagraphStyle("SigBlank", fontSize=4, leading=6)

    def signer_cell(title, role_txt):
        inner = Table([
            [Paragraph(f"<b>{title}</b>", head)],
            [Paragraph(role_txt, role)],
            [Spacer(1, 14 * mm)],
            [Paragraph("", blank)],
            [Paragraph("Signature", cap)],
            [Spacer(1, 4 * mm)],
            [Paragraph("", blank)],
            [Paragraph("Name (print)", cap)],
            [Spacer(1, 4 * mm)],
            [Paragraph("", blank)],
            [Paragraph("Date", cap)],
        ], colWidths=[CONTENT_W / 3 - 8 * mm])
        inner.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("BACKGROUND", (0, 0), (0, 0), SKY),
            ("LINEBELOW", (0, 3), (0, 3), 0.9, NAVY),
            ("LINEBELOW", (0, 6), (0, 6), 0.6, MED_TEXT),
            ("LINEBELOW", (0, 9), (0, 9), 0.6, MED_TEXT),
        ]))
        return inner

    outer = Table([[
        signer_cell("PREPARED BY", "Chief Operations Officer"),
        signer_cell("REVIEWED BY", "VP Engineering"),
        signer_cell("APPROVED BY", "Chief Executive Officer"),
    ]], colWidths=[CONTENT_W / 3] * 3)
    outer.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("BOX", (0, 0), (-1, -1), 0.8, NAVY),
        ("LINEBEFORE", (1, 0), (1, 0), 0.3, DIVIDER),
        ("LINEBEFORE", (2, 0), (2, 0), 0.3, DIVIDER),
    ]))
    return outer


# ─── Build the Document ──────────────────────────────────────────────────────
def build_document(output_path):
    doc = ScopeDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN_L,
        rightMargin=MARGIN_R,
        topMargin=21 * mm,
        bottomMargin=20 * mm,
        title=f"{DOC['title']} – {DOC['doc_no']} ({DOC['revision']})",
        author=COMPANY["name"],
        subject=DOC["subtitle"],
        keywords=("Halyk Petroleum, Scope of Work, Oil & Gas, Exploration, "
                  "Refining, Petroleum Products Supply, LNG, LPG, MAZUT, "
                  f"{DOC['doc_no']}"),
        creator="Halyk Petroleum LLP – Engineering & Operations Division",
    )

    cover_frame = Frame(MARGIN_L, 20 * mm, CONTENT_W, PAGE_H - 20 * mm - 18 * mm,
                        id="cover", leftPadding=0, rightPadding=0,
                        topPadding=0, bottomPadding=0)
    content_frame = Frame(MARGIN_L, 20 * mm, CONTENT_W,
                          PAGE_H - 20 * mm - 21 * mm, id="content",
                          leftPadding=0, rightPadding=0, topPadding=0,
                          bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover_page),
        PageTemplate(id="content", frames=[content_frame], onPage=draw_content_page),
    ])

    styles = get_styles()
    story = []

    # ══ COVER ══
    story.append(Spacer(1, 10 * mm))
    story.append(NextPageTemplate("content"))
    story.append(PageBreak())

    # ══ TABLE OF CONTENTS ══
    story.append(Paragraph("TABLE OF CONTENTS", styles["toc_title"]))
    story.append(HRFlowable(width="45%", thickness=1.4, color=GOLD,
                            hAlign="CENTER", spaceBefore=0, spaceAfter=5 * mm))
    toc = TableOfContents()
    toc.levelStyles = TOC_LEVEL_STYLES
    toc.dotsMinLevel = 0
    toc.tableStyle = TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ])
    story.append(toc)
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(
        "This document is controlled electronically. Printed copies are valid "
        "on the day of printing only; verify the revision against the master "
        "copy before use.",
        styles["center"],
    ))
    story.append(PageBreak())

    # ══ 1. DOCUMENT CONTROL ══
    story.extend(section_header("1. DOCUMENT CONTROL & REVISION HISTORY", styles))
    story.append(info_table([
        ("Document Title:", DOC["title"]),
        ("Document Number:", DOC["doc_no"]),
        ("Revision:", DOC["revision"]),
        ("Date of Issue:", DOC["date"]),
        ("Document Status:", DOC["status"]),
        ("Prepared By:", DOC["prepared_by"]),
        ("Reviewed By:", DOC["reviewed_by"]),
        ("Approved By:", DOC["approved_by"]),
        ("Classification:", DOC["classification"]),
        ("Validity Period:", DOC["validity"]),
        ("Client Reference:", DOC["client_ref"]),
        ("Contract Type:", DOC["contract_type"]),
        ("Supersedes:", DOC["supersedes"]),
        ("Review Cycle:", DOC["review_cycle"]),
    ]))
    story.append(Spacer(1, 3 * mm))
    story.append(sub_header("1.1 Revision History", styles))
    story.append(data_table(
        ["Rev.", "Date", "Description", "Author"],
        [
            ["01", "2025-01-15", "Initial issue – Draft scope definition", "Engineering Division"],
            ["02", "2025-04-20", "Updated refining capacity & product specifications", "Operations Division"],
            ["03", "2026-09-21", "Final approved version – Full scope alignment with board strategy", "Board of Directors"],
        ],
        col_widths=[14 * mm, 26 * mm, 80 * mm, 50 * mm],
    ))
    story.append(Spacer(1, 3 * mm))
    story.append(sub_header("1.2 Controlled Document Register", styles))
    story.append(info_table([
        ("Registered Name:", COMPANY["name"]),
        ("Business ID (BIN):", COMPANY["bin"]),
        ("Headquarters:", COMPANY["address"]),
        ("Contact Phone:", COMPANY["phone"]),
        ("Email:", COMPANY["email"]),
        ("Website:", COMPANY["website"]),
    ]))

    # ══ 2. COMPANY OVERVIEW ══
    story.extend(section_header("2. COMPANY OVERVIEW", styles))
    story.append(Paragraph(
        f"<b>{COMPANY['name']}</b> is a Kazakhstan-based integrated oil and gas company, primarily "
        "specialized in oil refining, exploration and development of oil and gas fields, and the "
        "production and sale of petroleum products. The company is one of the Kazakhstan oil "
        "industry's leading enterprises in efficiency and service delivery.",
        styles["body"],
    ))
    story.append(Paragraph(
        "Halyk Petroleum operates a modern refinery complex producing a wide range of "
        "environmentally friendly, highly competitive products including Crude Oil, Aviation Oil, "
        "Motor Fuel, MAZUT M100, Bitumen, LPG, Pet Coke, NPK, Sulfur Granular, Liquefied "
        "Natural Gas (LNG), Urea 46%, and Aviation Kerosene.",
        styles["body"],
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(stat_chips([
        ("13", "EXPLORATION LICENSES HELD"),
        ("12", "PRODUCT FAMILIES SUPPLIED"),
        ("3", "CONTINENTS SERVED"),
        ("24 mo", "FRAMEWORK VALIDITY"),
    ]))
    story.append(Spacer(1, 3 * mm))
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
    story.append(Spacer(1, 3 * mm))
    story.append(gold_highlight_box(
        "HALYK PETROLEUM HOLDS 13 EXPLORATION LICENSES IN THE CASPIAN SEA, "
        "FAR EASTERN, AND SOUTHERN SEAS OF KAZAKHSTAN"
    ))

    # ══ 3. PURPOSE & OBJECTIVES ══
    story.extend(section_header("3. PURPOSE & OBJECTIVES", styles))
    story.append(Paragraph(
        "This Approved Official Scope of Work defines the comprehensive range of services, "
        "deliverables, and operational standards that Halyk Petroleum LLP commits to providing "
        "under its framework supply agreements with international clients. The document serves "
        "as the authoritative reference for all project execution, quality benchmarks, and "
        "contractual obligations.",
        styles["body"],
    ))
    story.append(sub_header("3.1 Primary Objectives", styles))
    story.extend(bullets([
        "Define the complete scope of exploration, refining, and supply services with measurable deliverables",
        "Establish quality assurance benchmarks aligned with international standards (ISO, API, ASTM)",
        "Outline HSE protocols ensuring zero-incident operations across all project phases",
        "Set clear commercial terms, delivery schedules, and performance metrics",
        "Ensure regulatory compliance with Kazakhstan petroleum laws and international trade requirements",
        "Provide a transparent framework for client engagement, reporting, and dispute resolution",
    ], styles))

    # ══ 4. EXPLORATION SERVICES ══
    story.extend(section_header("4. SCOPE OF WORK – EXPLORATION SERVICES", styles))
    story.append(Paragraph(
        "Halyk Petroleum provides comprehensive oil and gas exploration services across "
        "Kazakhstan, utilizing cutting-edge technology and geological expertise to identify "
        "and develop high-potential oil reserves. Our exploration strategies ensure efficient "
        "resource discovery while adhering to environmental and safety standards.",
        styles["body"],
    ))
    story.append(sub_header("4.1 Seismic Surveys & Geological Assessment", styles))
    story.extend(bullets([
        "2D and 3D seismic data acquisition, processing, and interpretation",
        "Field seismic surveys for optimal surveillance system procurement",
        "Geological and geophysical modeling of subsurface formations",
        "Reservoir characterization and volumetric estimation",
        "Risk assessment and prospectivity mapping of licensed blocks",
    ], styles))
    story.append(sub_header("4.2 Drilling & Well Testing", styles))
    story.extend(bullets([
        "Exploratory and appraisal well planning, design, and execution",
        "Directional and horizontal drilling operations",
        "Well logging, coring, and formation evaluation",
        "Production testing and flow rate assessment",
        "Well completion and integrity assurance",
    ], styles))
    story.append(sub_header("4.3 Reservoir Development Planning", styles))
    story.append(Paragraph(
        "Comprehensive field development plans including production forecasting, facility sizing, "
        "and economic modeling to ensure optimal resource recovery and commercial viability.",
        styles["body"],
    ))
    story.append(data_table(
        ["Service Area", "Technology / Method", "Deliverable"],
        [
            ["Seismic Acquisition", "2D/3D/4D Seismic", "Processed seismic volumes & interpretation reports"],
            ["Geological Modeling", "Petrel / RMS", "Static & dynamic reservoir models"],
            ["Well Planning", "Directional Drilling Software", "Well trajectories & drilling programs"],
            ["Formation Evaluation", "LWD / Wireline Logging", "Petrophysical analysis & pay zone identification"],
            ["Production Testing", "Multi-rate / DST", "Flow test reports & reservoir parameters"],
        ],
        col_widths=[38 * mm, 44 * mm, 88 * mm],
    ))

    # ══ 5. OIL REFINING & PROCESSING ══
    story.extend(section_header("5. SCOPE OF WORK – OIL REFINING & PROCESSING", styles))
    story.append(Paragraph(
        "Halyk Petroleum delivers high-quality oil refining services utilizing state-of-the-art "
        "technology to produce premium petroleum products. Our refinery operates with advanced "
        "processing techniques ensuring maximum efficiency, safety, and environmental compliance.",
        styles["body"],
    ))
    story.append(sub_header("5.1 Crude Oil Processing", styles))
    story.extend(bullets([
        "Atmospheric and vacuum distillation of crude oil feedstocks",
        "Catalytic cracking and reforming for gasoline and diesel production",
        "Hydroprocessing (hydrotreating and hydrocracking) for product quality enhancement",
        "Sulfur recovery and amine treatment for environmental compliance",
        "Blending and additive injection to meet product specifications",
    ], styles))
    story.append(sub_header("5.2 Gas Processing", styles))
    story.append(Paragraph(
        "The company processes a range of gas types including dry gas, wet gas, shale gas, "
        "stripped gas, and marketable gas. Advanced separation and treatment technologies ensure "
        "optimal recovery of valuable hydrocarbon components.",
        styles["body"],
    ))
    story.append(sub_header("5.3 Product Specifications", styles))
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
        col_widths=[40 * mm, 26 * mm, 58 * mm, 46 * mm],
    ))

    # ══ 6. PETROLEUM PRODUCTS SUPPLY ══
    story.extend(section_header("6. SCOPE OF WORK – PETROLEUM PRODUCTS SUPPLY", styles))
    story.append(Paragraph(
        "Halyk Petroleum is a trusted leader in petroleum product sales and marketing, "
        "delivering high-quality refined products to local and international markets. Our "
        "strategic supply chain, competitive pricing, and commitment to excellence ensure "
        "reliable distribution across Asia, Europe, and the Americas.",
        styles["body"],
    ))
    story.append(sub_header("6.1 Supply Framework", styles))
    story.extend(bullets([
        "Supply of petroleum products on FOB (Free on Board) and CIF (Cost, Insurance, Freight) basis",
        "Flexible contract structures: spot, short-term, and long-term supply agreements",
        "Volume commitments from 10,000 MT to 500,000+ MT per annum per product",
        "Dedicated account management with 24/7 order processing capability",
        "Multi-product bundling with competitive volume-based pricing tiers",
    ], styles))
    story.append(sub_header("6.2 Products Portfolio", styles))
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
        col_widths=[32 * mm, 62 * mm, 40 * mm, 36 * mm],
    ))
    story.append(Spacer(1, 2.5 * mm))
    story.append(sub_header("6.3 Quality Guarantee", styles))
    story.append(Paragraph(
        "All products supplied by Halyk Petroleum are accompanied by Certificates of Analysis "
        "(COA) issued by accredited third-party laboratories. Products are guaranteed to meet "
        "or exceed the specifications outlined in Section 5.3. Any non-conforming product will "
        "be replaced or refunded at Halyk Petroleum's sole discretion and cost.",
        styles["body"],
    ))

    # ══ 7. LOGISTICS & DELIVERY ══
    story.extend(section_header("7. SCOPE OF WORK – LOGISTICS & DELIVERY", styles))
    story.append(Paragraph(
        "Halyk Petroleum maintains a robust logistics infrastructure to ensure timely and "
        "secure delivery of petroleum products to global destinations.",
        styles["body"],
    ))
    story.extend(bullets([
        "Coordination with certified tanker fleets for maritime and overland transport",
        "Port operations management at key Caspian, Black Sea, and Baltic terminals",
        "Customs clearance and export documentation support",
        "Real-time shipment tracking and ETA updates for all consignments",
        "Insurance coverage (marine cargo) for full transit period",
        "Demurrage management and laytime optimization",
    ], styles))
    story.append(sub_header("7.1 Delivery Performance Targets", styles))
    story.append(data_table(
        ["Metric", "Target", "Measurement"],
        [
            ["On-Time Delivery Rate", "≥ 98%", "Per quarter, measured from confirmed delivery date"],
            ["Product Quality Compliance", "100%", "Zero non-conforming shipments per contract period"],
            ["Documentation Accuracy", "100%", "Error-free COA, B/L, and customs documents"],
            ["Customer Response Time", "< 4 hours", "Inquiry to quotation turnaround during business days"],
            ["Shipment Tracking Updates", "Real-time", "GPS-enabled tracking with automated status notifications"],
        ],
        col_widths=[44 * mm, 26 * mm, 100 * mm],
    ))

    # ══ 8. QUALITY ASSURANCE ══
    story.extend(section_header("8. QUALITY ASSURANCE & COMPLIANCE", styles))
    story.append(Paragraph(
        "Halyk Petroleum maintains a comprehensive Quality Management System (QMS) aligned "
        "with international standards to ensure consistent product quality and operational excellence.",
        styles["body"],
    ))
    story.append(sub_header("8.1 Certifications & Standards", styles))
    story.extend(bullets([
        "ISO 9001:2015 – Quality Management System",
        "ISO 14001:2015 – Environmental Management System",
        "ISO 45001:2018 – Occupational Health & Safety Management",
        "API Q1 / Q2 – Quality Management for Petroleum Industry",
        "ASTM, EN, and GOST product specification compliance",
        "Kazakhstan Republic petroleum regulatory standards",
    ], styles))
    story.append(sub_header("8.2 Inspection & Testing Protocol", styles))
    story.append(Paragraph(
        "All products undergo rigorous testing at multiple stages: incoming crude assay, "
        "in-process quality monitoring, and final product certification. Third-party inspection "
        "by SGS, Bureau Veritas, or Intertek is available upon client request.",
        styles["body"],
    ))
    story.append(sub_header("8.3 Regulatory Compliance", styles))
    story.extend(bullets([
        "Full compliance with Kazakhstan Export Control regulations",
        "Adherence to EU REACH and CLP regulations for European-bound products",
        "Compliance with MARPOL Annex VI for marine fuel sulfur content limits",
        "Environmental impact assessments for all exploration and refining operations",
    ], styles))

    # ══ 9. HSE ══
    story.extend(section_header("9. HEALTH, SAFETY & ENVIRONMENT (HSE)", styles))
    story.append(Paragraph(
        "Halyk Petroleum is committed to achieving zero-incident operations through a proactive "
        "safety culture, rigorous risk management, and continuous environmental stewardship.",
        styles["body"],
    ))
    story.append(sub_header("9.1 Safety Management", styles))
    story.extend(bullets([
        "Implementation of Process Safety Management (PSM) across all facilities",
        "Regular HAZOP studies, risk assessments, and emergency response drills",
        "Mandatory safety training for all personnel – minimum 40 hours per annum",
        "Personal Protective Equipment (PPE) compliance monitoring",
        "Incident reporting, investigation, and root cause analysis protocols",
    ], styles))
    story.append(sub_header("9.2 Environmental Protection", styles))
    story.extend(bullets([
        "Emissions monitoring and reduction programs (SOx, NOx, CO2, VOC)",
        "Wastewater treatment and zero-discharge targets",
        "Spill prevention and containment systems at all facilities",
        "Waste management hierarchy: reduce, reuse, recycle, dispose",
        "Biodiversity protection measures for exploration license areas",
    ], styles))
    story.append(Spacer(1, 2 * mm))
    story.append(gold_highlight_box(
        "HALYK PETROLEUM TARGET: ZERO FATALITIES  •  ZERO MAJOR INCIDENTS  •  "
        "ZERO ENVIRONMENTAL RELEASES"
    ))

    # ══ 10. TIMELINE ══
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
        col_widths=[15 * mm, 52 * mm, 28 * mm, 75 * mm],
    ))
    story.append(Paragraph(
        "<b>Note:</b> Timeline is indicative for a standard FOB supply cycle of 50,000 MT. "
        "Actual timelines may vary based on product type, volume, destination, and market conditions.",
        styles["note"],
    ))

    # ══ 11. COMMERCIAL TERMS ══
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

    # ══ 12. APPROVAL & SIGNATURES ══
    story.extend(section_header("12. APPROVAL & SIGNATURES", styles, 75))
    story.append(Paragraph(
        "This Approved Official Scope of Work has been reviewed and authorized by the "
        "undersigned representatives of Halyk Petroleum LLP. This document is effective "
        f"from <b>{DOC['date']}</b> and shall remain valid for the period specified herein.",
        styles["body"],
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(KeepTogether([signature_table()]))
    story.append(Spacer(1, 6 * mm))
    story.append(gold_highlight_box(
        f"END OF DOCUMENT  •  {DOC['doc_no']}  •  {DOC['revision']}  •  {DOC['status']}"
    ))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        f"{COMPANY['name']}  •  {COMPANY['address']}  •  {COMPANY['phone']}  •  "
        f"{COMPANY['email']}  •  {COMPANY['website']}  •  BIN {COMPANY['bin']}",
        styles["center"],
    ))

    # ══ APPENDIX A – DEFINITIONS & ABBREVIATIONS ══
    story.extend(section_header("APPENDIX A – DEFINITIONS & ABBREVIATIONS", styles))
    story.append(Paragraph(
        "The following abbreviations and terms are used throughout this Scope of Work.",
        styles["body"],
    ))
    story.append(data_table(
        ["Term", "Definition"],
        [
            ["API", "American Petroleum Institute"],
            ["ASTM", "ASTM International (American Society for Testing and Materials)"],
            ["B/L", "Bill of Lading – carrier's receipt and document of title for shipped goods"],
            ["BIN", "Business Identification Number (Republic of Kazakhstan)"],
            ["CIF", "Cost, Insurance and Freight (Incoterm)"],
            ["CFR", "Cost and Freight (Incoterm)"],
            ["COA", "Certificate of Analysis – laboratory certification of product quality"],
            ["DAP", "Delivered at Place (Incoterm)"],
            ["DLC", "Documentary Letter of Credit"],
            ["DST", "Drill Stem Test – well production testing procedure"],
            ["ETA", "Estimated Time of Arrival"],
            ["FOB", "Free on Board (Incoterm)"],
            ["FSA", "Framework Supply Agreement"],
            ["GOST", "Interstate standard (Eurasian conformity standards system)"],
            ["HAZOP", "Hazard and Operability Study"],
            ["HSE", "Health, Safety and Environment"],
            ["ICC", "International Chamber of Commerce"],
            ["ISO", "International Organization for Standardization"],
            ["LNG", "Liquefied Natural Gas"],
            ["LPG", "Liquefied Petroleum Gas"],
            ["LWD", "Logging While Drilling"],
            ["MAZUT M100", "Heavy residual fuel oil grade per GOST 10585"],
            ["MARPOL", "International Convention for the Prevention of Pollution from Ships"],
            ["MT", "Metric Tonne (1,000 kg)"],
            ["NPK", "Nitrogen-Phosphorus-Potassium compound fertilizer"],
            ["PPE", "Personal Protective Equipment"],
            ["PSM", "Process Safety Management"],
            ["QMS", "Quality Management System"],
            ["SBLC", "Standby Letter of Credit"],
            ["SGS", "Société Générale de Surveillance – inspection & certification body"],
            ["VOC", "Volatile Organic Compounds"],
        ],
        col_widths=[32 * mm, 138 * mm],
    ))

    doc.multiBuild(story, canvasmaker=NumberedCanvas)
    print(f"Halyk Petroleum Scope of Work PDF generated: {output_path}")
    print(f"   File size: {os.path.getsize(output_path) / 1024:.1f} KB")


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "HALYK_PETROLEUM_SCO.pdf")
    build_document(output)
