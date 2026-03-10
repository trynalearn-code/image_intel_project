from PIL import Image
from PIL.ExifTags import TAGS
from pathlib import Path
import os

"""
extractor.py - שליפת EXIF מתמונות
צוות 1, זוג A

ראו docs/api_contract.md לפורמט המדויק של הפלט.

"""
def dms_to_decimal(dms_tuple, ref):
    degrees = float(dms_tuple[0])
    minutes = float(dms_tuple[1])
    seconds = float(dms_tuple[2])
    decimal = degrees + minutes / 60 + seconds / 3600
    if ref in [b'S', b'W', 'S', 'W']:
        decimal = -decimal
    return decimal

def has_gps(data: dict):
    return "GPSInfo" in data and 1 in data and 2 in data and 3 in data and 4 in data



def latitude(data: dict):
    try:
        gps = data.get("GPSInfo")
        if not gps or 1 not in gps or 2 not in gps:
            return None
        return dms_to_decimal(gps[2], gps[1])
    except Exception as e:
        return None

def longitude(data: dict):
    try:
        gps = data.get("GPSInfo")
        if not gps or 3 not in gps or 4 not in gps:
            return None
        return dms_to_decimal(gps[4], gps[3])
    except Exception as e:
        return None

def datatime(data: dict):
    return data["DateTimeOriginal"]


def camera_make(data: dict):
    return data["Make"]


def camera_model(data: dict):
    return data["Model"]


def extract_metadata(image_path):
    """
    שולף EXIF מתמונה בודדת.

    Args:
        image_path: נתיב לקובץ תמונה

    Returns:
        dict עם: filename, datetime, latitude, longitude,
              camera_make, camera_model, has_gps
    """
    path = Path(image_path)

    # תיקון: טיפול בתמונה בלי EXIF - בלי זה, exif.items() נופל עם AttributeError
    try:
        img = Image.open(image_path)
        exif = img._getexif()
    except Exception:
        exif = None

    if exif is None:
        return {
            "filename": path.name,
            "datetime": None,
            "latitude": None,
            "longitude": None,
            "camera_make": None,
            "camera_model": None,
            "has_gps": False
        }

    data = {}
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        data[tag] = value


    # תיקון: הוסר print(data) שהיה כאן - הדפיס את כל ה-EXIF הגולמי על כל תמונה

    exif_dict = {
        "filename": path.name,
        "datetime": datatime(data),
        "latitude": latitude(data),
        "longitude": longitude(data),
        "camera_make": camera_make(data),
        "camera_model": camera_model(data),
        "has_gps": has_gps(data)
    }
    return exif_dict


def extract_all(folder_path):
    """
    שולף EXIF מכל התמונות בתיקייה.

    Args:
        folder_path: נתיב לתיקייה

    Returns:
        list של dicts (כמו extract_metadata)
    """
    images=[]
    for image in os.listdir(folder_path):
        images.append(extract_metadata(os.path.join(folder_path,image)))
    return images
