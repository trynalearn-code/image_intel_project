from flask import Flask, render_template, request
import os

app = Flask(__name__)


@app.route('/')
def index():
    """דף הבית - טופס לבחירת תיקייה"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_images():
    # """מקבל נתיב תיקייה, מריץ את כל המודולים, מחזיר דו"ח"""
    #
    # folder_path = request.form.get('folder_path')
    #
    # # בדיקה שהנתיב קיים
    # if not folder_path:
    #     return "לא הוזן נתיב לתיקייה", 400
    #
    # folder_path = os.path.abspath(folder_path)
    #
    # if not os.path.isdir(folder_path):
    #     return "תיקייה לא נמצאה", 400
    photos = request.files.getlist('photos')
    print(photos)

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

        return report_html

    except Exception as e:
        print("ERROR:", e)
        return f"שגיאה במהלך הניתוח: {str(e)}", 500


if __name__ == '__main__':
    print("Image Intel server running...")
    app.run(debug=True)