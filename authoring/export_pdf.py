from __future__ import annotations

from io import BytesIO
from typing import Any


def export_pdf(manuscript: dict[str, Any]) -> bytes:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import inch

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=LETTER,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
        title=str(manuscript.get("title") or "Manuscript"),
    )
    styles = getSampleStyleSheet()
    story: list[Any] = []

    title = manuscript.get("title") or "Manuscript"
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 0.25 * inch))

    chapters = manuscript.get("chapters") or []
    for idx, ch in enumerate(chapters, start=1):
        ch_title = ch.get("title") or f"Chapter {idx}"
        story.append(Paragraph(ch_title, styles["Heading1"]))
        story.append(Spacer(1, 0.12 * inch))
        for seg in ch.get("segments") or []:
            text = (seg.get("text") or "").strip()
            if not text:
                continue
            for para in text.split("\n\n"):
                story.append(Paragraph(para.strip().replace("\n", " "), styles["BodyText"]))
                story.append(Spacer(1, 0.12 * inch))
        story.append(PageBreak())

    doc.build(story)
    return buf.getvalue()

