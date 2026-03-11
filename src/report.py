from datetime import datetime

from analyzer import analyze
from extractor import extract_all
from map_view import create_map
from timeline import create_timeline


def create_report(images_data, map_html, timeline_html, analysis):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    insights_html = ""
    for insight in analysis.get("insights", []):
        insights_html += f"<li>{insight}</li>"

    cameras_html = ""
    for cam in analysis.get("unique_cameras", []):
        cameras_html += f"<span class='badge'>{cam}</span> "

    html = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>Image Intel Report</title>
        <style>
            body {{ font-family: Arial; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
            .header {{ background: #1B4F72; color: white; padding: 30px; border-radius: 10px; text-align: center; }}
            .section {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .stats {{ display: flex; gap: 20px; justify-content: center; }}
            .stat-card {{ background: #E8F4FD; padding: 15px 25px; border-radius: 8px; text-align: center; }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #1B4F72; }}
            .badge {{ background: #2E86AB; color: white; padding: 5px 10px; border-radius: 15px; margin: 3px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Image Intel Report</h1>
            <p>נוצר ב-{now}</p>
        </div>

        <div class="section">
            <h2>סיכום</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{analysis.get('total_images', 0)}</div>
                    <div>תמונות</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{analysis.get('images_with_gps', 0)}</div>
                    <div>עם GPS</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(analysis.get('unique_cameras', []))}</div>
                    <div>מכשירים</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>תובנות מרכזיות</h2>
            <ul>{insights_html}</ul>
        </div>

        <div class="section">
            <h2>מפה</h2>
            {map_html}
        </div>

        <div class="section">
            <h2>ציר זמן</h2>
            {timeline_html}
        </div>

        <div class="section">
            <h2>מכשירים</h2>
            {cameras_html}
        </div>

        <div style="text-align:center; color:#888; margin-top:30px;">
            Image Intel | האקתון 2025
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    # תיקון: fake_data הועבר לכאן מגוף הקובץ - כדי שלא ירוץ בכל import
    fake_data = [
        {
            "filename": "test1.jpg",
            "datetime": "2025:01:12 08:30:00",
            "latitude": 32.0853,
            "longitude": 34.7818,
            "camera_make": "Samsung",
            "camera_model": "Galaxy S23",
            "has_gps": True
        },
        {
            "filename": "test2.jpg",
            "datetime": "2025:01:13 09:00:00",
            "latitude": 31.7683,
            "longitude": 35.2137,
            "camera_make": "Apple",
            "camera_model": "iPhone 15 Pro",
            "has_gps": True
        },
        {
            "filename": "test3.jpg",
            "datetime": None,
            "latitude": None,
            "longitude": None,
            "camera_make": None,
            "camera_model": None,
            "has_gps": False
        }
    ]
    data = extract_all("C:\\Users\\user\\PyCharmMiscProject\\image_intel_project\\images\\sample_data")
    html = create_report(data, create_map(data), create_timeline(data), analyze(data))
    with open("test_report.html", "w", encoding="utf-8") as f:
        f.write(html)
print("Created report")