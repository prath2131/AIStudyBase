from fpdf import FPDF
from database import Document
from typing import Sequence


def generate_report(documents: Sequence[Document]) -> bytes:
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", size=16)
    pdf.cell(0, 10, "My Study Library", ln=True)

    pdf.set_font("Helvetica", size=12)
    pdf.ln(5)

    for doc in documents:
        display_name = doc.filename
        upload_date = doc.created_at.strftime("%Y-%m-%d")

        pdf.cell(
            0,
            8,
            f"{display_name} - uploaded {upload_date}",
            ln=True
        )

    return bytes(pdf.output())