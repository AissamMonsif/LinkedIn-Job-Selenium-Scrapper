import logging
import random
import time
from datetime import datetime, timezone
from typing import List, Dict

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .driver import make_driver
from .utils import make_id


def build_search_url(job_title: str, location: str, past_hours: int = 24, page: int = 0, easy_apply: bool = False) -> str:
    from urllib.parse import urlencode

    base = "https://www.linkedin.com/jobs/search/"
    params = {
        "keywords": job_title,
        "location": location,
        "origin": "JOB_SEARCH_PAGE_SEARCH_BUTTON",
        "refresh": "true",
        "f_TPR": f"r{past_hours * 3600}",
    }
    if easy_apply:
        params["f_AL"] = "true"
    if page > 0:
        params["start"] = str(page * 25)
    return base + "?" + urlencode(params)


def scrape_linkedin_jobs(job_title: str, location: str, pages: int = 1, past_hours: int = 24, easy_apply: bool = False) -> List[Dict[str, str]]:
    logging.info(f'Start scrape: "{job_title}" @ "{location}"')
    drv = make_driver(headless=True)
    collected: List[Dict[str, str]] = []
    try:
        for p in range(max(1, pages)):
            url = build_search_url(job_title, location, past_hours, p, easy_apply)
            drv.get(url)

            try:
                WebDriverWait(drv, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul.jobs-search__results-list, div.base-card"))
                )
            except Exception:
                logging.info("Results list not found (maybe login wall) → skip page")
                continue

            last_h = 0
            for _ in range(4):
                drv.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(0.8, 1.6))
                h = drv.execute_script("return document.body.scrollHeight")
                if h == last_h:
                    break
                last_h = h

            html = drv.page_source
            soup = BeautifulSoup(html, "lxml")
            cards = soup.select("ul.jobs-search__results-list li") or soup.select("div.base-card")
            now = datetime.now(timezone.utc).isoformat()

            for c in cards:
                t = c.select_one("h3.base-search-card__title") or c.select_one("h3")
                comp = c.select_one("h4.base-search-card__subtitle") or c.select_one("h4")
                loc = c.select_one("span.job-search-card__location")
                link_el = c.select_one("a.base-card__full-link") or c.select_one("a")

                title = t.get_text(strip=True) if t else None
                company = comp.get_text(strip=True) if comp else ""
                location_txt = loc.get_text(strip=True) if loc else ""
                link = link_el["href"].split("?")[0] if link_el and link_el.has_attr("href") else ""
                if not title or not link:
                    continue

                time_el = c.select_one("time")
                posted_iso = time_el["datetime"] if time_el and time_el.has_attr("datetime") else now

                collected.append(
                    {
                        "id_hash": make_id(title, company, location_txt, job_title, link),
                        "title": title,
                        "company": company,
                        "location": location_txt,
                        "link": link,
                        "posted_at_utc": posted_iso,
                        "collected_at_utc": now,
                        "source": "LinkedIn",
                        "keyword": job_title,
                    }
                )

            time.sleep(random.uniform(1.0, 2.0))
    finally:
        drv.quit()
    logging.info(f"Scraped {len(collected)} rows.")
    return collected

