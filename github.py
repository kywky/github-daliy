import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request


API_ROOT = "https://api.github.com"
UA = "github-daily/0.1"


CATEGORIES = {
    "C/C++":  {"queries": ["language:cpp", "language:c"], "color": "#5b6ee1", "sigil": "C"},
    "AI":     {"queries": ["topic:llm", "topic:ai-agents"], "color": "#8b5cf6", "sigil": "AI"},
    "Python": {"queries": ["language:python"], "color": "#f59e0b", "sigil": "Py"},
    "GPU":    {"queries": ["topic:cuda", "gpu in:name,description"], "color": "#ef4444", "sigil": "GPU"},
    "自动化":  {"queries": ["automation in:name,description", "topic:mcp-server"], "color": "#10b981", "sigil": "A"},
}


BLOCK_NAME = re.compile(
    r"(?:^|[/_-])(awesome|tutorials?|roadmap|interview|cheatsheet|cheats|guide|course|"
    r"cheat|aimbot|crack|keygen|spoof|hwid|wallhack|executor|piracy|"
    r"triggerbot|spinbot|ragehack|hacks?)(?:$|[/_-])",
    re.I,
)
BLOCK_DESC = re.compile(
    r"\b(cheat|cracked|keygen|aimbot|wallhack|triggerbot|spinbot|ragehack|hack|hwid.?spoofer|dma|"
    r"unlock.?premium|piracy|bypass.?drm|executor)\b",
    re.I,
)


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
    return False


def fetch_by_categories(created_after: str, min_stars: int, per_cat_limit: int, token: str | None = None) -> dict[str, dict]:
    pool: dict[str, dict] = {}
    sleep_between = 8 if not token else 2
    for cat, cfg in CATEGORIES.items():
        for base in cfg["queries"]:
            q = f"{base} created:>{created_after} stars:>={min_stars}"
            print(f"  · {cat} / {base}")
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


def select_balanced(pool: dict[str, dict], total_limit: int, per_cat_quota: int = 2) -> list[dict]:
    by_cat: dict[str, list[dict]] = {c: [] for c in CATEGORIES}
    for r in pool.values():
        for c in r["categories"]:
            by_cat[c].append(r)

    chosen: dict[str, dict] = {}
    for items in by_cat.values():
        for r in sorted(items, key=rank_score, reverse=True)[:per_cat_quota]:
            chosen[r["full_name"]] = r

    if len(chosen) < total_limit:
        for r in sorted(pool.values(), key=rank_score, reverse=True):
            if len(chosen) >= total_limit:
                break
            chosen.setdefault(r["full_name"], r)

    return sorted(chosen.values(), key=rank_score, reverse=True)[:total_limit]
