import argparse
import json
import os
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from env import load_dotenv  # noqa: E402
load_dotenv()

from github import CATEGORIES, fetch_by_categories, fetch_repo, select_daily  # noqa: E402
from classic import candidates as classic_candidates, pick_languages  # noqa: E402
from render import render  # noqa: E402
from summarize import summarize  # noqa: E402


ROOT = Path(__file__).parent
DATA = ROOT / "data"
DIST = ROOT / "dist"
SNAPS = DATA / "snapshots"
SHOWN = DATA / "shown.json"
SHOWN_COOLDOWN_DAYS = 3
MAX_WINDOW = max(days for cfg in CATEGORIES.values() for _, days in cfg["queries"])


def load_previous_snapshot(today: date) -> tuple[str | None, dict[str, int]]:
    SNAPS.mkdir(parents=True, exist_ok=True)
    files = sorted(f for f in SNAPS.glob("*.json") if f.stem < today.isoformat())
    if not files:
        return None, {}
    latest = files[-1]
    try:
        return latest.stem, json.loads(latest.read_text())
    except Exception:
        return None, {}


def save_snapshot(today: date, pool: dict[str, dict]) -> None:
    SNAPS.mkdir(parents=True, exist_ok=True)
    payload = {name: r["stars"] for name, r in pool.items()}
    (SNAPS / f"{today.isoformat()}.json").write_text(json.dumps(payload, ensure_ascii=False))


def attach_speed(pool: dict[str, dict], prev_date: str | None, prev_stars: dict[str, int], today: date) -> None:
    if not prev_date:
        return
    span = max(1, (today - date.fromisoformat(prev_date)).days)
    for r in pool.values():
        old = prev_stars.get(r["full_name"])
        if old is None:
            r["star_delta"] = None
            r["stars_per_day"] = None
        else:
            r["star_delta"] = r["stars"] - old
            r["stars_per_day"] = round((r["stars"] - old) / span, 1)


def load_shown() -> dict[str, str]:
    if not SHOWN.exists():
        return {}
    try:
        return json.loads(SHOWN.read_text())
    except Exception:
        return {}


def save_shown(shown: dict[str, str], repos: list[dict], today: date) -> None:
    for r in repos:
        shown[r["full_name"]] = today.isoformat()
    SHOWN.parent.mkdir(parents=True, exist_ok=True)
    SHOWN.write_text(json.dumps(shown, ensure_ascii=False, indent=2, sort_keys=True))


def pick_learning(today: date, shown: dict[str, str], token: str | None, count: int) -> list[dict]:
    picked: list[dict] = []
    for lang in pick_languages(today, count):
        for name, note in classic_candidates(lang, shown, today):
            r = fetch_repo(name, token=token)
            if r is None:
                continue
            r["categories"] = [lang]
            r["kind"] = "learn"
            r["note"] = note
            r["star_delta"] = None
            r["stars_per_day"] = None
            picked.append(r)
            break
        time.sleep(1)
    return picked


def main() -> int:
    p = argparse.ArgumentParser(description="生成每日 GitHub 好项目静态页")
    p.add_argument("--min-stars", type=int, default=50, help="工具/AI 栏最少 star 数，默认 50")
    p.add_argument("--limit", type=int, default=9, help="每天展示多少个，默认 9")
    p.add_argument("--learn", type=int, default=2, help="其中经典学习项目多少个，默认 2")
    p.add_argument("--per-cat", type=int, default=50, help="每个分类每个查询拉多少，默认 50")
    args = p.parse_args()

    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=MAX_WINDOW)
    token = os.environ.get("GITHUB_TOKEN") or None
    shown = load_shown()

    print(f"→ 抓取: stars>={args.min_stars} per_cat={args.per_cat}" + (" [GITHUB_TOKEN]" if token else " [未认证]"))
    pool = fetch_by_categories(today, args.min_stars, args.per_cat, token=token)
    print(f"  ✓ 候选池 {len(pool)} 个")

    prev_date, prev_stars = load_previous_snapshot(today)
    if prev_date:
        print(f"  · 对比快照 {prev_date}（{len(prev_stars)} 个仓库）计算涨星速度")
    else:
        print("  · 暂无前一日快照，本次按总 star 排序；明天起即可显示日增")
    attach_speed(pool, prev_date, prev_stars, today)

    search_limit = max(0, args.limit - args.learn)
    repos = select_daily(pool, shown, today, total_limit=search_limit, cooldown_days=SHOWN_COOLDOWN_DAYS)
    learn = pick_learning(today, shown, token, args.learn)
    print(f"  · 工具/AI 选出 {len(repos)} 个，经典学习 {len(learn)} 个")
    repos = repos + learn

    print(f"→ 生成摘要: {os.environ.get('LLM_BASE_URL','(未配置)')} / {os.environ.get('LLM_MODEL','(未配置)')}" if os.environ.get("LLM_API_KEY") else "→ 未配置 LLM_API_KEY，摘要使用原始描述")
    for i, r in enumerate(repos, 1):
        print(f"  [{i}/{len(repos)}] {r['full_name']}")
        r["summary"] = summarize(r)
        time.sleep(1)

    DIST.mkdir(exist_ok=True)
    (DIST / "repos.json").write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_start": start.isoformat(),
        "window_end": today.isoformat(),
        "snapshot_compared": prev_date,
        "repos": repos,
    }, ensure_ascii=False, indent=2))
    (DIST / "index.html").write_text(render(repos, today.isoformat(), prev_date))

    save_snapshot(today, pool)
    save_shown(load_shown(), repos, today)

    print(f"✓ 已写入 {DIST}/index.html 与 data/snapshots/{today.isoformat()}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
