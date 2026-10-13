
from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def safe_text(value):
    """Escape text before inserting it into a ReportLab paragraph."""
    if value is None:
        return "Not provided"
    return escape(str(value)).replace("\n", "<br/>")


def generate_interview_pdf(
    report,
    candidate_name="Candidate",
    role="Not specified",
):
    """Generate a PDF report and return its bytes."""

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="AI Interview Report",
        author="AI Interviewer",
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17365D"),
            spaceAfter=12,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#17365D"),
            spaceBefore=12,
            spaceAfter=6,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportBody",
            parent=styles["BodyText"],
            fontSize=9,
            leading=12,
            spaceAfter=5,
        )
    )

    story = [
        Paragraph("AI Interview Report", styles["ReportTitle"]),
        Paragraph(
            f"<b>Candidate:</b> {safe_text(candidate_name)}",
            styles["BodyText"],
        ),
        Paragraph(
            f"<b>Role:</b> {safe_text(role)}",
            styles["BodyText"],
        ),
        Paragraph(
            f"<b>Generated:</b> "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["BodyText"],
        ),
        Spacer(1, 12),
    ]

    # Overall score
    score = report.get(
        "overall_score",
        report.get("average_score", report.get("score")),
    )

    if score is not None:
        score_table = Table(
            [
                [
                    Paragraph("<b>Overall score</b>", styles["BodyText"]),
                    Paragraph(
                        f"<b>{safe_text(score)}/100</b>",
                        styles["BodyText"],
                    ),
                ]
            ],
            colWidths=[100 * mm, 60 * mm],
        )

        score_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor("#EAF0F8"),
                    ),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        story.extend([score_table, Spacer(1, 8)])

    def add_section(title, items):
        if not items:
            return

        story.append(
            Paragraph(safe_text(title), styles["SectionHeading"])
        )

        if isinstance(items, str):
            items = [items]

        for item in items:
            if isinstance(item, dict):
                item = item.get(
                    "text",
                    item.get("description", str(item)),
                )

            story.append(
                Paragraph(
                    "&#8226; " + safe_text(item),
                    styles["ReportBody"],
                )
            )

    # Summary
    summary = report.get("summary")
    if summary:
        story.append(
            Paragraph("Summary", styles["SectionHeading"])
        )
        story.append(
            Paragraph(safe_text(summary), styles["ReportBody"])
        )

    # Strengths and improvement areas
    add_section("Strengths", report.get("strengths", []))

    add_section(
        "Areas to Improve",
        report.get(
            "improvement_areas",
            report.get("areas_for_improvement", []),
        ),
    )

    add_section(
        "Recommendations",
        report.get("recommendations", []),
    )

    # Topic scores
    topic_scores = report.get("topic_scores", {})

    if isinstance(topic_scores, dict) and topic_scores:
        story.append(
            Paragraph("Topic Scores", styles["SectionHeading"])
        )

        rows = [
            [
                Paragraph("<b>Topic</b>", styles["ReportBody"]),
                Paragraph("<b>Score</b>", styles["ReportBody"]),
            ]
        ]

        for topic, value in topic_scores.items():
            if isinstance(value, dict):
                value = value.get(
                    "score",
                    value.get("average_score", value),
                )

            rows.append(
                [
                    Paragraph(safe_text(topic), styles["ReportBody"]),
                    Paragraph(safe_text(value), styles["ReportBody"]),
                ]
            )

        table = Table(
            rows,
            colWidths=[115 * mm, 45 * mm],
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#EAF0F8"),
                    ),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )

        story.append(table)

    document.build(story)

    return buffer.getvalue()


def save_interview_pdf(
    report,
    output_path,
    candidate_name="Candidate",
    role="Not specified",
):
    """Save a report to disk and return the output path."""

    pdf_bytes = generate_interview_pdf(
        report=report,
        candidate_name=candidate_name,
        role=role,
    )

    with open(output_path, "wb") as file:
        file.write(pdf_bytes)

    return output_path
