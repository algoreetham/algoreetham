#!/usr/bin/env python3
"""Builds an interactive, responsive standalone web portfolio (index.html)
with scroll-triggered animations (IntersectionObserver).
Deploys directly to GitHub Pages.
"""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "cards"
FONTS = ROOT / "fonts"
OUT_HTML = ROOT / "index.html"

# Load font files once as base64
FONT_DEFS = {
    "Instrument Serif": ("serif-400.woff", "normal", 400),
    "Instrument Serif": ("serif-400-italic.woff", "italic", 400),
    "JetBrains Mono": ("mono-400.woff", "normal", 400),
    "Inter": ("sans-400.woff", "normal", 400),
    "Inter": ("sans-500.woff", "normal", 500),
}


def get_font_faces():
    css = []
    # JetBrains Mono
    if (FONTS / "mono-400.woff").exists():
        b = base64.b64encode((FONTS / "mono-400.woff").read_bytes()).decode()
        css.append(f"@font-face {{ font-family: 'JetBrains Mono'; font-style: normal; font-weight: 400; src: url(data:font/woff;base64,{b}) format('woff'); }}")
    # Instrument Serif regular
    if (FONTS / "serif-400.woff").exists():
        b = base64.b64encode((FONTS / "serif-400.woff").read_bytes()).decode()
        css.append(f"@font-face {{ font-family: 'Instrument Serif'; font-style: normal; font-weight: 400; src: url(data:font/woff;base64,{b}) format('woff'); }}")
    # Instrument Serif italic
    if (FONTS / "serif-400-italic.woff").exists():
        b = base64.b64encode((FONTS / "serif-400-italic.woff").read_bytes()).decode()
        css.append(f"@font-face {{ font-family: 'Instrument Serif'; font-style: italic; font-weight: 400; src: url(data:font/woff;base64,{b}) format('woff'); }}")
    # Inter regular
    if (FONTS / "sans-400.woff").exists():
        b = base64.b64encode((FONTS / "sans-400.woff").read_bytes()).decode()
        css.append(f"@font-face {{ font-family: 'Inter'; font-style: normal; font-weight: 400; src: url(data:font/woff;base64,{b}) format('woff'); }}")
    # Inter medium
    if (FONTS / "sans-500.woff").exists():
        b = base64.b64encode((FONTS / "sans-500.woff").read_bytes()).decode()
        css.append(f"@font-face {{ font-family: 'Inter'; font-style: normal; font-weight: 500; src: url(data:font/woff;base64,{b}) format('woff'); }}")
    return "\n".join(css)


def clean_card_svg(card_name):
    svg_path = CARDS / f"{card_name}.svg"
    if not svg_path.exists():
        return ""
    text = svg_path.read_text(encoding="utf-8")
    
    # Strip @font-face declarations inside SVG to avoid duplicate megabytes
    text = re.sub(r"@font-face\{[^}]+\}", "", text)
    
    # Update animation selectors so they trigger when parent has .in-view
    # Replace .rise, .fade, etc. with .in-view .rise, .in-view .fade
    # Initial state should be invisible/untransformed until .in-view
    replacements = [
        (r"\.rise\{([^}]+)\}", r".card .rise { opacity: 0; transform: translateY(16px); } .card.in-view .rise {\1}"),
        (r"\.fade\{([^}]+)\}", r".card .fade { opacity: 0; } .card.in-view .fade {\1}"),
        (r"\.ty\{([^}]+)\}", r".card .ty { fill-opacity: 0; } .card.in-view .ty {\1}"),
        (r"\.grow\{([^}]+)\}", r".card .grow { transform-box: fill-box; transform-origin: 50% 100%; transform: scaleY(0); } .card.in-view .grow {\1}"),
        (r"\.pop\{([^}]+)\}", r".card .pop { transform-box: fill-box; transform-origin: 50% 50%; opacity: 0; transform: scale(.2); } .card.in-view .pop {\1}"),
        (r"\.swing\{([^}]+)\}", r".card .swing { transform-box: fill-box; transform-origin: 0 100%; opacity: 0; } .card.in-view .swing {\1}"),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
        
    # Ensure svg is responsive: remove fixed width/height attributes or set style width: 100%, height: auto
    text = re.sub(r'<svg([^>]*)width="[0-9.]+"([^>]*)height="[0-9.]+"', r'<svg\1\2 style="width:100%;height:auto;display:block;"', text)
    return text


def build_html():
    font_css = get_font_faces()
    
    hero_svg = clean_card_svg("hero")
    graph_svg = clean_card_svg("graph")
    activity_svg = clean_card_svg("activity")
    build_svg = clean_card_svg("build")
    hackathons_svg = clean_card_svg("hackathons")
    learn_svg = clean_card_svg("learn")
    stack_svg = clean_card_svg("stack")
    arth_svg = clean_card_svg("arth")
    now_svg = clean_card_svg("now")
    hackathon_list_svg = clean_card_svg("hackathon-list")
    linkedin_svg = clean_card_svg("contact-linkedin")
    email_svg = clean_card_svg("contact-email")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Preetham Singh | Portfolio</title>
  <meta name="description" content="Preetham Singh - Joint Secretary · Azure Developer Club | B.Tech CSE (AI) · Alliance University">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚀</text></svg>">
  <style>
    {font_css}

    :root {{
      --bg: #0d1117;
      --card-bg: #f3f3f1;
      --ink: #111111;
      --blue: #3a56f5;
      --border: rgba(255, 255, 255, 0.1);
    }}

    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{
      background-color: var(--bg);
      color: #e6edf3;
      font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 24px 16px 80px 16px;
    }}

    /* Top Navigation */
    .nav-bar {{
      width: 100%;
      max-width: 1000px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 20px;
      margin-bottom: 24px;
      border-radius: 16px;
      background: rgba(22, 27, 34, 0.7);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border);
      position: sticky;
      top: 16px;
      z-index: 100;
    }}

    .nav-brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 14px;
      font-weight: 500;
      letter-spacing: 1px;
      color: #f0f6fc;
      text-decoration: none;
    }}

    .nav-status {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: #3fb950;
    }}

    .status-dot {{
      width: 8px;
      height: 8px;
      background: #3fb950;
      border-radius: 50%;
      box-shadow: 0 0 8px #3fb950;
      animation: pulse 2s infinite ease-in-out;
    }}

    @keyframes pulse {{
      0%, 100% {{ transform: scale(1); opacity: 1; }}
      50% {{ transform: scale(1.3); opacity: 0.5; }}
    }}

    .nav-links {{
      display: flex;
      gap: 12px;
    }}

    .nav-btn {{
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-family: 'JetBrains Mono', monospace;
      text-decoration: none;
      color: #c9d1d9;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border);
      transition: all 0.2s ease;
    }}

    .nav-btn:hover {{
      background: var(--blue);
      color: #ffffff;
      border-color: var(--blue);
      transform: translateY(-1px);
    }}

    /* Portfolio Layout */
    .portfolio-container {{
      width: 100%;
      max-width: 1000px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}

    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
    }}

    .grid-2 {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
    }}

    @media (max-width: 768px) {{
      .grid-3, .grid-2 {{
        grid-template-columns: 1fr;
      }}
    }}

    /* Card Wrapper & Scroll Animation */
    .card {{
      border-radius: 28px;
      overflow: hidden;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
      opacity: 0;
      transform: translateY(45px);
      transition: opacity 0.85s cubic-bezier(0.16, 1, 0.3, 1), transform 0.85s cubic-bezier(0.16, 1, 0.3, 1);
      will-change: opacity, transform;
    }}

    .card.in-view {{
      opacity: 1;
      transform: translateY(0);
    }}

    /* Hover effect on interactive cards */
    a.card-link {{
      display: block;
      text-decoration: none;
      border-radius: 28px;
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease;
    }}

    a.card-link:hover {{
      transform: translateY(-4px) scale(1.01);
      box-shadow: 0 18px 40px rgba(58, 86, 245, 0.25);
    }}

    /* Footer */
    footer {{
      margin-top: 60px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      color: #8b949e;
      text-align: center;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    footer a {{
      color: var(--blue);
      text-decoration: none;
    }}

    footer a:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>

  <!-- Sticky Header -->
  <header class="nav-bar">
    <a href="#" class="nav-brand">
      <span>preetham.singh</span>
      <span class="nav-status"><span class="status-dot"></span> open to work</span>
    </a>
    <div class="nav-links">
      <a href="https://github.com/algoreetham" target="_blank" rel="noopener" class="nav-btn">GitHub</a>
      <a href="https://www.linkedin.com/in/preetham-singh-1b8676382/" target="_blank" rel="noopener" class="nav-btn">LinkedIn</a>
    </div>
  </header>

  <!-- Main Content -->
  <main class="portfolio-container">

    <!-- Row 1: Hero Card -->
    <div class="card" id="card-hero">
      {hero_svg}
    </div>

    <!-- Row 2: Contribution Graph Card -->
    <div class="card" id="card-graph">
      {graph_svg}
    </div>

    <!-- Row 3: 12-Month Activity Card -->
    <div class="card" id="card-activity">
      {activity_svg}
    </div>

    <!-- Row 4: 3-column Tiles -->
    <div class="grid-3">
      <a href="https://github.com/algoreetham?tab=repositories" target="_blank" rel="noopener" class="card-link">
        <div class="card" id="card-build">
          {build_svg}
        </div>
      </a>
      <a href="https://www.linkedin.com/in/preetham-singh-1b8676382/" target="_blank" rel="noopener" class="card-link">
        <div class="card" id="card-hackathons">
          {hackathons_svg}
        </div>
      </a>
      <a href="https://github.com/algoreetham?tab=stars" target="_blank" rel="noopener" class="card-link">
        <div class="card" id="card-learn">
          {learn_svg}
        </div>
      </a>
    </div>

    <!-- Row 5: Tech Stack Card -->
    <div class="card" id="card-stack">
      {stack_svg}
    </div>

    <!-- Row 6: Featured Project: ARTH -->
    <a href="https://github.com/algoreetham/ARTH-Automated-Response-To-Human-Intent" target="_blank" rel="noopener" class="card-link">
      <div class="card" id="card-arth">
        {arth_svg}
      </div>
    </a>

    <!-- Row 7: 2-column Now & Hackathons list -->
    <div class="grid-2">
      <div class="card" id="card-now">
        {now_svg}
      </div>
      <div class="card" id="card-hackathon-list">
        {hackathon_list_svg}
      </div>
    </div>

    <!-- Row 8: 2-column Contact Cards -->
    <div class="grid-2">
      <a href="https://www.linkedin.com/in/preetham-singh-1b8676382/" target="_blank" rel="noopener" class="card-link">
        <div class="card" id="card-linkedin">
          {linkedin_svg}
        </div>
      </a>
      <a href="mailto:preetham.singh.sp@gmail.com" class="card-link">
        <div class="card" id="card-email">
          {email_svg}
        </div>
      </a>
    </div>

  </main>

  <!-- Footer -->
  <footer>
    <p>Crafted with SVG, CSS & JavaScript · Hosted on GitHub Pages</p>
    <p>© 2026 Preetham Singh · <a href="https://github.com/algoreetham">@algoreetham</a></p>
  </footer>

  <!-- Scroll-Triggered Animation Controller -->
  <script>
    document.addEventListener("DOMContentLoaded", () => {{
      const cards = document.querySelectorAll(".card");

      // Intersection Observer with precise scroll threshold
      const observer = new IntersectionObserver((entries) => {{
        entries.forEach((entry) => {{
          if (entry.isIntersecting) {{
            // Add in-view class to trigger the card entrance and internal SVG animations
            entry.target.classList.add("in-view");
          }}
        }});
      }}, {{
        threshold: 0.15,
        rootMargin: "0px 0px -40px 0px"
      }});

      cards.forEach((card) => observer.observe(card));
    }});
  </script>
</body>
</html>
"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Generated {OUT_HTML} ({len(html) / 1024:.1f} KB)")


if __name__ == "__main__":
    build_html()
