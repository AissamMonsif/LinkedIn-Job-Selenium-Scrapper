from dataclasses import dataclass
from typing import TypedDict, Optional


@dataclass(frozen=True)
class Job:
    id_hash: str
    title: str
    company: str
    location: str
    link: str
    posted_at_utc: str
    collected_at_utc: str
    source: str
    keyword: str


class JobDict(TypedDict):
    id_hash: str
    title: str
    company: str
    location: str
    link: str
    posted_at_utc: str
    collected_at_utc: str
    source: str
    keyword: str

