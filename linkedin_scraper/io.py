import logging
import os
from typing import Iterable, Dict

import requests


SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")


def slack_notify(rows: Iterable[Dict[str, str]], keyword: str):
    rows = list(rows)
    if not SLACK_WEBHOOK or not rows:
        return
    lines = [
        f"• <{r['link']}|{r['title']}> — {r['company']} ({r['location']})"
        for r in rows[:10]
    ]
    text = f"🎯 *{keyword}* — {len(rows)} new jobs\n" + "\n".join(lines)
    try:
        requests.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
    except Exception as e:
        logging.warning(f"Slack error: {e}")

