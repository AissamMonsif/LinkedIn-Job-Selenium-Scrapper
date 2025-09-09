import os
import re
import csv
import hashlib
import unicodedata
from pathlib import Path
from typing import Iterable, List, Set, Dict


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.strip().lower())
    return re.sub(r"-{2,}", "-", s).strip("-")


def build_csv_path(job: str, location: str, base_dir: str = "out") -> str:
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    return str(Path(base_dir) / f"jobs_{slugify(job)}_{slugify(location)}.csv")


def get_job_id_from_link(link: str):
    m = re.search(r"/jobs/view/(\d+)", link)
    if m:
        return m.group(1)
    m = re.search(r"currentJobId=(\d+)", link)
    if m:
        return m.group(1)
    return None


def make_id(title: str, company: str, location: str, keyword: str, link: str) -> str:
    jid = get_job_id_from_link(link)
    if jid:
        return jid
    raw = f"{title}|{company}|{location}|{keyword}".encode("utf-8", "ignore")
    return hashlib.sha256(raw).hexdigest()[:16]


def load_existing_ids(csv_path: str) -> Set[str]:
    ids: Set[str] = set()
    p = Path(csv_path)
    if p.exists():
        with p.open(newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                ids.add(row.get("id_hash", ""))
    return ids


def append_rows(csv_path: str, rows: Iterable[Dict[str, str]]):
    exists = Path(csv_path).exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "id_hash",
                "title",
                "company",
                "location",
                "link",
                "posted_at_utc",
                "collected_at_utc",
                "source",
                "keyword",
            ],
        )
        if not exists:
            w.writeheader()
        for r in rows:
            w.writerow(r)

