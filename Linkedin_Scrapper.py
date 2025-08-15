# -*- coding: utf-8 -*-
import os, csv, time, random, hashlib, argparse, logging, re, unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(filename="scraping.log", level=logging.INFO)
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")  # optionnel

# ---------- Utils ----------
def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.strip().lower())
    return re.sub(r"-{2,}", "-", s).strip("-")

def build_csv_path(job: str, location: str, base_dir="out") -> str:
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    return str(Path(base_dir) / f"jobs_{slugify(job)}_{slugify(location)}.csv")

def get_job_id_from_link(link: str) -> str | None:
    # Essaie d'extraire l'ID LinkedIn s'il est présent
    m = re.search(r"/jobs/view/(\d+)", link)
    if m: return m.group(1)
    m = re.search(r"currentJobId=(\d+)", link)
    if m: return m.group(1)
    return None

def make_id(title, company, location, keyword, link):
    jid = get_job_id_from_link(link)
    if jid:  # si on a un ID LinkedIn, c'est la meilleure clé
        return jid
    raw = f"{title}|{company}|{location}|{keyword}".encode("utf-8", "ignore")
    return hashlib.sha256(raw).hexdigest()[:16]

def load_existing_ids(csv_path):
    ids = set()
    if Path(csv_path).exists():
        with open(csv_path, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                ids.add(row.get("id_hash",""))
    return ids

def append_rows(csv_path, rows):
    exists = Path(csv_path).exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "id_hash","title","company","location","link",
            "posted_at_utc","collected_at_utc","source","keyword"
        ])
        if not exists:
            w.writeheader()
        for r in rows:
            w.writerow(r)

def slack_notify(rows, keyword):
    if not SLACK_WEBHOOK or not rows: return
    lines = [f"• <{r['link']}|{r['title']}> — {r['company']} ({r['location']})" for r in rows[:10]]
    text = f"🎯 *{keyword}* — {len(rows)} new jobs\n" + "\n".join(lines)
    try:
        requests.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
    except Exception as e:
        logging.warning(f"Slack error: {e}")

# ---------- Driver ----------
def make_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1366,900")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--lang=fr-FR")
    opts.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=opts)  # Selenium Manager -> pas de chromedriver manuel

# ---------- Core ----------
def build_search_url(job_title, location, past_hours=24, page=0, easy_apply=False):
    from urllib.parse import urlencode
    base = "https://www.linkedin.com/jobs/search/"
    params = {
        "keywords": job_title,
        "location": location,
        "origin": "JOB_SEARCH_PAGE_SEARCH_BUTTON",
        "refresh": "true",
        "f_TPR": f"r{past_hours*3600}",  # annonces publiées dans les X dernières heures
    }
    if easy_apply:
        params["f_AL"] = "true"
    if page > 0:
        params["start"] = str(page*25)
    return base + "?" + urlencode(params)

def scrape_linkedin_jobs(job_title, location, pages=1, past_hours=24, easy_apply=False):
    logging.info(f'Start scrape: "{job_title}" @ "{location}"')
    drv = make_driver(headless=True)
    collected = []
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

            # petit scroll pour charger les cartes
            last_h = 0
            for _ in range(4):
                drv.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(0.8, 1.6))
                h = drv.execute_script("return document.body.scrollHeight")
                if h == last_h: break
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
                if not title or not link: continue

                time_el = c.select_one("time")
                posted_iso = time_el["datetime"] if time_el and time_el.has_attr("datetime") else now

                collected.append({
                    "id_hash": make_id(title, company, location_txt, job_title, link),
                    "title": title,
                    "company": company,
                    "location": location_txt,
                    "link": link,
                    "posted_at_utc": posted_iso,
                    "collected_at_utc": now,
                    "source": "LinkedIn",
                    "keyword": job_title
                })

            time.sleep(random.uniform(1.0, 2.0))
    finally:
        drv.quit()
    logging.info(f"Scraped {len(collected)} rows.")
    return collected

# ---------- CLI ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", default="Développeur Java")
    ap.add_argument("--location", default="Paris")
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--past_hours", type=int, default=24)
    ap.add_argument("--csv", default=None, help="Chemin CSV (sinon auto par job+location)")
    args = ap.parse_args()

    csv_path = args.csv or build_csv_path(args.job, args.location)
    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)

    existing = load_existing_ids(csv_path)
    rows = scrape_linkedin_jobs(args.job, args.location, args.pages, args.past_hours, easy_apply=False)
    new_rows = [r for r in rows if r["id_hash"] not in existing]

    if new_rows:
        append_rows(csv_path, new_rows)
        logging.info(f"Added {len(new_rows)} new rows → {csv_path}")
        slack_notify(new_rows, args.job)
    else:
        logging.info(f"No new rows for {args.job} @ {args.location} (CSV: {csv_path})")

if __name__ == "__main__":
    main()
