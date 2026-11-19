
from reportlab.lib.pagesizes import A4  # type: ignore[reportMissingModuleSource]
from reportlab.platypus import (  # type: ignore[reportMissingModuleSource]
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore[reportMissingModuleSource]
from reportlab.lib import colors  # type: ignore[reportMissingModuleSource]
from reportlab.lib.enums import TA_CENTER  # type: ignore[reportMissingModuleSource]
from xml.sax.saxutils import escape
from datetime import datetime
import os


def generate_meeting_pdf(
    meeting_name,
    transcript,
    summary,
    decisions,
    action_items
):
    os.makedirs("reports", exist_ok=True)

    filename = "reports/meeting_report_" + datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    ) + ".pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D")
    )

    story = []

    story.append(Paragraph("BELVO MINUTES", title_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph(
        "<b>Meeting:</b> " + escape(str(meeting_name)),
        styles["Normal"]
    ))
    story.append(Paragraph(
        "<b>Generated:</b> " + datetime.now().strftime("%d-%m-%Y %H:%M"),
        styles["Normal"]
    ))
    story.append(Spacer(1, 20))

    sections = [
        ("AI MEETING SUMMARY", summary),
        ("KEY DECISIONS", decisions),
        ("ACTION ITEMS", action_items),
        ("FULL TRANSCRIPT", transcript)
    ]

    for heading, content in sections:
        story.append(Paragraph(heading, styles["Heading2"]))
        story.append(Spacer(1, 8))

        if isinstance(content, list):
            if content:
                for item in content:
                    story.append(Paragraph(
                        "• " + escape(str(item)),
                        styles["Normal"]
                    ))
                    story.append(Spacer(1, 5))
            else:
                story.append(Paragraph(
                    "No information detected.",
                    styles["Normal"]
                ))
        else:
            safe_text = escape(str(content or "Not available"))
            for line in safe_text.splitlines():
                if line.strip():
                    story.append(Paragraph(line, styles["Normal"]))
                    story.append(Spacer(1, 4))

        story.append(Spacer(1, 15))

    doc.build(story)

    return filename
