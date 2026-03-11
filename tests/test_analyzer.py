def get_fake_data():
    return [
        {"filename": "t1.jpg", "latitude": 32.0, "longitude": 34.7,
         "has_gps": True, "camera_make": "Samsung", "camera_model": "Galaxy S23",
         "datetime": "2025:01:12 08:30:00"},
        {"filename": "t2.jpg", "latitude": 31.7, "longitude": 35.2,
         "has_gps": True, "camera_make": "Apple", "camera_model": "iPhone 15 Pro",
         "datetime": "2025:01:13 09:00:00"},
    ]

def test_analyze_returns_dict():
    from analyzer import analyze
    result = analyze(get_fake_data())
    assert isinstance(result, dict)

def test_analyze_has_required_fields():
    from analyzer import analyze
    result = analyze(get_fake_data())
    assert "total_images" in result
    assert "images_with_gps" in result
    assert "unique_cameras" in result
    assert "insights" in result

def test_analyze_counts_correctly():
    from analyzer import analyze
    result = analyze(get_fake_data())
    assert result["total_images"] == 2
    assert result["images_with_gps"] == 2

def test_analyze_handles_empty():
    from analyzer import analyze
    result = analyze([])
    assert result["total_images"] == 0