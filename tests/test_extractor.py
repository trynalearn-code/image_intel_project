import pytest
import os

# בהתחלה, לפני שהמודול מוכן, אפשר לדלג
# pytest.importorskip("extractor")

def test_extract_metadata_returns_dict():
    from extractor import extract_metadata
    result = extract_metadata("images/sample_data/IMG_001.jpg")
    assert isinstance(result, dict)

def test_extract_metadata_has_required_fields():
    from extractor import extract_metadata
    result = extract_metadata("images/sample_data/IMG_001.jpg")
    required = ["filename", "datetime", "latitude", "longitude",
                "camera_make", "camera_model", "has_gps"]
    for field in required:
        assert field in result, f"Missing field: {field}"

def test_extract_metadata_gps_is_float_or_none():
    from extractor import extract_metadata
    result = extract_metadata("images/sample_data/IMG_001.jpg")
    if result["has_gps"]:
        assert isinstance(result["latitude"], float)
        assert isinstance(result["longitude"], float)
    else:
        assert result["latitude"] is None
        assert result["longitude"] is None

def test_extract_all_returns_list():
    from src.extractor import extract_all
    result = extract_all("images/sample_data")
    assert isinstance(result, list)
    assert len(result) > 0

def test_extract_all_handles_empty_folder(tmp_path):
    from extractor import extract_all
    result = extract_all(str(tmp_path))
    assert isinstance(result, list)
    assert len(result) == 0