import html
import json
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path


WEEKDAYS = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")
PLATFORMS = ("安卓", "鸿蒙", "Linux", "Windows")
FILTERS = ("安卓", "鸿蒙", "Linux", "Windows", "AI", "C", "C++", "Python")
BANNER_MARK = "<!-- archive-banner -->"

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
:root { --ink:#0b1220; --muted:#64748b; --line:#e6e8ee; --accent:#4f46e5; --bg:#f5f6fa; }
body {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
               "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: var(--bg); color: var(--ink);
  -webkit-font-smoothing: antialiased; min-height: 100vh;
}
.wrap { max-width: 880px; margin: 0 auto; padding: 0 20px; }
.hero {
  background:
    radial-gradient(900px 320px at 10% -20%, rgba(139,92,246,.55), transparent 60%),
    radial-gradient(700px 260px at 110% 10%, rgba(236,72,153,.42), transparent 55%),
    linear-gradient(135deg, #0f172a 0%, #1e1b4b 60%, #312e81 100%);
  color: #fff; padding: 46px 0 56px;
}
.eyebrow { font-size: 12px; letter-spacing: .16em; text-transform: uppercase; color: #a5b4fc; font-weight: 600; margin-bottom: 12px; }
.hero h1 { font-size: 36px; font-weight: 800; letter-spacing: -1px; }
.hero h1 .grad {
  background: linear-gradient(90deg, #c4b5fd, #f0abfc, #fda4af);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero p { color: #c7d2fe; font-size: 14px; line-height: 1.7; margin-top: 12px; max-width: 560px; }
.hero .meta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 20px; }
.pill {
  font-size: 12px; padding: 6px 12px; border-radius: 999px; text-decoration: none;
  background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.14); color: #e0e7ff;
}
a.pill:hover { background: rgba(255,255,255,.14); }
main { padding: 30px 0 20px; }
.list { display: grid; gap: 12px; }
.day {
  display: flex; align-items: center; gap: 16px; text-decoration: none; color: inherit;
  background: #fff; border: 1px solid var(--line); border-radius: 14px;
  padding: 16px 18px; transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease;
  box-shadow: 0 1px 2px rgba(15,23,42,.03), 0 12px 28px -24px rgba(15,23,42,.25);
}
.day:hover { transform: translateY(-2px); border-color: #d8dbf0; box-shadow: 0 16px 32px -24px rgba(49,46,129,.4); }
.day-main { flex: 1; min-width: 0; }
.date { font-size: 17px; font-weight: 800; display: flex; align-items: baseline; gap: 8px; }
.date .week { font-size: 12px; font-weight: 600; color: var(--muted); }
.preview {
  font-size: 12.5px; color: var(--muted); margin-top: 5px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.chips { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 9px; }
.chip { font-size: 10.5px; padding: 2px 8px; border-radius: 999px; background: #f1f5f9; color: #475569; }
.chip.strong { background: #eef2ff; color: #4338ca; font-weight: 700; }
.chip.plat { background: #f8fafc; border: 1px solid #eef2f7; color: #64748b; }
.go { flex: 0 0 auto; font-size: 13px; font-weight: 700; color: var(--accent); white-space: nowrap; }
.empty { text-align: center; padding: 70px 20px; color: var(--muted); font-size: 14px; }
footer { padding: 26px 20px 40px; text-align: center; color: #94a3b8; font-size: 12px; }
"""

PROJECT_CSS = CSS + """
.wrap.wide { max-width: 1080px; }
.ptools { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 12px; }
.psearch {
  flex: 1 1 240px; min-width: 200px; font: inherit; font-size: 13.5px;
  padding: 10px 14px; border: 1px solid var(--line); border-radius: 10px;
  background: #fff; color: var(--ink); outline: none;
}
.psearch:focus { border-color: #c7d2fe; box-shadow: 0 0 0 3px rgba(79,70,229,.08); }
.psort {
  font: inherit; font-size: 13px; padding: 9px 12px; border-radius: 10px;
  border: 1px solid var(--line); background: #fff; color: #334155; cursor: pointer;
}
.filters { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
.fbtn {
  font: inherit; font-size: 12px; padding: 6px 12px; border-radius: 999px;
  border: 1px solid var(--line); background: #fff; color: #475569; cursor: pointer;
}
.fbtn:hover { border-color: #cbd5e1; }
.fbtn.active { background: #eef2ff; color: #4338ca; border-color: #c7d2fe; font-weight: 700; }
.presult { font-size: 12.5px; color: var(--muted); margin: 0 0 18px; }
.presult strong { color: #4338ca; }
.pgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 14px; }
.pcard {
  background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px;
  box-shadow: 0 1px 2px rgba(15,23,42,.03), 0 12px 28px -26px rgba(15,23,42,.25);
  display: flex; flex-direction: column; gap: 8px;
}
.phead { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; }
.pdate { font-size: 11.5px; color: var(--muted); text-decoration: none; font-variant-numeric: tabular-nums; }
.pdate:hover { color: var(--accent); }
.pick { font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 999px; }
.pick.top { background: #fff7ed; color: #b45309; }
.pick.growth { background: #ecfdf5; color: #047857; }
.pick.ai { background: #f5f3ff; color: #6d28d9; }
.pick.learn { background: #eff6ff; color: #1d4ed8; }
.pick.daily { background: #f1f5f9; color: #475569; }
.times { font-size: 10.5px; color: #94a3b8; margin-left: auto; }
.ptitle { font-size: 16px; line-height: 1.35; letter-spacing: -.2px; word-break: break-all; }
.ptitle a { color: inherit; text-decoration: none; }
.ptitle a:hover { color: var(--accent); }
.ptitle .owner { color: var(--muted); font-weight: 500; font-size: 13.5px; }
.pdesc, .psummary {
  font-size: 12.8px; line-height: 1.65; color: #475569;
  display: -webkit-box; -webkit-box-orient: vertical; overflow: hidden;
}
.pdesc { -webkit-line-clamp: 3; color: var(--muted); }
.psummary { -webkit-line-clamp: 6; white-space: pre-line; }
.pcats { display: flex; flex-wrap: wrap; gap: 5px; }
.pcat { font-size: 10px; padding: 2px 7px; border-radius: 999px; background: #f8fafc; color: #64748b; border: 1px solid #eef2f7; }
.pfoot { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; margin-top: auto; padding-top: 4px; }
.pstars { font-size: 12.5px; font-weight: 700; color: #0f172a; font-variant-numeric: tabular-nums; }
.pmeta { font-size: 11px; color: #94a3b8; }
.pempty { text-align: center; padding: 60px 20px; color: var(--muted); font-size: 14px; }
.pnote { margin-top: 26px; padding-top: 16px; border-top: 1px solid var(--line); font-size: 12px; color: #94a3b8; line-height: 1.8; }
@media (max-width: 560px) {
  .hero h1 { font-size: 30px; }
  .pgrid { grid-template-columns: 1fr; }
  .presult { margin-bottom: 12px; }
}
"""


def _load_day(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text("utf-8"))
    except Exception:
        return None
    return data if isinstance(data.get("repos"), list) else None


def _meta_from_data(data: dict) -> dict:
    repos = data["repos"]
    learn = sum(1 for r in repos if r.get("kind") == "learn")
    ai = sum(1 for r in repos if "AI" in (r.get("categories") or []))
    platforms = [p for p in PLATFORMS if any(p in (r.get("categories") or []) for r in repos)]
    names = [r.get("full_name", "") for r in repos if r.get("full_name")]
    return {
        "total": len(repos),
        "tools": max(len(repos) - learn - ai, 0),
        "ai": ai,
        "learn": learn,
        "platforms": platforms,
        "names": names,
    }


def _meta_from_html(page: str) -> dict:
    total = page.count('<article class="card"')
    learn = page.count("经典可读")
    platforms = [p for p in PLATFORMS if f'data-cat="{html.escape(p)}"' in page]
    return {
        "total": total,
        "tools": max(total - learn, 0),
        "ai": None,
        "learn": learn,
        "platforms": platforms,
        "names": [],
    }


def _patch_page(page: str, day: str) -> str:
    if BANNER_MARK in page:
        if "../projects.html" in page:
            return page
        start = page.index(BANNER_MARK)
        end = page.find("</div>", start)
        if end == -1:
            return page
        banner = page[start:end]
        if "../archive.html" in banner:
            banner = banner.replace(
                '<a href="../archive.html"',
                '<a href="../projects.html" style="color:#c7d2fe;font-weight:600">项目总表</a>'
                '<span style="color:#475569;margin:0 8px">/</span>'
                '<a href="../archive.html"',
                1,
            )
            page = page[:start] + banner + page[end:]
        return page
    page = page.replace('href="archive.html"', 'href="../archive.html"')
    banner = (
        f"{BANNER_MARK}\n"
        '<div style="background:#0f172a;color:#cbd5e1;font-size:13px;text-align:center;'
        'padding:10px 16px;line-height:1.6">'
        f"{html.escape(day)} 存档 · "
        '<a href="../index.html" style="color:#c7d2fe;font-weight:600">回到今天</a>'
        '<span style="color:#475569;margin:0 8px">/</span>'
        '<a href="../projects.html" style="color:#c7d2fe;font-weight:600">项目总表</a>'
        '<span style="color:#475569;margin:0 8px">/</span>'
        '<a href="../archive.html" style="color:#c7d2fe;font-weight:600">全部存档</a>'
        "</div>"
    )
    if "<body>" in page:
        page = page.replace("<body>", "<body>\n" + banner, 1)
    return page


def _entry_html(day: str, meta: dict) -> str:
    weekday = WEEKDAYS[date.fromisoformat(day).weekday()]
    chips = [f'<span class="chip strong">{meta["total"]} 个项目</span>']
    if meta.get("tools"):
        chips.append(f'<span class="chip">工具 {meta["tools"]}</span>')
    if meta.get("ai"):
        chips.append(f'<span class="chip">AI {meta["ai"]}</span>')
    if meta.get("learn"):
        chips.append(f'<span class="chip">经典 {meta["learn"]}</span>')
    for p in meta.get("platforms", []):
        chips.append(f'<span class="chip plat">{html.escape(p)}</span>')

    names = meta.get("names") or []
    preview = " · ".join(html.escape(n) for n in names[:3])
    if len(names) > 3:
        preview += f" 等 {len(names)} 个"

    return f"""
<a class="day" href="day/{html.escape(day)}.html">
  <div class="day-main">
    <div class="date">{html.escape(day)}<span class="week">{weekday}</span></div>
    {f'<div class="preview">{preview}</div>' if preview else ''}
    <div class="chips">{''.join(chips)}</div>
  </div>
  <span class="go">查看 →</span>
</a>"""


def _render_archive(entries: list[tuple[str, dict]]) -> str:
    items = "".join(_entry_html(day, meta) for day, meta in entries)
    body = f'<div class="list">{items}</div>' if entries else '<div class="empty">还没有存档，明天开始每天自动归档。</div>'
    unique = {
        name.lower()
        for _, meta in entries
        for name in (meta.get("names") or [])
        if name
    }
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>历史存档 · GitHub 每日精选</title>
<style>{CSS}</style>
</head>
<body>
<header class="hero">
  <div class="wrap">
    <div class="eyebrow">Archive</div>
    <h1>历史<span class="grad">存档</span></h1>
    <p>每天的推荐都会原样保存在这里，按日期从新到旧排列。</p>
    <div class="meta">
      <span class="pill">已归档 {len(entries)} 天</span>
      {f'<span class="pill">共 {len(unique)} 个项目</span>' if unique else ''}
      <a class="pill" href="projects.html">项目总表 →</a>
      <a class="pill" href="index.html">回到今天 →</a>
    </div>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer>github-daily · 每天自动整理并归档</footer>
</body>
</html>
"""


def _pick_badge(r: dict) -> tuple[str, str]:
    if r.get("kind") == "learn":
        return "经典精读", "learn"
    return {
        "top": ("人气榜", "top"),
        "growth": ("涨星最快", "growth"),
        "ai": ("热门 AI", "ai"),
    }.get(r.get("pick"), ("每日精选", "daily"))


def _project_platforms(r: dict) -> list[str]:
    if r.get("pick") == "ai":
        return ["AI"]
    slot = r.get("slot")
    if r.get("pick") in ("top", "growth") and slot:
        return [slot]
    return r.get("categories") or []


def _fmt_stars(n: int) -> str:
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def _project_card(r: dict) -> str:
    name = r.get("full_name", "")
    owner, _, short = name.partition("/")
    label, cls = _pick_badge(r)
    cats = r.get("categories") or []
    topics = r.get("topics") or []
    summary = (r.get("summary") or "").strip()
    desc = (r.get("description") or "").strip()
    if summary:
        body = f'<div class="psummary">{html.escape(summary)}</div>'
    elif desc:
        body = f'<div class="pdesc">{html.escape(desc)}</div>'
    else:
        body = ""
    cat_html = "".join(f'<span class="pcat">{html.escape(c)}</span>' for c in cats)
    topic_html = "".join(f'<span class="pcat">#{html.escape(t)}</span>' for t in topics[:4])
    dates = r.get("dates") or []
    times = f'<span class="times">推荐 {len(dates)} 次</span>' if len(dates) > 1 else ""
    search = " ".join([name, desc, summary, " ".join(cats), " ".join(topics)]).lower()
    stars = int(r.get("stars") or 0)
    lang = r.get("language") or "未知"
    created = r.get("created_at") or "-"
    last_day = r.get("last_day") or ""

    return f"""
<article class="pcard" data-platforms="{html.escape(','.join(_project_platforms(r)), quote=True)}"
         data-stars="{stars}" data-date="{html.escape(last_day)}"
         data-name="{html.escape(name, quote=True)}" data-search="{html.escape(search, quote=True)}">
  <div class="phead">
    <a class="pdate" href="day/{html.escape(last_day)}.html">{html.escape(last_day)}</a>
    <span class="pick {cls}">{label}</span>
    {times}
  </div>
  <h3 class="ptitle"><a href="{html.escape(r.get('url', ''))}"><span class="owner">{html.escape(owner)}/</span>{html.escape(short)}</a></h3>
  {body}
  {f'<div class="pcats">{cat_html}{topic_html}</div>' if (cat_html or topic_html) else ''}
  <div class="pfoot">
    <span class="pstars">★ {_fmt_stars(stars)}</span>
    <span class="pmeta">{html.escape(lang)} · {html.escape(created)}</span>
  </div>
</article>"""


def _project_record(r: dict) -> dict:
    dates = r.get("dates") or []
    return {
        "full_name": r.get("full_name", ""),
        "url": r.get("url", ""),
        "description": r.get("description", ""),
        "summary": r.get("summary", ""),
        "stars": int(r.get("stars") or 0),
        "language": r.get("language", ""),
        "topics": r.get("topics") or [],
        "categories": r.get("categories") or [],
        "platforms": _project_platforms(r),
        "pick": r.get("pick"),
        "slot": r.get("slot"),
        "kind": r.get("kind", "search"),
        "created_at": r.get("created_at", ""),
        "first_date": dates[-1] if dates else "",
        "last_date": r.get("last_day", ""),
        "dates": dates,
        "times": len(dates),
    }


def _render_projects(projects: list[dict]) -> str:
    projects.sort(key=lambda r: (r.get("last_day") or "", r.get("stars") or 0), reverse=True)
    occurrences = sum(len(r.get("dates") or []) for r in projects)
    counts: Counter = Counter()
    for r in projects:
        for c in set(_project_platforms(r)):
            counts[c] += 1

    filters = [c for c in FILTERS if counts.get(c)]
    filter_html = [f'<button class="fbtn active" data-plat="all">全部 {len(projects)}</button>']
    for c in filters:
        filter_html.append(
            f'<button class="fbtn" data-plat="{html.escape(c, quote=True)}">'
            f"{html.escape(c)} {counts[c]}</button>"
        )

    cards = "".join(_project_card(r) for r in projects)
    body = (
        f'<div class="pgrid" id="pgrid">{cards}</div>'
        '<div class="pempty" id="pempty" hidden>没有匹配的项目，换个关键词试试。</div>'
    ) if projects else '<div class="empty">还没有项目记录，明天开始自动归档。</div>'

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>项目总表 · GitHub 每日精选</title>
<style>{PROJECT_CSS}</style>
</head>
<body>
<header class="hero">
  <div class="wrap wide">
    <div class="eyebrow">All Projects</div>
    <h1>项目<span class="grad">总表</span></h1>
    <p>把每天推荐过的项目合并去重，按最近推荐时间排列；支持搜索、平台筛选和按 star 排序。</p>
    <div class="meta">
      <span class="pill">已收录 {len(projects)} 个项目</span>
      <span class="pill">共 {occurrences} 次推荐</span>
      <a class="pill" href="projects.json">下载全部数据 ↓</a>
      <a class="pill" href="archive.html">历史存档 →</a>
      <a class="pill" href="index.html">回到今天 →</a>
    </div>
  </div>
</header>
<main class="wrap wide">
  <div class="ptools">
    <input id="psearch" class="psearch" type="search" placeholder="搜索项目名、描述或摘要…">
    <select id="psort" class="psort">
      <option value="recent">最近推荐</option>
      <option value="stars">Star 最多</option>
      <option value="name">名称 A–Z</option>
    </select>
  </div>
  <div class="filters">{''.join(filter_html)}</div>
  <p class="presult">显示 <strong id="pshown">{len(projects)}</strong> / {len(projects)} 个</p>
  {body}
  <p class="pnote">数据位置：每日存档为 <code>day/YYYY-MM-DD.json</code>；全量汇总为 <a href="projects.json">projects.json</a>；候选池涨星快照保存在仓库 <code>data/snapshots/</code>。</p>
</main>
<footer>github-daily · 每天自动整理并归档</footer>
<script>
(function () {{
  var grid = document.getElementById('pgrid');
  if (!grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.pcard'));
  var search = document.getElementById('psearch');
  var sort = document.getElementById('psort');
  var btns = Array.prototype.slice.call(document.querySelectorAll('.fbtn'));
  var shown = document.getElementById('pshown');
  var empty = document.getElementById('pempty');
  var active = 'all';

  function apply() {{
    var q = (search.value || '').trim().toLowerCase();
    var n = 0;
    cards.forEach(function (c) {{
      var okP = active === 'all' || (c.getAttribute('data-platforms') || '').split(',').indexOf(active) >= 0;
      var okQ = !q || (c.getAttribute('data-search') || '').indexOf(q) >= 0;
      var ok = okP && okQ;
      c.hidden = !ok;
      if (ok) n++;
    }});
    shown.textContent = n;
    empty.hidden = n > 0;
  }}

  btns.forEach(function (b) {{
    b.addEventListener('click', function () {{
      btns.forEach(function (x) {{ x.classList.remove('active'); }});
      b.classList.add('active');
      active = b.getAttribute('data-plat');
      apply();
    }});
  }});
  search.addEventListener('input', apply);
  sort.addEventListener('change', function () {{
    var v = sort.value;
    var sorted = cards.slice().sort(function (a, b) {{
      if (v === 'stars') return (+b.getAttribute('data-stars')) - (+a.getAttribute('data-stars'));
      if (v === 'name') return (a.getAttribute('data-name') || '').localeCompare(b.getAttribute('data-name') || '');
      return (b.getAttribute('data-date') || '').localeCompare(a.getAttribute('data-date') || '')
        || (+b.getAttribute('data-stars')) - (+a.getAttribute('data-stars'));
    }});
    sorted.forEach(function (c) {{ grid.appendChild(c); }});
    apply();
  }});
  apply();
}})();
</script>
</body>
</html>
"""


def build(site: Path) -> int:
    day_dir = site / "day"
    day_dir.mkdir(parents=True, exist_ok=True)
    entries: list[tuple[str, dict]] = []
    projects: dict[str, dict] = {}

    for page_path in sorted(day_dir.glob("*.html"), reverse=True):
        day = page_path.stem
        try:
            date.fromisoformat(day)
        except ValueError:
            continue
        page = page_path.read_text("utf-8")
        patched = _patch_page(page, day)
        if patched != page:
            page_path.write_text(patched, "utf-8")

        data = _load_day(day_dir / f"{day}.json")
        meta = _meta_from_data(data) if data else _meta_from_html(page)
        entries.append((day, meta))

        for repo in (data or {}).get("repos", []):
            name = repo.get("full_name")
            if not name:
                continue
            key = name.lower()
            if key in projects:
                projects[key]["dates"].append(day)
            else:
                item = dict(repo)
                item["dates"] = [day]
                item["last_day"] = day
                projects[key] = item

    ordered = list(projects.values())
    ordered.sort(key=lambda r: (r.get("last_day") or "", r.get("stars") or 0), reverse=True)
    (site / "archive.html").write_text(_render_archive(entries), "utf-8")
    (site / "projects.html").write_text(_render_projects(ordered), "utf-8")
    (site / "projects.json").write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(ordered),
        "occurrences": sum(len(r.get("dates") or []) for r in ordered),
        "projects": [_project_record(r) for r in ordered],
    }, ensure_ascii=False, indent=2), "utf-8")
    return len(entries)


def main() -> int:
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    if not (site / "index.html").exists():
        print(f"! 找不到 {site}/index.html")
        return 1
    count = build(site)
    print(f"✓ 已生成 {site}/archive.html、projects.html、projects.json（{count} 天存档）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
