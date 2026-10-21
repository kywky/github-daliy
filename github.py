import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta


API_ROOT = "https://api.github.com"
UA = "github-daily/0.1"


CATEGORIES = {
    "C/C++":  {"queries": ["language:cpp", "language:c"], "days": 7, "color": "#5b6ee1", "sigil": "C"},
    "AI":     {"queries": ["topic:llm", "topic:ai-agents"], "days": 7, "color": "#8b5cf6", "sigil": "AI"},
    "Python": {"queries": ["language:python"], "days": 7, "color": "#f59e0b", "sigil": "Py"},
    "GPU":    {"queries": ["topic:cuda", "topic:gpu", "gpu in:name,description", "topic:llm-inference"], "days": 30, "color": "#ef4444", "sigil": "GPU"},
    "自动化":  {"queries": ["topic:automation", "topic:browser-automation", "topic:mcp-server"], "days": 30, "color": "#10b981", "sigil": "A"},
}


BLOCK_NAME = re.compile(
    r"(?:^|[/_-])(awesome|tutorials?|roadmap|interview|cheatsheet|cheats|guide|course|"
    r"cheat|aimbot|crack|keygen|spoof|hwid|wallhack|executor|piracy|"
    r"triggerbot|spinbot|ragehack|hacks?|jailbreak|fairplay|kahoot|answer-?tool|answer-?key)(?:$|[/_-])",
    re.I,
)
BLOCK_DESC = re.compile(
    r"\b(cheat|cracked|keygen|aimbot|wallhack|triggerbot|spinbot|ragehack|hacks?|hwid.?spoofer|dma|"
    r"unlock.?premium|piracy|bypass.?drm|executor|jailbreak|fairplay|kahoot|exam.?answers?|"
    r"answer.?key|answer.?tool|drm.?circumvention)\b",
    re.I,
)
BLOCK_DESC_CN = re.compile(r"破解|作弊|外挂|刷题|代刷|越狱|破甲|激活码|盗版")


def _get(url: str, token: str | None = None) -> dict:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", UA)
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _search(query: str, limit: int, token: str | None) -> list[dict]:
    params = urllib.parse.urlencode({
        "q": query, "sort": "stars", "order": "desc", "per_page": limit,
    })
    return _get(f"{API_ROOT}/search/repositories?{params}", token=token).get("items", [])


def _search_retry(query: str, limit: int, token: str | None, max_tries: int = 2) -> list[dict]:
    for attempt in range(max_tries):
        try:
            return _search(query, limit, token)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < max_tries - 1:
                print(f"    ! 限流 (HTTP {e.code})，65s 后重试...")
                time.sleep(65)
                continue
            print(f"    ! 查询失败: HTTP {e.code}")
            return []
        except Exception as e:
            print(f"    ! 查询异常: {e}")
            return []
    return []


def _shape(r: dict) -> dict:
    return {
        "full_name": r["full_name"],
        "url": r["html_url"],
        "description": (r.get("description") or "").strip(),
        "stars": r["stargazers_count"],
        "forks": r.get("forks_count") or 0,
        "language": r.get("language") or "",
        "topics": r.get("topics") or [],
        "created_at": r["created_at"][:10],
        "homepage": r.get("homepage") or "",
        "archived": bool(r.get("archived")),
        "fork": bool(r.get("fork")),
        "has_license": bool(r.get("license")),
        "categories": [],
    }


def is_low_quality(r: dict) -> bool:
    if r["archived"] or r["fork"]:
        return True
    if len(r["description"]) < 15:
        return True
    if BLOCK_NAME.search(r["full_name"]):
        return True
    if BLOCK_DESC.search(r["description"]):
        return True
    if BLOCK_DESC_CN.search(r["description"]):
        return True
    return False


def fetch_by_categories(today: date, min_stars: int, per_cat_limit: int, token: str | None = None) -> dict[str, dict]:
    pool: dict[str, dict] = {}
    sleep_between = 8 if not token else 2
    for cat, cfg in CATEGORIES.items():
        days = cfg.get("days", 7)
        created_after = (today - timedelta(days=days)).isoformat()
        for base in cfg["queries"]:
            q = f"{base} created:>{created_after} stars:>={min_stars}"
            print(f"  · {cat} / {base}（>{days}d）")
            items = _search_retry(q, per_cat_limit, token)
            kept = 0
            for raw in items:
                r = _shape(raw)
                if is_low_quality(r):
                    continue
                kept += 1
                key = r["full_name"]
                if key not in pool:
                    pool[key] = r
                if cat not in pool[key]["categories"]:
                    pool[key]["categories"].append(cat)
            print(f"    ✓ {len(items)} 条 / 过滤后 {kept} 条")
            time.sleep(sleep_between)
    return pool


def rank_score(r: dict) -> float:
    if r.get("stars_per_day") is not None:
        return float(r["stars_per_day"])
    return r["stars"] / 1000.0


def select_daily(pool: dict[str, dict], shown: dict[str, str], today: date, total_limit: int = 10,
                 per_cat_quota: int = 2, max_per_cat: int = 3, cooldown_days: int = 3) -> list[dict]:
    cutoff = today - timedelta(days=cooldown_days)

    def last_shown(r: dict) -> date:
        value = shown.get(r["full_name"])
        return date.fromisoformat(value) if value else date.min

    def is_fresh(r: dict) -> bool:
        return last_shown(r) < cutoff

    by_cat: dict[str, list[dict]] = {c: [] for c in CATEGORIES}
    for r in pool.values():
        for c in r["categories"]:
            by_cat[c].append(r)

    chosen: dict[str, dict] = {}
    cat_count: dict[str, int] = {c: 0 for c in CATEGORIES}

    def add(r: dict) -> None:
        if r["full_name"] in chosen:
            return
        chosen[r["full_name"]] = r
        for c in r["categories"]:
            cat_count[c] += 1

    for c, items in by_cat.items():
        candidates = sorted(items, key=lambda r: (0 if is_fresh(r) else 1, last_shown(r), -rank_score(r)))
        for r in candidates:
            if cat_count[c] >= per_cat_quota or len(chosen) >= total_limit:
                break
            add(r)

    for only_fresh in (True, False):
        for r in sorted(pool.values(), key=rank_score, reverse=True):
            if len(chosen) >= total_limit:
                break
            if only_fresh and not is_fresh(r):
                continue
            if r["categories"] and all(cat_count[c] >= max_per_cat for c in r["categories"]):
                continue
            add(r)

    if len(chosen) < total_limit:
        for r in sorted(pool.values(), key=rank_score, reverse=True):
            if len(chosen) >= total_limit:
                break
            add(r)

    return sorted(chosen.values(), key=rank_score, reverse=True)[:total_limit]
