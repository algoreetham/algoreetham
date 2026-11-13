#!/usr/bin/env python3
"""Saves your last year of GitHub contributions to data/contributions.json."""
import datetime as dt
import json
import os
import re
import urllib.request
from pathlib import Path

USER = "algoreetham"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"

token = os.environ.get("GITHUB_TOKEN")

if token:
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
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    res = json.load(urllib.request.urlopen(req, timeout=30))
    if "errors" in res:
        raise SystemExit(res["errors"])

    user = res["data"]["user"]
    weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [{"date": d["date"], "count": d["contributionCount"]} for w in weeks for d in w["contributionDays"]]
    repos = user["repositories"]["totalCount"]
else:
    # Fallback for local execution without GITHUB_TOKEN: fetch public calendar & repos
    url = f"https://github.com/users/{USER}/contributions"
    req_cal = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req_cal, timeout=30).read().decode("utf-8")
    tooltips = dict(re.findall(r'<tool-tip[^>]*for=\"([^\"]+)\"[^>]*>(.*?)</tool-tip>', html, re.DOTALL))
    days_raw = re.findall(r'data-date=\"(\d{4}-\d{2}-\d{2})\".*?id=\"([^\"]+)\"', html)
    days = []
    for date, elem_id in days_raw:
        tip = tooltips.get(elem_id, "")
        m = re.search(r'(\d+)\s+contribution', tip)
        days.append({"date": date, "count": int(m.group(1)) if m else 0})

    try:
        req_u = urllib.request.Request(f"https://api.github.com/users/{USER}", headers={"User-Agent": "Mozilla/5.0"})
        uinfo = json.loads(urllib.request.urlopen(req_u, timeout=10).read().decode("utf-8"))
        repos = uinfo.get("public_repos", 0)
    except Exception:
        repos = 17

OUT.write_text(json.dumps({"repos": repos, "days": days}, indent=2))
print(f"saved {len(days)} days, {repos} public repos")
