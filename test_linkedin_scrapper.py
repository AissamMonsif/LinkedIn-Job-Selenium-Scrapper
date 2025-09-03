from linkedin_scraper.core import build_search_url
from linkedin_scraper.utils import slugify


def test_slugify_basic():
    assert slugify("Développeur Java / Paris") == "developpeur-java-paris"


def test_build_search_url_has_params():
    url = build_search_url("software engineer", "san francisco", past_hours=24, page=0)
    assert "keywords=software+engineer" in url
    assert "location=san+francisco" in url
    assert "f_TPR=r86400" in url
