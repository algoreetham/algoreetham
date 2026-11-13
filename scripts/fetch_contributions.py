#!/usr/bin/env python3
"""Saves your last year of GitHub contributions to data/contributions.json."""
import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

USER = "algoreetham"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER, isFork: false) { totalCount }
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}"""

now = dt.datetime.now(dt.timezone.utc)
body = json.dumps({
    "query": QUERY,
    "variables": {"login": USER, "from": (now - dt.timedelta(days=364)).isoformat(), "to": now.isoformat()},
}).encode()
req = urllib.request.Request(
    "https://api.github.com/graphql", data=body,
    headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
)
res = json.load(urllib.request.urlopen(req, timeout=30))
if "errors" in res:
    raise SystemExit(res["errors"])

user = res["data"]["user"]
weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]
days = [{"date": d["date"], "count": d["contributionCount"]} for w in weeks for d in w["contributionDays"]]
OUT.write_text(json.dumps({"repos": user["repositories"]["totalCount"], "days": days}))
print(f"saved {len(days)} days, {user['repositories']['totalCount']} public repos")
