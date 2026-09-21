#!/usr/bin/env python3
"""
Professional Resume/CV PDF Generator
Generates a beautifully designed resume using ReportLab.

Improvements in this revision:
  * Name/title now sit inside the navy header band (no empty bar) and the
    contact line wraps cleanly with no dangling separator.
  * Section headings can no longer be orphaned at a page bottom
    (keepWithNext + KeepTogether per entry) – fixes the old "EDUCATION
    heading on page 1, degrees on page 2" break.
  * Skill chips, right-aligned date column, refined bullet typography.
  * "Page X of Y" footer, continuation-page header rule, and complete PDF
    metadata (title / author / subject / keywords / creator).
  * All resume content from the data block is rendered – nothing omitted.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether,
    Frame, PageTemplate, BaseDocTemplate, NextPageTemplate, CondPageBreak,
)
from reportlab.pdfgen import canvas as pdfcanvas
import os

# ─── Color Palette ───────────────────────────────────────────────────────────
PRIMARY      = HexColor("#1a365d")   # Deep navy
ACCENT       = HexColor("#2b6cb0")   # Medium blue
LIGHT_ACCENT = HexColor("#ebf4ff")   # Very light blue
DARK_TEXT    = HexColor("#1a202c")   # Near black
MED_TEXT     = HexColor("#4a5568")   # Medium gray
LIGHT_TEXT   = HexColor("#718096")   # Light gray
DIVIDER      = HexColor("#cbd5e0")   # Subtle divider
WHITE        = HexColor("#ffffff")
HIGHLIGHT    = HexColor("#ed8936")   # Orange accent
PALE_NAME    = HexColor("#90cdf4")   # Light blue on navy

PAGE_W, PAGE_H = A4
MARGIN_L = 18 * mm
MARGIN_R = 18 * mm
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R


# ─── Resume Data ─────────────────────────────────────────────────────────────
RESUME = {
    "name": "ALEXANDRA CHEN",
    "title": "Senior Software Engineer",
    "contact": {
        "email": "alexandra.chen@email.com",
        "phone": "+1 (415) 555-0192",
        "location": "San Francisco, CA",
        "linkedin": "linkedin.com/in/alexandrachen",
        "github": "github.com/alexchen",
    },
    "summary": (
        "Results-driven software engineer with 8+ years of experience designing and building "
        "scalable distributed systems. Passionate about clean architecture, developer experience, "
        "and mentoring teams. Led initiatives that improved system reliability by 99.95% and reduced "
        "deployment times by 60%. Seeking to leverage deep technical expertise in a Staff Engineer role."
    ),
    "experience": [
        {
            "role": "Senior Software Engineer",
            "company": "Stripe",
            "location": "San Francisco, CA",
            "period": "Jan 2021 – Present",
            "bullets": [
                "Architected and led the migration of a monolithic payment processing service to a "
                "microservices architecture, reducing latency by 40% and enabling independent scaling.",
                "Designed a real-time fraud detection pipeline processing 50M+ transactions daily "
                "using Kafka, Flink, and custom ML models, reducing chargebacks by 23%.",
                "Mentored a team of 6 engineers, establishing code review standards and leading "
                "weekly architecture deep-dives that improved team velocity by 35%.",
                "Implemented comprehensive observability with distributed tracing (Jaeger) and "
                "custom Grafana dashboards, cutting mean-time-to-resolution by 50%.",
            ],
        },
        {
            "role": "Software Engineer II",
            "company": "Airbnb",
            "location": "San Francisco, CA",
            "period": "Mar 2018 – Dec 2020",
            "bullets": [
                "Built the dynamic pricing recommendation engine serving 100K+ hosts, increasing "
                "average booking revenue by 18% through machine-learning-driven suggestions.",
                "Developed a GraphQL federation layer unifying 12 backend services, improving "
                "frontend development speed and reducing API response times by 30%.",
                "Led the adoption of container orchestration (Kubernetes) for 40+ microservices, "
                "reducing infrastructure costs by 25% through auto-scaling policies.",
            ],
        },
        {
            "role": "Software Engineer",
            "company": "Palantir Technologies",
            "location": "Palo Alto, CA",
            "period": "Jun 2016 – Feb 2018",
            "bullets": [
                "Developed data integration pipelines for government analytics platforms handling "
                "2TB+ of daily data ingestion with 99.9% uptime SLA.",
                "Created an internal developer toolkit that reduced onboarding time for new "
                "engineers from 3 weeks to 5 days.",
                "Collaborated with cross-functional teams to deliver a real-time threat "
                "intelligence dashboard used by 500+ analysts daily.",
            ],
        },
    ],
    "education": [
        {
            "degree": "M.S. Computer Science",
            "school": "Stanford University",
            "period": "2014 – 2016",
            "detail": "Focus: Distributed Systems & Machine Learning | GPA: 3.92/4.0",
        },
        {
            "degree": "B.S. Computer Science, Minor in Mathematics",
            "school": "University of California, Berkeley",
            "period": "2010 – 2014",
            "detail": "Magna Cum Laude | GPA: 3.88/4.0",
        },
    ],
    "skills": {
        "Languages": ["Python", "Go", "Java", "TypeScript", "Rust", "SQL"],
        "Infrastructure": ["Kubernetes", "Docker", "Terraform", "AWS", "GCP", "CI/CD"],
        "Data & ML": ["Kafka", "Spark", "Flink", "PostgreSQL", "Redis", "TensorFlow"],
        "Practices": ["Microservices", "System Design", "TDD", "Agile/Scrum", "Tech Lead"],
    },
    "certifications": [
        "AWS Solutions Architect – Professional (2023)",
        "Certified Kubernetes Administrator (CKA) (2022)",
    ],
    "projects": [
        {
            "name": "OpenTrace",
            "description": (
                "Open-source distributed tracing library for Go microservices. "
                "2.5K+ GitHub stars, adopted by 3 companies in production."
            ),
        },
    ],
}


# ─── Canvas with "Page X of Y" footer + continuation header ──────────────────
class NumberedCanvas(pdfcanvas.Canvas):
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
            self._draw_chrome(total)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _draw_chrome(self, total):
        w, h = PAGE_W, PAGE_H
        # footer
        self.setStrokeColor(DIVIDER)
        self.setLineWidth(0.5)
        self.line(MARGIN_L, 12 * mm, w - MARGIN_R, 12 * mm)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(LIGHT_TEXT)
        self.drawCentredString(w / 2, 8.4 * mm,
                               f"Alexandra Chen  •  Resume  •  Page {self._pageNumber} of {total}")
        # continuation pages: slim top rule with identity
        if self._pageNumber > 1:
            self.setFillColor(PRIMARY)
            self.rect(0, h - 6 * mm, w, 6 * mm, fill=1, stroke=0)
            self.setFillColor(HIGHLIGHT)
            self.rect(0, h - 7 * mm, w, 1 * mm, fill=1, stroke=0)
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(WHITE)
            self.drawString(MARGIN_L, h - 4.4 * mm, "ALEXANDRA CHEN")
            self.setFont("Helvetica", 8)
            self.setFillColor(PALE_NAME)
            self.drawRightString(w - MARGIN_R, h - 4.4 * mm, "Senior Software Engineer")


def draw_first_page(c, doc):
    """Navy header band with name, title and contact strip."""
    w, h = PAGE_W, PAGE_H
    band_h = 34 * mm
    c.setFillColor(PRIMARY)
    c.rect(0, h - band_h, w, band_h, fill=1, stroke=0)
    c.setFillColor(HIGHLIGHT)
    c.rect(0, h - band_h - 1.6 * mm, w, 1.6 * mm, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 25)
    c.setFillColor(WHITE)
    c.drawString(MARGIN_L, h - 16 * mm, RESUME["name"])
    c.setFont("Helvetica", 12.5)
    c.setFillColor(PALE_NAME)
    c.drawString(MARGIN_L, h - 24 * mm, RESUME["title"].upper())

    # contact strip
    strip_h = 9 * mm
    c.setFillColor(LIGHT_ACCENT)
    c.rect(0, h - band_h - 1.6 * mm - strip_h, w, strip_h, fill=1, stroke=0)
    parts = [
        RESUME["contact"]["email"],
        RESUME["contact"]["phone"],
        RESUME["contact"]["location"],
        RESUME["contact"]["linkedin"],
        RESUME["contact"]["github"],
    ]
    c.setFont("Helvetica", 8.4)
    c.setFillColor(MED_TEXT)
    c.drawCentredString(w / 2, h - band_h - 1.6 * mm - 5.8 * mm,
                        "   |   ".join(parts))


# ─── Styles ──────────────────────────────────────────────────────────────────
def get_styles():
    return {
        "section_header": ParagraphStyle(
            "SectionHeader", fontName="Helvetica-Bold", fontSize=11.5, leading=15,
            textColor=PRIMARY, spaceBefore=5.5 * mm, spaceAfter=1.2 * mm,
            keepWithNext=1,
        ),
        "summary": ParagraphStyle(
            "Summary", fontName="Helvetica", fontSize=9.6, leading=14.2,
            textColor=DARK_TEXT, alignment=TA_JUSTIFY, spaceAfter=1.5 * mm,
        ),
        "job_role": ParagraphStyle(
            "JobRole", fontName="Helvetica-Bold", fontSize=10.6, leading=14,
            textColor=DARK_TEXT,
        ),
        "job_meta": ParagraphStyle(
            "JobMeta", fontName="Helvetica-Oblique", fontSize=8.6, leading=12,
            textColor=LIGHT_TEXT, spaceAfter=1.4 * mm,
        ),
        "period": ParagraphStyle(
            "Period", fontName="Helvetica-Bold", fontSize=8.6, leading=14,
            textColor=ACCENT, alignment=2,  # right
        ),
        "bullet": ParagraphStyle(
            "Bullet", fontName="Helvetica", fontSize=9.2, leading=13.2,
            textColor=MED_TEXT, leftIndent=11, bulletIndent=0,
            spaceBefore=0.5 * mm, spaceAfter=0.5 * mm,
        ),
        "edu_degree": ParagraphStyle(
            "EduDegree", fontName="Helvetica-Bold", fontSize=10, leading=13.5,
            textColor=DARK_TEXT,
        ),
        "edu_detail": ParagraphStyle(
            "EduDetail", fontName="Helvetica", fontSize=8.8, leading=12.4,
            textColor=MED_TEXT, spaceAfter=1.6 * mm,
        ),
        "skill_cat": ParagraphStyle(
            "SkillCat", fontName="Helvetica-Bold", fontSize=9, leading=13,
            textColor=PRIMARY,
        ),
        "chip": ParagraphStyle(
            "Chip", fontName="Helvetica", fontSize=8.4, leading=11,
            textColor=DARK_TEXT, alignment=TA_CENTER,
        ),
        "cert": ParagraphStyle(
            "Cert", fontName="Helvetica", fontSize=9.2, leading=13.2,
            textColor=MED_TEXT, leftIndent=11, bulletIndent=0,
            spaceBefore=0.5 * mm, spaceAfter=0.5 * mm,
        ),
        "proj_name": ParagraphStyle(
            "ProjName", fontName="Helvetica-Bold", fontSize=9.8, leading=13,
            textColor=DARK_TEXT, spaceBefore=1.5 * mm,
        ),
        "proj_desc": ParagraphStyle(
            "ProjDesc", fontName="Helvetica", fontSize=9.2, leading=13,
            textColor=MED_TEXT, alignment=TA_JUSTIFY,
        ),
        "closing": ParagraphStyle(
            "Closing", fontName="Helvetica-Oblique", fontSize=8.4, leading=12,
            textColor=LIGHT_TEXT, alignment=TA_CENTER, spaceBefore=4 * mm,
        ),
    }


def section_header(text, styles, guard_mm=40):
    """Heading + rule, guarded so it can never be orphaned at a page bottom."""
    rule = HRFlowable(width="100%", thickness=0.8, color=DIVIDER,
                      spaceBefore=0, spaceAfter=2.4 * mm)
    rule.keepWithNext = 1
    return [CondPageBreak(guard_mm * mm),
            Paragraph(text, styles["section_header"]), rule]


def bullet_list(items, styles, style_key="bullet"):
    return [Paragraph('<bullet><font color="#ed8936"><b>&bull;</b></font></bullet>' + i,
                      styles[style_key]) for i in items]


def skill_chip_row(category, items, styles):
    chips = []
    for item in items:
        chips.append(Paragraph(item, styles["chip"]))
    inner = Table([chips])
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(len(items)):
        cmds.append(("BACKGROUND", (i, 0), (i, 0), LIGHT_ACCENT))
        cmds.append(("BOX", (i, 0), (i, 0), 0.4, DIVIDER))
    inner.setStyle(TableStyle(cmds))

    outer = Table([
        [Paragraph(category, styles["skill_cat"]), inner]
    ], colWidths=[32 * mm, CONTENT_W - 32 * mm])
    outer.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return outer


def experience_block(job, styles):
    head = Table([[
        Paragraph(f'<b>{job["role"]}</b> — <font color="#2b6cb0">{job["company"]}</font>',
                  styles["job_role"]),
        Paragraph(job["period"], styles["period"]),
    ]], colWidths=[CONTENT_W - 45 * mm, 45 * mm])
    head.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    flow = [head, Paragraph(f'{job["location"]}', styles["job_meta"])]
    flow.extend(bullet_list(job["bullets"], styles))
    flow.append(Spacer(1, 2.2 * mm))
    return KeepTogether(flow)


# ─── Build ───────────────────────────────────────────────────────────────────
def build_document(output_path):
    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN_L,
        rightMargin=MARGIN_R,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Alexandra Chen – Senior Software Engineer Resume",
        author="Alexandra Chen",
        subject="Resume / CV – Senior Software Engineer (Distributed Systems)",
        keywords=("Alexandra Chen, Resume, CV, Senior Software Engineer, "
                  "Distributed Systems, Kubernetes, Python, Go, AWS"),
        creator="generate_resume.py (ReportLab)",
    )
    first_frame = Frame(MARGIN_L, 16 * mm, CONTENT_W,
                        PAGE_H - 16 * mm - 47 * mm, id="first",
                        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    later_frame = Frame(MARGIN_L, 16 * mm, CONTENT_W,
                        PAGE_H - 16 * mm - 14 * mm, id="later",
                        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="first", frames=[first_frame], onPage=draw_first_page),
        PageTemplate(id="later", frames=[later_frame]),
    ])

    styles = get_styles()
    story = []

    # ── Professional summary ──
    story.extend(section_header("PROFESSIONAL SUMMARY", styles, 35))
    story.append(Paragraph(RESUME["summary"], styles["summary"]))

    # ── Experience ─
    story.extend(section_header("EXPERIENCE", styles, 55))
    for job in RESUME["experience"]:
        story.append(experience_block(job, styles))

    # ── Education ─
    story.extend(section_header("EDUCATION", styles, 30))
    for edu in RESUME["education"]:
        story.append(KeepTogether([
            Paragraph(f'<b>{edu["degree"]}</b> — <font color="#2b6cb0"><b>{edu["school"]}</b></font>',
                      styles["edu_degree"]),
            Paragraph(f'{edu["period"]}  •  {edu["detail"]}', styles["edu_detail"]),
        ]))

    # ── Technical skills ──
    story.extend(section_header("TECHNICAL SKILLS", styles, 48))
    skill_rows = [skill_chip_row(category, items, styles)
                  for category, items in RESUME["skills"].items()]
    skill_rows.append(Spacer(1, 1.5 * mm))
    story.append(KeepTogether(skill_rows))

    # ── Certifications ──
    story.extend(section_header("CERTIFICATIONS", styles, 25))
    story.extend(bullet_list(RESUME["certifications"], styles, style_key="cert"))

    # ── Open source ──
    story.extend(section_header("OPEN SOURCE PROJECTS", styles, 30))
    for proj in RESUME["projects"]:
        story.append(KeepTogether([
            Paragraph(f'<b>{proj["name"]}</b>  <font color="#718096">– github.com/alexchen</font>',
                      styles["proj_name"]),
            Paragraph(proj["description"], styles["proj_desc"]),
        ]))

    story.append(Paragraph("References available upon request.", styles["closing"]))

    # first page uses the banded template; later pages the slim one
    story.insert(0, NextPageTemplate("later"))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Resume PDF generated: {output_path}")
    print(f"   File size: {os.path.getsize(output_path) / 1024:.1f} KB")


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resume.pdf")
    build_document(output)
