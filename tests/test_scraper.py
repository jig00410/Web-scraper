"""
Tests for scraper_service.py
Run with: python -m pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.scraper_service import scrape_website_data


def test_invalid_url():
    result = scrape_website_data("not-a-url")
    assert result["success"] == False
    assert "Invalid URL" in result["error"]

def test_missing_url():
    result = scrape_website_data("")
    assert result["success"] == False

def test_valid_url_structure():
    """Test that a valid URL returns expected keys."""
    result = scrape_website_data("https://example.com")
    assert "success" in result
    assert "title" in result
    assert "headings" in result
    assert isinstance(result["headings"], list)
