#!/usr/bin/env python3
"""
Professional Resume/CV PDF Generator
Generates a beautifully designed resume using ReportLab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os

# ─── Color Palette ───────────────────────────────────────────────────────────
PRIMARY      = HexColor("#1a365d")   # Deep navy
ACCENT       = HexColor("#2b6cb0")   # Medium blue
LIGHT_ACCENT = HexColor("#ebf4ff")   # Very light blue
DARK_TEXT     = HexColor("#1a202c")   # Near black
MED_TEXT      = HexColor("#4a5568")   # Medium gray
LIGHT_TEXT    = HexColor("#718096")   # Light gray
DIVIDER       = HexColor("#cbd5e0")   # Subtle divider
WHITE         = HexColor("#ffffff")
HIGHLIGHT     = HexColor("#ed8936")   # Orange accent for tags


# ─── Sample Resume Data ─────────────────────────────────────────────────────
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


# ─── Styles ──────────────────────────────────────────────────────────────────
def get_styles():
    return {
        "name": ParagraphStyle(
            "Name",
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=32,
            textColor=PRIMARY,
            spaceAfter=2 * mm,
        ),
        "title": ParagraphStyle(
            "Title",
            fontName="Helvetica",
            fontSize=12,
            leading=16,
            textColor=ACCENT,
            spaceAfter=4 * mm,
            letterSpacing=1.5,
        ),
        "contact": ParagraphStyle(
            "Contact",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=MED_TEXT,
            alignment=TA_LEFT,
        ),
        "section_header": ParagraphStyle(
            "SectionHeader",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=PRIMARY,
            spaceBefore=6 * mm,
            spaceAfter=2 * mm,
            letterSpacing=2,
        ),
        "summary": ParagraphStyle(
            "Summary",
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=DARK_TEXT,
            spaceAfter=2 * mm,
        ),
        "job_role": ParagraphStyle(
            "JobRole",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=DARK_TEXT,
            spaceAfter=1 * mm,
        ),
        "job_meta": ParagraphStyle(
            "JobMeta",
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=12,
            textColor=LIGHT_TEXT,
            spaceAfter=2 * mm,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=MED_TEXT,
            leftIndent=12,
            bulletIndent=0,
            spaceBefore=1 * mm,
        ),
        "edu_degree": ParagraphStyle(
            "EduDegree",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=DARK_TEXT,
        ),
        "edu_detail": ParagraphStyle(
            "EduDetail",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=MED_TEXT,
        ),
        "skill_cat": ParagraphStyle(
            "SkillCat",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=14,
            textColor=PRIMARY,
        ),
        "skill_items": ParagraphStyle(
            "SkillItems",
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=MED_TEXT,
        ),
        "cert": ParagraphStyle(
            "Cert",
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=MED_TEXT,
            leftIndent=12,
            bulletIndent=0,
            spaceBefore=1 * mm,
        ),
        "project_name": ParagraphStyle(
            "ProjectName",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=DARK_TEXT,
        ),
        "project_desc": ParagraphStyle(
            "ProjectDesc",
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=MED_TEXT,
            spaceAfter=2 * mm,
        ),
    }


# ─── Custom Page with Header Accent Bar ──────────────────────────────────────
def draw_page(canvas_obj, doc):
    """Draw page decorations: top accent bar and footer."""
    width, height = A4

    # Top accent bar
    canvas_obj.saveState()
    canvas_obj.setFillColor(PRIMARY)
    canvas_obj.rect(0, height - 8 * mm, width, 8 * mm, fill=1, stroke=0)

    # Thin accent line below bar
    canvas_obj.setFillColor(ACCENT)
    canvas_obj.rect(0, height - 9 * mm, width, 1 * mm, fill=1, stroke=0)

    # Footer
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.setFillColor(LIGHT_TEXT)
    canvas_obj.drawCentredString(
        width / 2, 10 * mm,
        f"Alexandra Chen  •  Resume  •  Page {doc.page}"
    )

    # Bottom accent line
    canvas_obj.setFillColor(DIVIDER)
    canvas_obj.rect(20 * mm, 14 * mm, width - 40 * mm, 0.3 * mm, fill=1, stroke=0)

    canvas_obj.restoreState()


# ─── Section Divider ─────────────────────────────────────────────────────────
def section_divider():
    return HRFlowable(
        width="100%", thickness=0.5, color=DIVIDER,
        spaceBefore=1 * mm, spaceAfter=2 * mm
    )


# ─── Build the PDF ───────────────────────────────────────────────────────────
def build_resume(output_path):
    width, height = A4
    margin_left = 22 * mm
    margin_right = 22 * mm
    margin_top = 18 * mm
    margin_bottom = 20 * mm

    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=margin_left,
        rightMargin=margin_right,
        topMargin=margin_top,
        bottomMargin=margin_bottom,
        title="Alexandra Chen – Resume",
        author="Alexandra Chen",
    )

    frame = Frame(
        margin_left, margin_bottom,
        width - margin_left - margin_right,
        height - margin_top - margin_bottom,
        id="main",
    )
    template = PageTemplate(id="resume", frames=[frame], onPage=draw_page)
    doc.addPageTemplates([template])

    styles = get_styles()
    story = []

    # ── Header ────────────────────────────────────────────────────────────
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(RESUME["name"], styles["name"]))
    story.append(Paragraph(RESUME["title"].upper(), styles["title"]))

    # Contact info in a compact layout
    c = RESUME["contact"]
    contact_line = (
        f'{c["email"]}  &nbsp;|&nbsp;  {c["phone"]}  &nbsp;|&nbsp;  '
        f'{c["location"]}  &nbsp;|&nbsp;  {c["linkedin"]}  &nbsp;|&nbsp;  {c["github"]}'
    )
    story.append(Paragraph(contact_line, styles["contact"]))
    story.append(Spacer(1, 3 * mm))
    story.append(section_divider())

    # ── Summary ───────────────────────────────────────────────────────────
    story.append(Paragraph("PROFESSIONAL SUMMARY", styles["section_header"]))
    story.append(Paragraph(RESUME["summary"], styles["summary"]))
    story.append(section_divider())

    # ── Experience ────────────────────────────────────────────────────────
    story.append(Paragraph("EXPERIENCE", styles["section_header"]))

    for job in RESUME["experience"]:
        job_elements = []
        # Role and company
        role_text = f'{job["role"]}  —  <font color="{ACCENT.hexval()}">{job["company"]}</font>'
        job_elements.append(Paragraph(role_text, styles["job_role"]))

        # Location and period
        meta_text = f'{job["location"]}  •  {job["period"]}'
        job_elements.append(Paragraph(meta_text, styles["job_meta"]))

        # Bullets
        for bullet in job["bullets"]:
            bullet_para = Paragraph(
                f'<bullet>&bull;</bullet> {bullet}',
                styles["bullet"]
            )
            job_elements.append(bullet_para)

        job_elements.append(Spacer(1, 3 * mm))
        story.append(KeepTogether(job_elements))

    story.append(section_divider())

    # ── Education ─────────────────────────────────────────────────────────
    story.append(Paragraph("EDUCATION", styles["section_header"]))

    for edu in RESUME["education"]:
        edu_elements = []
        edu_text = f'{edu["degree"]}  —  <font color="{ACCENT.hexval()}">{edu["school"]}</font>'
        edu_elements.append(Paragraph(edu_text, styles["edu_degree"]))

        period_detail = f'{edu["period"]}  •  {edu["detail"]}'
        edu_elements.append(Paragraph(period_detail, styles["edu_detail"]))
        edu_elements.append(Spacer(1, 2 * mm))
        story.append(KeepTogether(edu_elements))

    story.append(section_divider())

    # ── Technical Skills ──────────────────────────────────────────────────
    story.append(Paragraph("TECHNICAL SKILLS", styles["section_header"]))

    skill_rows = []
    for category, items in RESUME["skills"].items():
        skill_rows.append([
            Paragraph(f"{category}:", styles["skill_cat"]),
            Paragraph(" &nbsp;•&nbsp; ".join(items), styles["skill_items"]),
        ])

    skill_table = Table(skill_rows, colWidths=[35 * mm, None])
    skill_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("LEFTPADDING", (1, 0), (1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(skill_table)
    story.append(section_divider())

    # ── Certifications ────────────────────────────────────────────────────
    story.append(Paragraph("CERTIFICATIONS", styles["section_header"]))
    for cert in RESUME["certifications"]:
        story.append(Paragraph(f'<bullet>&bull;</bullet> {cert}', styles["cert"]))

    story.append(section_divider())

    # ── Projects ──────────────────────────────────────────────────────────
    story.append(Paragraph("OPEN SOURCE PROJECTS", styles["section_header"]))
    for proj in RESUME["projects"]:
        proj_elements = []
        proj_elements.append(Paragraph(proj["name"], styles["project_name"]))
        proj_elements.append(Paragraph(proj["description"], styles["project_desc"]))
        story.append(KeepTogether(proj_elements))

    # Build
    doc.build(story)
    print(f"✅ Resume PDF generated: {output_path}")
    print(f"   File size: {os.path.getsize(output_path) / 1024:.1f} KB")


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(__file__), "resume.pdf")
    build_resume(output)
