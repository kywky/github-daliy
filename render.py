import html
import re


LANG_COLORS = {
    "Python": "#3572A5", "C": "#555555", "C++": "#f34b7d", "C#": "#178600",
    "Java": "#b07219", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Go": "#00ADD8", "Rust": "#dea584", "Kotlin": "#A97BFF", "Swift": "#F05138",
    "Ruby": "#701516", "PHP": "#4F5D95", "Zig": "#ec915c", "Lua": "#000080",
}

CSS = """
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

/* hero */
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
.pill {
  font-size: 12px; padding: 6px 12px; border-radius: 999px;
  background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.14);
  color: #e0e7ff; backdrop-filter: blur(6px);
}

/* tabs */
.tabbar-wrap { position: relative; margin-top: -34px; z-index: 2; }
.tabbar {
  display: flex; gap: 6px; padding: 6px; background: #fff; border-radius: 14px;
  border: 1px solid var(--line); overflow-x: auto; scrollbar-width: none;
  box-shadow: 0 10px 30px -18px rgba(15,23,42,.35);
}
.tabbar::-webkit-scrollbar { display: none; }
.tab {
  flex: 0 0 auto; border: 0; background: transparent; color: #475569;
  font: inherit; font-size: 13.5px; font-weight: 600; padding: 9px 16px;
  border-radius: 10px; cursor: pointer; display: inline-flex; align-items: center; gap: 7px;
  transition: background .15s ease, color .15s ease;
}
.tab:hover { background: #f1f5f9; color: var(--ink); }
.tab.active { background: #0f172a; color: #fff; }
.tab .count {
  font-size: 11px; padding: 1px 7px; border-radius: 999px;
  background: rgba(148,163,184,.22); color: inherit;
}
.tab.active .count { background: rgba(255,255,255,.18); }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }

/* cards */
main { padding: 30px 0 10px; }
.grid { display: grid; gap: 18px; grid-template-columns: 1fr; }
@media (min-width: 820px) { .grid { grid-template-columns: 1fr 1fr; } }
.card {
  background: #fff; border: 1px solid var(--line); border-radius: 16px;
  padding: 20px 20px 16px; display: flex; flex-direction: column;
  box-shadow: 0 1px 2px rgba(15,23,42,.03), 0 12px 28px -22px rgba(15,23,42,.22);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.card:hover {
  transform: translateY(-3px); border-color: #d8dbf0;
  box-shadow: 0 2px 4px rgba(15,23,42,.04), 0 22px 40px -24px rgba(49,46,129,.35);
}
.card-head { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.rank {
  flex: 0 0 auto; width: 30px; height: 30px; border-radius: 9px;
  display: grid; place-items: center; font-size: 13px; font-weight: 800;
  background: #f1f5f9; color: #64748b;
}
.rank.r1 { background: linear-gradient(140deg, #fbbf24, #f59e0b); color: #fff; }
.rank.r2 { background: linear-gradient(140deg, #cbd5e1, #94a3b8); color: #fff; }
.rank.r3 { background: linear-gradient(140deg, #fdba74, #ea580c); color: #fff; }
.cats { display: flex; flex-wrap: wrap; gap: 5px; flex: 1; min-width: 0; }
.cat {
  font-size: 10.5px; font-weight: 700; letter-spacing: .02em;
  padding: 3px 9px; border-radius: 999px; color: #fff; white-space: nowrap;
}
.speed {
  font-size: 12px; font-weight: 700; padding: 3px 9px; border-radius: 999px;
  background: #ecfdf5; color: #047857; white-space: nowrap;
}
.speed.neutral { background: #f1f5f9; color: #64748b; }
.title { font-size: 18px; font-weight: 700; line-height: 1.35; margin-bottom: 6px; word-break: break-word; }
.title a { color: var(--ink); text-decoration: none; }
.title a:hover { color: var(--accent); }
.title .owner { color: #94a3b8; font-weight: 500; }
.desc { font-size: 13px; line-height: 1.6; color: var(--muted); margin-bottom: 12px; }

.summary {
  background: #f8fafc; border: 1px solid #eef2f7; border-left: 3px solid var(--accent);
  border-radius: 10px; padding: 12px 14px; font-size: 13px; line-height: 1.75;
  color: #334155; flex: 1;
}
.summary ul { list-style: none; padding: 0; margin: 0; display: grid; gap: 6px; }
.summary li { position: relative; padding-left: 18px; }
.summary li::before {
  content: ''; position: absolute; left: 3px; top: .62em; width: 5px; height: 5px;
  border-radius: 50%; background: #c7d2fe;
}
.summary strong { color: var(--ink); font-weight: 700; }
.summary p { margin: 0; }

.card-foot {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  margin-top: 14px; padding-top: 12px; border-top: 1px solid #f1f5f9;
  font-size: 12px; color: var(--muted);
}
.lang { display: inline-flex; align-items: center; gap: 6px; min-width: 0; }
.lang-dot { width: 9px; height: 9px; border-radius: 50%; flex: 0 0 auto; }
.gh-link {
  color: var(--accent); text-decoration: none; font-weight: 700; font-size: 12.5px;
  padding: 5px 10px; border-radius: 8px; background: #eef2ff; white-space: nowrap;
  transition: background .15s ease;
}
.gh-link:hover { background: #e0e7ff; }

.topics { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px; }
.topic {
  font-size: 10.5px; color: #64748b; background: #f8fafc; border: 1px solid #eef2f7;
  padding: 2px 7px; border-radius: 6px;
}

.empty { text-align: center; padding: 70px 20px; color: var(--muted); font-size: 14px; }
footer { padding: 34px 20px 40px; text-align: center; color: #94a3b8; font-size: 12px; }
footer .sep { margin: 0 8px; }
"""

TAB_JS = """
document.querySelectorAll('.tab').forEach(function (tab) {
  tab.addEventListener('click', function () {
    document.querySelectorAll('.tab').forEach(function (t) { t.classList.remove('active'); });
    tab.classList.add('active');
    var cat = tab.getAttribute('data-cat');
    document.querySelectorAll('.card').forEach(function (card) {
      var cats = (card.getAttribute('data-cats') || '').split(',');
      card.style.display = (cat === 'all' || cats.indexOf(cat) !== -1) ? '' : 'none';
    });
  });
});
"""


def _md_to_html(text: str) -> str:
    esc = html.escape(text).strip()

    def li(m):
        lines = [ln.lstrip('- ').strip() for ln in m.group(0).strip().split("\n") if ln.strip()]
        return "<ul>" + "".join(f"<li>{x}</li>" for x in lines) + "</ul>"

    if re.search(r"(?:^- .+(?:\n|$))+", esc, flags=re.M):
        esc = re.sub(r"(?:^- .+(?:\n|$))+", li, esc, flags=re.M)
    else:
        esc = f"<p>{esc}</p>"
    esc = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc)
    return esc


def _cat_color(name: str) -> str:
    from github import CATEGORIES
    cfg = CATEGORIES.get(name)
    return cfg["color"] if cfg else "#64748b"


def render(repos: list[dict], window_start: str, window_end: str, comparison: str | None) -> str:
    cat_counts: dict[str, int] = {}
    for r in repos:
        for c in r.get("categories", []):
            cat_counts[c] = cat_counts.get(c, 0) + 1

    from github import CATEGORIES
    tab_categories = list(CATEGORIES.keys())

    tabs = [f'<button class="tab active" data-cat="all">全部 <span class="count">{len(repos)}</span></button>']
    for cat in tab_categories:
        n = cat_counts.get(cat, 0)
        if n == 0:
            continue
        color = _cat_color(cat)
        tabs.append(
            f'<button class="tab" data-cat="{html.escape(cat)}">'
            f'<span class="dot" style="background:{color}"></span>{html.escape(cat)} '
            f'<span class="count">{n}</span></button>'
        )

    cards = []
    for idx, r in enumerate(repos, 1):
        cats = r.get("categories") or []
        cat_html = "".join(
            f'<span class="cat" style="background:{_cat_color(k)}">{html.escape(k)}</span>'
            for k in cats
        )

        spd = r.get("stars_per_day")
        if spd is None:
            speed_html = '<span class="speed neutral">新收录</span>'
        elif spd > 0:
            speed_html = f'<span class="speed">↑ {spd:g}★/天</span>'
        else:
            speed_html = f'<span class="speed neutral">{spd:g}★/天</span>'

        rank_cls = f" r{idx}" if idx <= 3 else ""
        owner, _, repo_name = r["full_name"].partition("/")
        lang = r["language"] or "未知"
        lang_color = LANG_COLORS.get(lang, "#94a3b8")
        topics = "".join(f'<span class="topic">#{html.escape(t)}</span>' for t in r["topics"][:6])
        desc_html = f'<div class="desc">{html.escape(r["description"])}</div>' if r.get("description") else ""
        data_cats = ",".join(cats)

        cards.append(f"""
<article class="card" data-cats="{html.escape(data_cats)}">
  <div class="card-head">
    <span class="rank{rank_cls}">{idx}</span>
    <div class="cats">{cat_html}</div>
    {speed_html}
  </div>
  <h3 class="title"><a href="{html.escape(r['url'])}" target="_blank" rel="noreferrer"><span class="owner">{html.escape(owner)}/</span>{html.escape(repo_name)}</a></h3>
  {desc_html}
  <div class="summary">{_md_to_html(r.get('summary', ''))}</div>
  {f'<div class="topics">{topics}</div>' if topics else ''}
  <div class="card-foot">
    <span class="lang"><span class="lang-dot" style="background:{lang_color}"></span>{html.escape(lang)} · 成立于 {html.escape(r['created_at'])}</span>
    <a class="gh-link" href="{html.escape(r['url'])}" target="_blank" rel="noreferrer">GitHub ↗</a>
  </div>
</article>""")

    grid = f'<div class="grid">{"".join(cards)}</div>' if cards else '<div class="empty">今天没有符合条件的新项目，明天再来看看。</div>'
    speed_note = f"对比 {comparison} 快照计算日增" if comparison else "首次运行，今日按总 star 排序"

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GitHub 每日精选 · {window_end}</title>
<style>{CSS}</style>
</head>
<body>
<header class="hero">
  <div class="wrap">
    <div class="eyebrow">Daily Digest</div>
    <h1>GitHub <span class="grad">每日精选</span></h1>
    <p class="lead">从近 7 天新崛起的一批项目里，按 C/C++、AI、Python、GPU、自动化五个方向各挑 2 个，再看它们昨天的涨星表现。</p>
    <div class="meta">
      <span class="pill">{window_start} → {window_end}</span>
      <span class="pill">{len(repos)} 个项目</span>
      <span class="pill">{speed_note}</span>
    </div>
  </div>
</header>

<div class="wrap tabbar-wrap">
  <div class="tabbar">{''.join(tabs)}</div>
</div>

<main class="wrap">
{grid}
</main>

<footer>
  github-daily · 每天自动整理<span class="sep">·</span>数据来源 GitHub API<span class="sep">·</span>摘要由 GLM-4-Flash 生成
</footer>

<script>{TAB_JS}</script>
</body>
</html>
"""
