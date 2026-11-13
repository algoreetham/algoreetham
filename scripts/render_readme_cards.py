#!/usr/bin/env python3
"""Draws every README card as an animated SVG into cards/.

Reads data/contributions.json (made by fetch_contributions.py), data/portrait.txt
and data/hackathons.json. STATIC=1 draws the final frame with no animation.
"""
import base64
import datetime as dt
import html
import json
import math
import os
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"
DATA_FILE = Path(os.environ.get("DATA_FILE", ROOT / "data" / "contributions.json"))
OUT = Path(os.environ.get("OUT_DIR", ROOT / "cards"))

# ---- your details (edit here) ----------------------------------------------
USER = "algoreetham"
FIRST, LAST = "Preetham", "Singh"
TAGLINE = ["a little curiosity, a lot of imagination", "and endless possibilities"]
CAPTION = ["Joint Secretary · Azure Developer Club", "B.Tech CSE (AI) · Alliance University"]
EMAIL = "preetham.singh.sp@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/preetham-singh-1b8676382/"
ARTH_URL = f"https://github.com/{USER}/ARTH-Automated-Response-To-Human-Intent"

STACK = [
    ("LANGUAGES", ["Python", "Java", "C++", "JavaScript", "HTML", "CSS"]),
    ("WEB", ["React", "Node.js", "Tailwind CSS", "Flask", "FastAPI"]),
    ("AI / ML", ["NumPy", "Pandas", "scikit-learn", "PyTorch", "TensorFlow"]),
    ("TOOLS", ["Git", "GitHub Actions", "Azure", "Figma"]),
]
NOW = [
    "Rebuilding ARTH as a voice assistant with a local AI model",
    "Learning LLMs and AI agents",
    "Working towards GSoC and open source",
]

PAPER, INK, BLUE, MUTE, LINE = "#f3f3f1", "#111111", "#3a56f5", "#6b6b66", "#d6d6d0"
RED, YELLOW = "#dc4c3a", "#f6c94a"
LEVELS = ["#e4e4df", "#c9d1fb", "#9eacf8", "#6f84f6", "#3a56f5", "#2338d6"]

# ---- fonts ------------------------------------------------------------------
FONTS = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serifi": ("Instrument Serif", "italic", 400, "serif-400-italic.woff"),
    "mono": ("JetBrains Mono", "normal", 400, "mono-400.woff"),
    "sans": ("Inter", "normal", 400, "sans-400.woff"),
    "sansm": ("Inter", "normal", 500, "sans-500.woff"),
}
_ttf = {}


def _font(key):
    if key not in _ttf:
        t = TTFont(ROOT / "fonts" / FONTS[key][3])
        _ttf[key] = (t.getBestCmap(), t["hmtx"], t["head"].unitsPerEm)
    return _ttf[key]


def tw(key, text, size, spacing=0):
    """Width of text in px, measured from the real font file."""
    cmap, hmtx, upm = _font(key)
    total = sum(hmtx[cmap.get(ord(c), ".notdef")][0] for c in text)
    return total / upm * size + spacing * len(text)


def face(key):
    fam, style, weight, fn = FONTS[key]
    b64 = base64.b64encode((ROOT / "fonts" / fn).read_bytes()).decode()
    return (f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
            f"src:url(data:font/woff;base64,{b64}) format('woff')}}")


def wrap(key, text, size, maxw):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if tw(key, trial, size) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


esc = html.escape

BASE_CSS = (".serif{font-family:'Instrument Serif',serif}"
            ".serifi{font-family:'Instrument Serif',serif;font-style:italic}"
            ".mono{font-family:'JetBrains Mono',monospace}"
            ".sans{font-family:Inter,sans-serif}.sansm{font-family:Inter,sans-serif;font-weight:500}")

ANIM = "" if STATIC else """
@keyframes rise{from{opacity:0;transform:translateY(16px)}}
@keyframes fade{from{opacity:0}}
@keyframes grow{from{transform:scaleY(0)}}
@keyframes pop{from{opacity:0;transform:scale(.2)}}
@keyframes swing{0%{opacity:0;transform:translateY(60px) rotate(-5deg)}60%{opacity:1;transform:translateY(-8px) rotate(1deg)}100%{opacity:1;transform:none}}
@keyframes blink{50%{opacity:0}}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(1.6)}}
@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(5px)}}
@keyframes typ{from{fill-opacity:0}}
.rise{animation:rise .8s cubic-bezier(.2,.7,.2,1) both;animation-delay:var(--d,0s)}
.fade{animation:fade .5s ease both;animation-delay:var(--d,0s)}
.ty{animation:typ .01s linear both;animation-delay:var(--d,0s)}
.grow{transform-box:fill-box;transform-origin:50% 100%;animation:grow .8s cubic-bezier(.2,.7,.2,1) both;animation-delay:var(--d,0s)}
.pop{transform-box:fill-box;transform-origin:50% 50%;animation:pop .35s cubic-bezier(.3,1.6,.5,1) both;animation-delay:var(--d,0s)}
.swing{transform-box:fill-box;transform-origin:0 100%;animation:swing 1s cubic-bezier(.2,.8,.2,1) both;animation-delay:var(--d,0s)}
.blink{animation:blink 1s steps(1) infinite}
.pulse{transform-box:fill-box;transform-origin:50% 50%;animation:pulse 1.8s ease-in-out infinite}
.nudge{animation:nudge 1.6s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.cnt{display:none}}
"""


def d(sec):
    return "" if STATIC else f' style="--d:{sec:.3f}s"'


def svg(w, h, body, fonts, defs="", title=""):
    css = "".join(face(f) for f in fonts) + BASE_CSS + ANIM
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(title)}"><title>{esc(title)}</title>'
            f"<defs>{defs}<style>{css}</style></defs>{body}</svg>")


def arrow(x, y, color, nudge=True):
    cls = ' class="nudge"' if (nudge and not STATIC) else ""
    return (f'<g{cls}><path d="M{x} {y} h18 M{x+11} {y-7} l7 7 l-7 7" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g>')


# ---- data -------------------------------------------------------------------
def load_data():
    raw = json.loads(DATA_FILE.read_text())
    days = [(dt.date.fromisoformat(x["date"]), x["count"]) for x in raw["days"]]
    days.sort()
    return days, raw.get("repos", 0)


def streaks(days):
    cur = 0
    seq = [c for _, c in days]
    i = len(seq) - 1
    if i >= 0 and seq[i] == 0:  # today may not be over yet
        i -= 1
    while i >= 0 and seq[i] > 0:
        cur += 1
        i -= 1
    return cur


def monthly(days):
    last = days[-1][0]
    keys = []
    y, m = last.year, last.month
    for _ in range(12):
        keys.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    keys.reverse()
    tot = {k: 0 for k in keys}
    for day, c in days:
        if (day.year, day.month) in tot:
            tot[(day.year, day.month)] += c
    return keys, tot, last


# ---- cards ------------------------------------------------------------------
def hero():
    W, H = 1000, 460
    p = [f'<rect width="{W}" height="{H}" rx="28" fill="{PAPER}"/>']
    p.append(f'<text x="56" y="84" class="mono rise"{d(0)} font-size="14" letter-spacing="3" fill="{MUTE}">HELLO, I AM</text>')
    p.append(f'<text x="56" y="206" class="serif rise"{d(.15)} font-size="126" fill="{INK}">{FIRST}</text>')
    fill = BLUE if STATIC else "url(#shine)"
    p.append(f'<text x="56" y="322" class="serifi rise"{d(.4)} font-size="126" fill="{fill}">{LAST}</text>')
    t0, step = 1.0, 0.035
    n = 0
    for li, line in enumerate(TAGLINE):
        y = 372 + li * 30
        chars = ""
        for ch in line:
            chars += f'<tspan class="ty"{d(t0 + n * step)}>{esc(ch)}</tspan>'
            n += 1
        p.append(f'<text x="56" y="{y}" xml:space="preserve" class="sans" font-size="21" fill="{INK}">{chars}</text>')
    endx = 56 + tw("sans", TAGLINE[-1], 21) + 4
    cur_cls = "" if STATIC else ' class="blink"'
    p.append(f'<rect{cur_cls} x="{endx:.1f}" y="{372 + 30 * (len(TAGLINE) - 1) - 18}" width="10" height="22" fill="{BLUE}"/>')
    
    # portrait panel
    px, py, pw, ph = 590, 40, 354, 330
    clip_def = f'<clipPath id="portrait-clip"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="20"/></clipPath>'

    exact_img = ROOT / "data" / "portrait_exact.jpg"
    if not exact_img.exists():
        exact_img = ROOT / "data" / "portrait_exact.png"

    if exact_img.exists():
        mime = "image/jpeg" if exact_img.suffix in (".jpg", ".jpeg") else "image/png"
        b64_img = base64.b64encode(exact_img.read_bytes()).decode()
        p.append(f'<g clip-path="url(#portrait-clip)" class="fade"{d(1.0)}>'
                 f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="{INK}"/>'
                 f'<image href="data:{mime};base64,{b64_img}" xlink:href="data:{mime};base64,{b64_img}" '
                 f'x="{px}" y="{py}" width="{pw}" height="{ph}" preserveAspectRatio="xMidYMid slice"/>'
                 f'</g>')
    else:
        p.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="20" fill="{INK}"/>')
        rows = (ROOT / "data" / "portrait.txt").read_text().split("\n")
        cols = max(len(r) for r in rows)
        fs, lh = 9, 10
        adv = tw("mono", "M", fs)
        ox = px + (pw - cols * adv) / 2
        oy = py + (ph - len(rows) * lh) / 2 + lh - 2
        for i, r in enumerate(rows):
            if not r.strip():
                continue
            p.append(f'<text x="{ox:.1f}" y="{oy + i * lh:.1f}" xml:space="preserve" class="mono fade"{d(1.0 + i * 0.03)} '
                     f'font-size="{fs}" fill="{PAPER}" fill-opacity=".92">{esc(r)}</text>')

    for i, c in enumerate(CAPTION):
        p.append(f'<text x="{px + pw / 2}" y="{402 + i * 24}" text-anchor="middle" class="mono rise"{d(1.2 + i * .15)} '
                 f'font-size="14" fill="{INK if i == 0 else MUTE}">{esc(c)}</text>')
    
    defs = clip_def
    if not STATIC:
        stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in
                        [(0, BLUE), (.42, BLUE), (.5, "#a9b6ff"), (.58, BLUE), (1, BLUE)])
        defs += (f'<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="440" y2="0">{stops}'
                 '<animateTransform attributeName="gradientTransform" type="translate" '
                 'values="-440 0;440 0;440 0" keyTimes="0;.3;1" dur="6s" begin="1.2s" repeatCount="indefinite"/>'
                 "</linearGradient>")
    return svg(W, H, "".join(p), ["serif", "serifi", "mono", "sans"], defs,
               f"{FIRST} {LAST}. {' '.join(TAGLINE)}")


def tile(color, fg, label, line1, line2, body, delay, count=None):
    W, H = 330, 320
    p = [f'<g class="swing"{d(delay)}>',
         f'<rect width="{W}" height="{H}" rx="26" fill="{color}"/>',
         f'<text x="32" y="52" class="mono" font-size="14" letter-spacing="2.5" fill="{fg}">{label}</text>',
         arrow(W - 52, 46, fg)]
    y1, y2 = 150, 212
    widest = max(tw("serif", count and f"{count:,}" or line1, 100), tw("serifi", line2, 100))
    fs = min(76, int((W - 64) / widest * 100))
    if count is not None and not STATIC:
        frames, t0, dt_ = 18, delay + .5, .05
        for i in range(frames):
            v = round(count * (1 - (1 - i / (frames - 1)) ** 3))
            p.append(f'<text class="cnt serif" x="32" y="{y1}" font-size="{fs}" fill="{fg}" opacity="0">{v:,}'
                     f'<set attributeName="opacity" to="1" begin="{t0 + i * dt_:.2f}s" dur="{dt_:.2f}s"/></text>')
        p.append(f'<text class="serif fade" x="32" y="{y1}" font-size="{fs}" fill="{fg}" '
                 f'style="--d:{t0 + frames * dt_:.2f}s">{count:,}</text>')
    else:
        text = f"{count:,}" if count is not None else line1
        p.append(f'<text class="serif" x="32" y="{y1}" font-size="{fs}" fill="{fg}">{esc(text)}</text>')
    p.append(f'<text class="serifi" x="32" y="{y2}" font-size="{fs}" fill="{fg}">{esc(line2)}</text>')
    for i, ln in enumerate(wrap("sans", body, 17, W - 64)):
        p.append(f'<text class="sans" x="32" y="{255 + i * 25}" font-size="17" fill="{fg}">{esc(ln)}</text>')
    p.append("</g>")
    return svg(W, H, "".join(p), ["serif", "serifi", "mono", "sans"], title=f"{label}: {line1} {line2}. {body}")


def activity(days):
    W, H = 1000, 400
    keys, tot, last = monthly(days)
    total = sum(c for _, c in days)
    done = keys[:-1] if last.day < 28 else keys
    best = max(done, key=lambda k: tot[k]) if done and max(tot[k] for k in done) > 0 else None
    mx = max(tot.values()) or 1
    p = [f'<rect width="{W}" height="{H}" rx="28" fill="{PAPER}"/>',
         f'<text x="56" y="62" class="mono" font-size="14" letter-spacing="2.5" fill="{MUTE}">THE LAST 12 MONTHS ON GITHUB</text>',
         f'<text x="56" y="140" font-size="78" fill="{INK}" class="rise"{d(0)}><tspan class="serif">{total:,} </tspan>'
         f'<tspan class="serifi">contributions</tspan></text>']
    base, maxh, bw, pitch, x0 = 338, 140, 38, 49, 56
    for i, k in enumerate(keys):
        h = max(5, tot[k] / mx * maxh)
        x = x0 + i * pitch
        partial = i == len(keys) - 1 and last.day < 28
        col = "#c9c9c3" if partial else (BLUE if k == best else INK)
        p.append(f'<rect class="grow"{d(.5 + i * .06)} x="{x}" y="{base - h:.1f}" width="{bw}" height="{h:.1f}" rx="6" fill="{col}"/>')
        p.append(f'<text x="{x + bw / 2}" y="{base + 28}" text-anchor="middle" class="mono" font-size="13" fill="{MUTE}">'
                 f'{dt.date(k[0], k[1], 1).strftime("%b")}</text>')
        if k == best:
            p.append(f'<text class="mono pop"{d(1.4)} x="{x + bw / 2}" y="{base - h - 12:.1f}" text-anchor="middle" '
                     f'font-size="14" fill="{BLUE}">{tot[k]:,}</text>')
    ndays = sum(1 for _, c in days if c > 0)
    busiest = max(c for _, c in days)
    stats = [(f"{streaks(days)}", " day" if streaks(days) == 1 else " days", "current streak"),
             (f"{ndays}", f" / {len(days)}", "days with a contribution"),
             (f"{busiest}", "", "on the busiest day")]
    sx = 720
    for i, (a, b, lab) in enumerate(stats):
        y = 150 + i * 92
        if i:
            p.append(f'<line x1="{sx}" x2="{W - 56}" y1="{y - 56}" y2="{y - 56}" stroke="{LINE}"/>')
        p.append(f'<g class="rise"{d(.8 + i * .15)}><text y="{y}" x="{sx}" font-size="50" fill="{INK}">'
                 f'<tspan class="serif">{a}</tspan><tspan class="serifi" fill="#9a9a94">{esc(b)}</tspan></text>'
                 f'<text x="{sx}" y="{y + 26}" class="sans" font-size="16" fill="{MUTE}">{lab}</text></g>')
    return svg(W, H, "".join(p), ["serif", "serifi", "mono", "sans"],
               title=f"{total} contributions in the last 12 months, {streaks(days)} day streak")


def graph(days):
    W, H = 1000, 318
    first_wd = (days[0][0].weekday() + 1) % 7  # Sunday first, like GitHub
    ncols = math.ceil((len(days) + first_wd) / 7)
    x0, pitch = 56, (W - 112) / ncols
    cell = pitch - 3.8
    top = 112
    nz = sorted(c for _, c in days if c > 0)
    q = [nz[int(len(nz) * f)] for f in (.25, .5, .75)] if nz else [1, 2, 3]

    def level(c):
        if c == 0:
            return 0
        return 1 + sum(c > t for t in q)

    p = [f'<rect width="{W}" height="{H}" rx="28" fill="{PAPER}"/>',
         f'<text x="56" y="76" font-size="50" fill="{INK}"><tspan class="serif">Every day, </tspan>'
         f'<tspan class="serifi" fill="{BLUE}">in blue</tspan></text>',
         f'<text x="{W - 56}" y="70" text-anchor="end" class="mono" font-size="14" letter-spacing="2.5" fill="{MUTE}">REFRESHED DAILY</text>']
    last_label_col = -9
    for i, (day, c) in enumerate(days):
        col, row = divmod(i + first_wd, 7)
        x, y = x0 + col * pitch, top + row * pitch
        p.append(f'<rect class="pop"{d(.3 + col * .014)} x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" '
                 f'rx="3.5" fill="{LEVELS[level(c)]}"/>')
        if day.day == 1 and col - last_label_col >= 3:
            p.append(f'<text x="{x:.1f}" y="{top + 7 * pitch + 18:.1f}" class="mono" font-size="13" fill="{MUTE}">{day.strftime("%b")}</text>')
            last_label_col = col
    ly = top + 7 * pitch + 52
    lx = W - 56 - 40 - 6 * (cell + 4) - 40
    p.append(f'<text x="{lx - 8}" y="{ly}" text-anchor="end" class="mono" font-size="13" fill="{MUTE}">less</text>')
    for i, c in enumerate(LEVELS):
        p.append(f'<rect x="{lx + i * (cell + 4):.1f}" y="{ly - 12}" width="{cell:.1f}" height="{cell:.1f}" rx="3.5" fill="{c}"/>')
    p.append(f'<text x="{lx + 6 * (cell + 4) + 4:.1f}" y="{ly}" class="mono" font-size="13" fill="{MUTE}">more</text>')
    return svg(W, H, "".join(p), ["serif", "serifi", "mono"], title="Contribution graph for the last year, in blue")


def stack():
    W = 1000
    p, y = [], 112
    label_w, x_start, x_end = 150, 56 + 150, W - 56
    for gi, (label, items) in enumerate(STACK):
        x, row_y = x_start, y
        p.append(f'<text x="56" y="{row_y + 23}" class="mono" font-size="13" letter-spacing="2.5" fill="{MUTE}">{label}</text>')
        for it in items:
            w = tw("sansm", it, 16) + 32
            if x + w > x_end:
                x, row_y = x_start, row_y + 46
            p.append(f'<g class="pop"{d(.3 + (gi * 5) * .05 + (x - x_start) / 4000)}>'
                     f'<rect x="{x:.1f}" y="{row_y}" width="{w:.1f}" height="34" rx="17" fill="#fff" stroke="{LINE}"/>'
                     f'<text x="{x + w / 2:.1f}" y="{row_y + 22}" text-anchor="middle" class="sansm" font-size="16" fill="{INK}">{esc(it)}</text></g>')
            x += w + 10
        y = row_y + 62
    H = y + 14
    head = (f'<rect width="{W}" height="{H}" rx="28" fill="{PAPER}"/>'
            f'<text x="56" y="76" font-size="50" fill="{INK}"><tspan class="serif">What I </tspan>'
            f'<tspan class="serifi" fill="{BLUE}">build with</tspan></text>')
    return svg(W, H, head + "".join(p), ["serif", "serifi", "mono", "sansm"], title="Tech stack: " + ", ".join(i for _, g in STACK for i in g))


def arth():
    W, H = 1000, 250
    p = [f'<rect width="{W}" height="{H}" rx="28" fill="{PAPER}"/>',
         f'<text x="56" y="62" class="mono" font-size="14" letter-spacing="2.5" fill="{MUTE}">FEATURED PROJECT</text>',
         f'<text x="56" y="146" font-size="84" fill="{INK}" class="rise"{d(0)}><tspan class="serif">ARTH </tspan>'
         f'<tspan class="serifi" fill="{BLUE}">assistant</tspan></text>',
         f'<text x="56" y="182" class="mono" font-size="14" fill="{MUTE}">Automated Response to Human Intent</text>']
    desc = "A personal AI assistant that runs on my own computer. It remembers me, understands how I feel, opens apps and does quick tasks."
    lines = wrap("sans", desc, 18, 420)
    for i, ln in enumerate(lines):
        p.append(f'<text x="520" y="{104 + i * 28}" class="sans" font-size="18" fill="{INK}">{esc(ln)}</text>')
    p.append(f'<circle cx="528" cy="{104 + len(lines) * 28 + 22}" r="6" fill="{BLUE}"/>'
             f'<text x="544" y="{104 + len(lines) * 28 + 27}" class="mono" font-size="14" fill="{MUTE}">Python</text>')
    p.append(f'<text x="{W - 90}" y="62" text-anchor="end" class="mono" font-size="14" letter-spacing="2.5" fill="{INK}">VIEW REPO</text>')
    p.append(arrow(W - 74, 56, INK))
    return svg(W, H, "".join(p), ["serif", "serifi", "mono", "sans"], title="Featured project: ARTH assistant. " + desc)


def now_card():
    W, H = 490, 330
    p = [f'<rect width="{W}" height="{H}" rx="28" fill="{PAPER}"/>',
         f'<text x="36" y="56" class="mono" font-size="14" letter-spacing="2.5" fill="{MUTE}">CURRENTLY</text>',
         f'<text x="36" y="118" font-size="56" fill="{INK}"><tspan class="serif">Right </tspan><tspan class="serifi" fill="{BLUE}">now</tspan></text>']
    y = 168
    for i, item in enumerate(NOW):
        lines = wrap("sans", item, 17, W - 36 - 36 - 28)
        dot = "" if STATIC else ' class="pulse"'
        p.append(f'<circle{dot} cx="42" cy="{y - 6}" r="5" fill="{BLUE}"/>')
        for ln in lines:
            p.append(f'<text x="62" y="{y}" class="sans rise"{d(.4 + i * .2)} font-size="17" fill="{INK}">{esc(ln)}</text>')
            y += 24
        y += 20
    return svg(W, H, "".join(p), ["serif", "serifi", "mono", "sans"], title="Right now: " + "; ".join(NOW))


def hackathons():
    W, H = 490, 330
    items = json.loads((ROOT / "data" / "hackathons.json").read_text())
    p = [f'<rect width="{W}" height="{H}" rx="28" fill="{PAPER}"/>',
         f'<text x="36" y="56" class="mono" font-size="14" letter-spacing="2.5" fill="{MUTE}">HACKATHONS</text>',
         f'<text x="36" y="118" font-size="56" fill="{INK}"><tspan class="serif">Built at </tspan><tspan class="serifi" fill="{BLUE}">hackathons</tspan></text>']
    y = 166
    for i, it in enumerate(items[:5]):
        label = it["name"] + (f"  ·  {it['date']}" if it.get("date") else "")
        p.append(f'<g class="rise"{d(.4 + i * .15)}><line x1="36" x2="{W - 36}" y1="{y - 22}" y2="{y - 22}" stroke="{LINE}"/>'
                 f'<text x="36" y="{y}" class="sans" font-size="17" fill="{INK}">{esc(label)}</text></g>')
        y += 38
    p.append(f'<text x="36" y="{y}" class="serifi rise"{d(.4 + len(items[:5]) * .15)} font-size="22" fill="{MUTE}">and many more.</text>')
    return svg(W, H, "".join(p), ["serif", "serifi", "mono", "sans"], title="Hackathons: " + ", ".join(i["name"] for i in items) + " and many more")


def contact(kind):
    W, H = 490, 150
    if kind == "linkedin":
        bg, fg, label, big, small = BLUE, "#fff", "LINKEDIN", f"{FIRST} {LAST}", "Let's connect"
    else:
        bg, fg, label, big, small = INK, PAPER, "EMAIL", EMAIL, "Say hello"
    p = [f'<rect width="{W}" height="{H}" rx="26" fill="{bg}"/>',
         f'<text x="32" y="46" class="mono" font-size="13" letter-spacing="2.5" fill="{fg}">{label}</text>',
         arrow(W - 50, 40, fg)]
    if kind == "linkedin":
        p.append(f'<text x="32" y="104" class="serif" font-size="52" fill="{fg}">{big}</text>')
    else:
        p.append(f'<text x="32" y="98" class="sansm" font-size="{22 if tw("sansm", big, 22) < W - 64 else 19}" fill="{fg}">{big}</text>')
    p.append(f'<text x="32" y="130" class="serifi" font-size="22" fill="{fg}" fill-opacity=".75">{small}</text>')
    return svg(W, H, "".join(p), ["serif", "serifi", "mono", "sansm"], title=f"{label.title()}: {big}")


def main():
    days, repos = load_data()
    OUT.mkdir(parents=True, exist_ok=True)
    cards = {
        "hero": hero(),
        "build": tile(BLUE, "#ffffff", "BUILD", str(repos), "public repos",
                      "Software and AI projects, built in the open.", 0.1, count=repos),
        "hackathons": tile(RED, "#ffffff", "HACKATHONS", "Many", "hackathons",
                           "Teams, deadlines and ideas turned into working demos.", 0.25),
        "learn": tile(YELLOW, INK, "LEARN", "AI & ML", "learning",
                      "LLMs, AI agents and open source, on the way to GSoC.", 0.4),
        "activity": activity(days),
        "graph": graph(days),
        "stack": stack(),
        "arth": arth(),
        "now": now_card(),
        "hackathon-list": hackathons(),
        "contact-linkedin": contact("linkedin"),
        "contact-email": contact("email"),
    }
    for name, s in cards.items():
        (OUT / f"{name}.svg").write_text(s)
        print(f"{name}.svg  {len(s) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
