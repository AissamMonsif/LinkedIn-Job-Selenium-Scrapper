import argparse
import logging
from pathlib import Path
from typing import Optional

from .core import scrape_linkedin_jobs
from .io import slack_notify
from .utils import build_csv_path, load_existing_ids, append_rows


def run_search(job: str, location: str, pages: int = 1, past_hours: int = 24, csv_path: Optional[str] = None, easy_apply: bool = False) -> int:
    csv_out = csv_path or build_csv_path(job, location)
    Path(csv_out).parent.mkdir(parents=True, exist_ok=True)

    existing = load_existing_ids(csv_out)
    rows = scrape_linkedin_jobs(job, location, pages, past_hours, easy_apply)
    new_rows = [r for r in rows if r["id_hash"] not in existing]

    if new_rows:
        append_rows(csv_out, new_rows)
        logging.info(f"Added {len(new_rows)} new rows → {csv_out}")
        slack_notify(new_rows, job)
    else:
        logging.info(f"No new rows for {job} @ {location} (CSV: {csv_out})")
    return 0


def main():
    logging.basicConfig(filename="scraping.log", level=logging.INFO)
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", default="Développeur Java")
    ap.add_argument("--location", default="Paris")
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--past_hours", type=int, default=24)
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()

    return run_search(
        job=args.job,
        location=args.location,
        pages=args.pages,
        past_hours=args.past_hours,
        csv_path=args.csv,
        easy_apply=False,
    )


if __name__ == "__main__":
    raise SystemExit(main())

