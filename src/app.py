import os
import tempfile
from io import BytesIO

from flask import Flask, render_template, request, Response
from reportlab.pdfgen import canvas

app = Flask(__name__)


@app.route('/')
def index():
    """דף הבית - טופס לבחירת תיקייה"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_images():
    """מקבל נתיבים לתמונות, מריץ את כל המודולים, מחזיר דו"ח"""

    photos = request.files.getlist('photos')

    folder_path = tempfile.mkdtemp()
    for photo in photos:
        path = os.path.join(folder_path, photo.filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        photo.save(path)

    # בדיקה שהנתיב קיים
    if not folder_path:
        return "לא הוזנו תמונות", 400

    folder_path = os.path.abspath(folder_path)

    if not os.path.isdir(folder_path):
        return "התמונות לא נמצאו", 400

    try:

        # שלב 1: שליפת נתונים
        from extractor import extract_all
        images_data = extract_all(folder_path)

        if not images_data:
            return "לא נמצאו תמונות בתיקייה", 400

        # שלב 2: יצירת מפה
        from map_view import create_map
        map_html = create_map(images_data)

        # שלב 3: ציר זמן
        from timeline import create_timeline
        timeline_html = create_timeline(images_data)

        # שלב 4: ניתוח
        from analyzer import analyze
        analysis = analyze(images_data)

        # שלב 5: הרכבת דו"ח
        from report import create_report
        report_html = create_report(images_data, map_html, timeline_html, analysis)

        style = """
        <style>
        .download-btn {
            background-color: #38bdf8;
            color: black;
            border: none;
            padding: 15px 30px;
            font-size: 1.2em;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .download-btn:hover {
            background-color: 0284c7;
            color: white;
            box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4);
        }
        </style>
        """

        report_html = report_html.replace("</head>", style + "</head>")

        button = """
        <form action="/download" method="GET">
            <button type="submit" class="download-btn">הורד PDF</button>
        </form>
        """

        report_html = report_html.replace('<div style="text-align:center; color:#888; margin-top:30px;">', button + '<div style="text-align:center; color:#888; margin-top:30px;">')
        print(report_html)

        return report_html

    except Exception as e:
        print("ERROR:", e)
        return f"שגיאה במהלך הניתוח: {str(e)}", 500

def fake_generate_pdf():
    buffer = BytesIO()

    c = canvas.Canvas(buffer)
    c.drawString(100, 750, "Hello PDF")
    c.save()

    buffer.seek(0)
    return buffer.read()

@app.route('/download')
def download_pdf():
    pdf_data = fake_generate_pdf()

    return Response(
        pdf_data,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=report.pdf"
        }
    )

if __name__ == '__main__':
    print("Image Intel server running...")
    app.run(debug=True)