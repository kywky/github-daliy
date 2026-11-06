"""Shared CSS styles for github-daily HTML pages."""

RESET = """
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --ink: #0b1220;
  --muted: #64748b;
  --line: #e6e8ee;
  --accent: #4f46e5;
  --bg: #f5f6fa;
}
html { scroll-behavior: smooth; }
body {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
               "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: var(--bg);
  color: var(--ink);
  -webkit-font-smoothing: antialiased;
  min-height: 100vh;
}
.wrap { max-width: 1080px; margin: 0 auto; padding: 0 20px; }
"""

HERO = """
.hero {
  background:
    radial-gradient(1200px 400px at 15% -20%, rgba(139,92,246,.55), transparent 60%),
    radial-gradient(900px 300px at 110% 10%, rgba(236,72,153,.45), transparent 55%),
    linear-gradient(135deg, #0f172a 0%, #1e1b4b 60%, #312e81 100%);
  color: #fff;
  padding: 52px 0 76px;
}
.hero .eyebrow {
  font-size: 12px; letter-spacing: .16em; text-transform: uppercase;
  color: #a5b4fc; font-weight: 600; margin-bottom: 14px;
}
.hero h1 { font-size: 40px; font-weight: 800; letter-spacing: -1px; line-height: 1.1; }
.hero h1 .grad {
  background: linear-gradient(90deg, #c4b5fd, #f0abfc, #fda4af);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero .lead { color: #c7d2fe; font-size: 15px; margin-top: 14px; max-width: 620px; line-height: 1.7; }
.hero .meta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 22px; }
.hero p { color: #c7d2fe; font-size: 14px; line-height: 1.7; margin-top: 12px; max-width: 560px; }
.pill {
  font-size: 12px; padding: 6px 12px; border-radius: 999px;
  background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.14);
  color: #e0e7ff; backdrop-filter: blur(6px);
  text-decoration: none;
}
a.pill:hover { background: rgba(255,255,255,.14); border-color: rgba(255,255,255,.28); }
"""

FOOTER = """
footer { padding: 34px 20px 40px; text-align: center; color: #94a3b8; font-size: 12px; }
footer .sep { margin: 0 8px; }
"""

EMPTY = """
.empty { text-align: center; padding: 70px 20px; color: var(--muted); font-size: 14px; }
"""


def base_css() -> str:
    return RESET + HERO + FOOTER + EMPTY
