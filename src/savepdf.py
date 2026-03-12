from reportlab.pdfgen import canvas
from io import BytesIO


def generate_pdf(text: str) -> bytes:
    buffer = BytesIO()

    c = canvas.Canvas(buffer)
    c.drawString(100, 750, text)
    c.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes