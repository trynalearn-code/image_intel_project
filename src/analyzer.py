import math
from json import JSONDecodeError

import requests
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


def total_images(images_data):
    return len(images_data)

def images_with_gps(images_data):
    return len([image for image in images_data if image["has_gps"]])

def unique_cameras(images_data):
    return list(set([image["camera_model"] for image in images_data]))

def date_range(image_data):
    dates = [image["datetime"] for image in image_data if image["datetime"]]
    if not dates:
        return ""
    start = "-".join(sorted(dates)[0].split(" ")[0].split(":"))
    end = "-".join(sorted(dates)[-1].split(" ")[0].split(":"))
    return {"start": start, "end": end}

def detect_camera_switches(images_data):
    sorted_images = sorted(
        [img for img in images_data if img["datetime"]],
        key=lambda x: x["datetime"]
    )
    switches = []
    for i in range(1, len(sorted_images)):
        prev_cam = sorted_images[i-1].get("camera_model")
        curr_cam = sorted_images[i].get("camera_model")
        if prev_cam and curr_cam and prev_cam != curr_cam:
            switches.append({
                "date": sorted_images[i]["datetime"],
                "from": prev_cam,
                "to": curr_cam
            })
    return switches

def detect_geographical_concentration(images_data):
    concentrations = {}
    for i in range(len(images_data)-1):
        if not images_data[i]["has_gps"]:
            continue
        for j in range(len(images_data)-i):
            if not images_data[j+i]["has_gps"]:
                continue

            if images_data[i] is images_data[j+i]:
                continue

            lat1, lon1 = images_data[i]["latitude"], images_data[i]["longitude"]
            lat2, lon2 = images_data[j+i]["latitude"], images_data[j+i]["longitude"]

            dlat = (lat2 - lat1) * 111
            dlon = (lon2 - lon1) * 111 * math.cos(math.radians((lat1 + lat2) / 2))

            distance = math.sqrt(dlat ** 2 + dlon ** 2)

            if distance < 1:
                url = "https://nominatim.openstreetmap.org/reverse"

                params = {
                    "lat": lat1,
                    "lon": lon1,
                    "format": "json"
                }

                headers = {
                    "User-Agent": "my-python-app"
                }

                response = requests.get(url, params=params, headers=headers)
                try:
                    data = response.json()

                    concentrations[data["address"].get("city")] = concentrations.get(data["address"].get("city"), set())
                    concentrations[data["address"].get("city")].add(images_data[i]["filename"])
                    concentrations[data["address"].get("city")].add(images_data[j+i]["filename"])
                except JSONDecodeError:
                    print(response.status_code)
    return concentrations

def time_gaps(images_data):
    filtered_images = [image for image in images_data if image["datetime"]]
    sorted_images = sorted(filtered_images, key=lambda image: image["datetime"])
    gaps = []
    for i in range(1, len(sorted_images)):
        if sorted_images[i] is sorted_images[i-1]:
            continue

        perv_image = sorted_images[i-1]
        curr_image = sorted_images[i]

        date1 = perv_image["datetime"].split(" ")[0]
        date2 = curr_image["datetime"].split(" ")[0]

        time1 = perv_image["datetime"].split(" ")[1]
        time2 = curr_image["datetime"].split(" ")[1]

        year1 = date1.split(":")[0]
        year2 = date2.split(":")[0]
        if year1 != year2:
            gap = abs(int(year1) - int(year2))
            if gap == 1:
                gaps.append({
                    "gap": f"שנה {gap}",
                    "from": perv_image["filename"],
                    "to": curr_image["filename"]
                })
            else:
                gaps.append({
                    "gap": f"{gap} שנים",
                    "from": perv_image["filename"],
                    "to": curr_image["filename"]
                })
            continue

        month1 = date1.split(":")[1]
        month2 = date2.split(":")[1]
        if month1 != month2:
            gap = abs(int(month1) - int(month2))
            if gap == 1:
                gaps.append({
                    "gap": f"חודש {gap}",
                    "from": perv_image["filename"],
                    "to": curr_image["filename"]
                })
            else:
                if gap == 1:
                    gaps.append({
                        "gap": f"{gap} חודשים",
                        "from": perv_image["filename"],
                        "to": curr_image["filename"]
                    })
            continue

        day1 = date1.split(":")[2]
        day2 = date2.split(":")[2]
        hour1 = time1.split(":")[0]
        hour2 = time2.split(":")[0]

        if day1 != day2:
            gap = abs(int(day1) - int(day2))
            if gap != 1:
                gaps.append({
                    "gap": f"{gap} ימים",
                    "from": perv_image["filename"],
                    "to": curr_image["filename"]
                })
                continue

            gap = abs(int(hour1) - (int(hour2) + 24))
            if gap >= 12:
                gaps.append({
                    "gap": f"{gap} שעות",
                    "from": perv_image["filename"],
                    "to": curr_image["filename"]
                })
                continue

        gap = abs(int(hour1) - int(hour2))
        if gap >= 12:
            gaps.append({
                "gap": f"{gap} שעות",
                "from": perv_image["filename"],
                "to": curr_image["filename"]
            })
    return gaps

def detect_return_to_location(images_data):
    locations = {}
    last_city = None
    geolocator = Nominatim(user_agent="my_unique_list_app", timeout=10)

    reverse_geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)

    for image in images_data:
        if not image["has_gps"]:
            continue
        coords = (image["latitude"], image["longitude"])
        location = reverse_geocode(coords)
        if not location:
            continue
        address = location.raw.get('address', {})
        city = address.get('city') or address.get('town') or address.get('village')
        if city == last_city:
            continue
        locations[city] = locations.get(city, 0) + 1
        last_city = city
    return {location:locations[location] for location in locations if locations[location] > 1}


def analyze(images_data: list[dict]) -> dict:
    """
    מנתח את הנתונים ומוצא דפוסים.

    מקבל: רשימת מילונים מ-extract_all
    מחזיר: מילון עם תובנות, לדוגמה:
    {
        "total_images": 12,
        "images_with_gps": 10,
        "unique_cameras": ["Samsung Galaxy S23", "Apple iPhone 15 Pro"],
        "date_range": {"start": "2025-01-12", "end": "2025-01-16"},
        "insights": [
            "נמצאו 3 מכשירים שונים",
            "הסוכן החליף מכשיר ב-13/01",
            "ריכוז תמונות באזור תל אביב"
        ]
    }
    """

    camera_switches_insights = []
    for switch in detect_camera_switches(images_data):
        date = "/".join(switch["date"].split(" ")[0].split(":"))
        camera_switches_insights.append(f"ב-{date} הסוכן עבר ממכשיר {switch["from"]} ל-{switch["to"]}")

    geographical_concentration_insights = []
    for city, concentration in detect_geographical_concentration(images_data).items():
            geographical_concentration_insights.append(f"ריכוז של {len(concentration)} תמונות באזור {city}")

    time_gaps_insights = []
    for gap in time_gaps(images_data):
        time_gaps_insights.append(f"יש פער של {gap["gap"]} מהתמונה {gap["from"]} לתמונה-{gap["to"]}")

    return_to_location_insights = []
    for city, times in detect_return_to_location(images_data).items():
        return_to_location_insights.append(f"חזר ל {city} {times} פעמים")

    return {
        "total_images": total_images(images_data),
        "images_with_gps": images_with_gps(images_data),
        "unique_cameras": unique_cameras(images_data),
        "date_range": date_range(images_data),
        "insights": [
            f"נמצאו {len(unique_cameras(images_data))} מכשירים שונים" if len(unique_cameras(images_data)) > 1 else  "נמצא מחזיר 1" if len(unique_cameras(images_data)) == 1 else "לא נמצאו מכשירים"
        ] + camera_switches_insights + geographical_concentration_insights + time_gaps_insights + return_to_location_insights
    }