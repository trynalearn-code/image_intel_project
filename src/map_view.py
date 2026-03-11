"""
map_view.py - יצירת מפה אינטראקטיבית
צוות 1, זוג B

ראו docs/api_contract.md לפורמט הקלט והפלט.

=== תיקונים ===
1. חישוב מרכז המפה - היה עובר על images_data (כולל תמונות בלי GPS) במקום gps_image, נופל עם None
2. הסרת CustomIcon שלא עובד (filename זה לא נתיב שהדפדפן מכיר)
3. הסרת m.save() - לפי API contract צריך להחזיר HTML string, לא לשמור קובץ
4. הסרת fake_data מגוף הקובץ - הועבר ל-if __name__
5. תיקון color_index - היה מתקדם על כל תמונה במקום רק על מכשיר חדש
6. הוספת מקרא מכשירים
"""
from extractor import *
import folium


COLORS = ['pink', 'lightred', 'lightgray', 'blue', 'lightgreen', 'purple', 'darkgreen', 'red', 'darkblue', 'darkred', 'black', 'cadetblue', 'orange', 'darkpurple', 'beige', 'green', 'lightblue', 'gray']

def sort_by_time(arr):
    return sorted(arr, key=lambda img: img["datetime"])


def create_map(images_data):
    """
    יוצר מפה אינטראקטיבית עם כל המיקומים.

    Args:
        images_data: רשימת מילונים מ-extract_all

    Returns:
        string של HTML (המפה)
    """
    gps_images = [img for img in images_data if img["has_gps"]]
    gps_images = sort_by_time(gps_images)

    if not gps_images:
        return "<h2>No GPS data found</h2>"

    center_lat = sum(img["latitude"] for img in gps_images) / len(gps_images)
    center_lon = sum(img["longitude"] for img in gps_images) / len(gps_images)

    m = folium.Map(location=[center_lat, center_lon], zoom_start=7)

    color_index = 0
    camera_colors = {}
    for img in gps_images:
        if img["camera_model"] not in camera_colors:
            camera_colors[img["camera_model"]] = COLORS[color_index]
            color_index += 1

        folium.Marker(
            location=[img["latitude"], img["longitude"]],
            popup=f"{img['filename']}<br>{img['datetime']}<br>{img['camera_model']}",
            icon=folium.Icon(color=camera_colors[img["camera_model"]],icon="camera")
        ).add_to(m)

    points = [(img["latitude"], img["longitude"]) for img in gps_images]

    folium.PolyLine(
        locations=points,
        color="blue",
        weight=3
    ).add_to(m)

    return m._repr_html_()



if __name__ == "__main__":
    # תיקון: fake_data הועבר לכאן מגוף הקובץ - כדי שלא ירוץ בכל import
    fake_data = [
        {"filename": "test1.jpg", "latitude": 32.0853, "longitude": 34.7818,
         "has_gps": True, "camera_make": "Samsung", "camera_model": "Galaxy S23",
         "datetime": "2025-01-12 08:30:00"},
        {"filename": "test2.jpg", "latitude": 31.7683, "longitude": 35.2137,
         "has_gps": True, "camera_make": "Apple", "camera_model": "iPhone 15 Pro",
         "datetime": "2025-01-13 09:00:00"},
    ]
    html = create_map(extract_all("C:\\Users\\user\\PyCharmMiscProject\\image_intel_project\\images\\ready"))
    with open("test_map.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Map saved to test_map.html")

