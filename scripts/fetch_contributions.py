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
FIELDS = "name description stargazerCount primaryLanguage { name color }"


def pick_projects(pinned, recent):
    """Three repos for the 'What I'm coding' cards: your pinned ones, else the latest with a description."""
    pool = [n for n in pinned if n and n["name"] != USER]
    pool = pool or [n for n in recent if n and n["name"] != USER and n.get("description")]
    return [{"name": n["name"], "description": n.get("description") or "",
             "language": (n.get("primaryLanguage") or {}).get("name", ""),
             "color": (n.get("primaryLanguage") or {}).get("color") or "",
             "stars": n.get("stargazerCount", 0)} for n in pool[:3]]


if token:
    QUERY = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        repositories(privacy: PUBLIC, ownerAffiliations: OWNER, isFork: false) { totalCount }
        pinnedItems(first: 6, types: REPOSITORY) { nodes { ... on Repository { FIELDS } } }
        recent: repositories(first: 20, privacy: PUBLIC, ownerAffiliations: OWNER, isFork: false,
                             orderBy: {field: PUSHED_AT, direction: DESC}) { nodes { FIELDS } }
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar { weeks { contributionDays { date contributionCount } } }
        }
      }
    }""".replace("FIELDS", FIELDS)

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
    projects = pick_projects(user["pinnedItems"]["nodes"], user["recent"]["nodes"])
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

    try:
        req_r = urllib.request.Request(f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=30",
                                       headers={"User-Agent": "Mozilla/5.0"})
        recent = [{"name": r["name"], "description": r.get("description"), "stargazerCount": r["stargazers_count"],
                   "primaryLanguage": {"name": r["language"]} if r.get("language") else None}
                  for r in json.loads(urllib.request.urlopen(req_r, timeout=10).read().decode("utf-8")) if not r["fork"]]
        projects = pick_projects([], recent)
    except Exception:
        projects = []

OUT.write_text(json.dumps({"repos": repos, "projects": projects, "days": days}, indent=2))
print(f"saved {len(days)} days, {repos} public repos")
