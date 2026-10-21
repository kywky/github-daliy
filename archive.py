import html
import json
import sys
from datetime import date
from pathlib import Path


WEEKDAYS = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")
PLATFORMS = ("安卓", "鸿蒙", "Linux", "Windows")
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


def _meta_from_json(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text("utf-8"))
    except Exception:
        return None
    repos = data.get("repos")
    if not isinstance(repos, list):
        return None
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
        return page
    page = page.replace('href="archive.html"', 'href="../archive.html"')
    banner = (
        f"{BANNER_MARK}\n"
        '<div style="background:#0f172a;color:#cbd5e1;font-size:13px;text-align:center;'
        'padding:10px 16px;line-height:1.6">'
        f"{html.escape(day)} 存档 · "
        '<a href="../index.html" style="color:#c7d2fe;font-weight:600">回到今天</a>'
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


def build(site: Path) -> int:
    day_dir = site / "day"
    day_dir.mkdir(parents=True, exist_ok=True)
    entries: list[tuple[str, dict]] = []

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

        meta = _meta_from_json(day_dir / f"{day}.json") or _meta_from_html(page)
        entries.append((day, meta))

    (site / "archive.html").write_text(_render_archive(entries), "utf-8")
    return len(entries)


def main() -> int:
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    if not (site / "index.html").exists():
        print(f"! 找不到 {site}/index.html")
        return 1
    count = build(site)
    print(f"✓ 已生成 {site}/archive.html（{count} 天存档）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
