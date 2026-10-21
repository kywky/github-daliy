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
    "安卓": {
        "queries": [
            ("android tool in:name,description", 90), ("topic:android-app", 90),
            ("topic:termux", 90), ("topic:shizuku", 90), ("topic:adb", 90),
            ("topic:f-droid", 90),
        ],
        "color": "#3ddc84", "sigil": "安", "quota": 1, "group": "tool",
    },
    "鸿蒙": {
        "queries": [
            ("topic:harmonyos", 180), ("harmonyos in:name,description", 180),
            ("openharmony in:name,description", 180), ("topic:arkts", 365),
        ],
        "color": "#e33e31", "sigil": "鸿", "quota": 1, "group": "tool",
    },
    "Linux": {
        "queries": [
            ("topic:cli", 90), ("cli tool in:name,description", 90),
            ("linux tool in:name,description", 90), ("topic:linux", 90),
        ],
        "color": "#f59e0b", "sigil": "L", "quota": 1, "group": "tool",
    },
    "Windows": {
        "queries": [
            ("windows tool in:name,description", 90), ("windows app in:name,description", 90),
            ("topic:windows", 90), ("for windows in:description", 90),
        ],
        "color": "#0ea5e9", "sigil": "W", "quota": 1, "group": "tool",
    },
    "AI": {
        "queries": [
            ("topic:llm", 30), ("topic:ai-agents", 30), ("llm in:name,description", 30),
        ],
        "color": "#8b5cf6", "sigil": "AI", "quota": 1, "group": "ai",
    },
    # 学习栏不走搜索，候选来自 classic.py 的经典清单
    "C":       {"queries": [], "color": "#5b6ee1", "sigil": "C", "quota": 1, "group": "learn"},
    "C++":     {"queries": [], "color": "#f34b7d", "sigil": "++", "quota": 1, "group": "learn"},
    "Python":  {"queries": [], "color": "#3572A5", "sigil": "Py", "quota": 1, "group": "learn"},
}

TOOL_CATS = tuple(c for c, cfg in CATEGORIES.items() if cfg.get("group") == "tool")
SEARCH_CATS = tuple(c for c, cfg in CATEGORIES.items() if cfg["queries"])
TOOL_LIB = re.compile(r"sdk\b|framework\b|library\b|开发套件|开发框架", re.I)


BLOCK_NAME = re.compile(
    r"(?:^|[/_-])(awesome|tutorials?|roadmap|interview|cheatsheet|cheats|guide|course|"
    r"cheat|aimbot|crack|keygen|spoof|hwid|wallhack|executor|piracy|"
    r"triggerbot|spinbot|ragehack|hacks?|jailbreak|fairplay|kahoot|answer-?tool|answer-?key|"
    r"ehviewer|exhentai|nhentai|jmcomic|bika|hentai|poc)(?:$|[/_-])",
    re.I,
)
BLOCK_DESC = re.compile(
    r"(?<![a-z0-9])(?:cheats?|cracked|keygen|aimbot|wallhack|triggerbot|spinbot|ragehack|hacks?|"
    r"hwid.?spoofer|dma|unlock.?premium|piracy|bypass.?drm|executor|jailbreak|fairplay|kahoot|"
    r"exam.?answers?|answer.?key|answer.?tool|drm.?circumvention|"
    r"cve-\d{4}-\d+|exploit\s+(?:poc|research|code|chain)|"
    r"nsfw|porn|pornography|hentai|exhentai|nhentai|jmcomic|bika|18\+|adult.?content|"
    r"mod\s+(?:menu|apk|version)|modded\s+apk|cracked\s+apk|hacked\s+apk|premium\s+unlocked|"
    r"unlimited\s+(?:coins|gems|money|diamonds)|free\s+download|official\s+installer|"
    r"setup\s+guide|installation\s+guide|install\s+guide|how\s+to\s+install)(?![a-z0-9])",
    re.I,
)
BLOCK_DESC_CN = re.compile(
    r"破解|作弊|外挂|刷题|代刷|越狱|破甲|激活码|盗版|禁漫|里番|色情|成人漫画|18禁|"
    r"修改版|无限金币|会员解锁|解锁会员|内置菜单|安装教程|下载安装|免费下载|官方下载"
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
    if BLOCK_DESC_CN.search(r["description"]):
        return True
    return False


def fetch_repo(name: str, token: str | None = None) -> dict | None:
    """按 full_name 取单个仓库的实时数据，经典清单用它同步 star 和描述。"""
    try:
        return _shape(_get(f"{API_ROOT}/repos/{urllib.parse.quote(name)}", token=token))
    except Exception as e:
        print(f"    ! 读取 {name} 失败: {e}")
        return None


def fetch_by_categories(today: date, min_stars: int, per_cat_limit: int, token: str | None = None) -> dict[str, dict]:
    pool: dict[str, dict] = {}
    sleep_between = 8 if not token else 2
    for cat in SEARCH_CATS:
        cfg = CATEGORIES[cat]
        for base, days in cfg["queries"]:
            created_after = (today - timedelta(days=days)).isoformat()
            q = f"{base} created:>{created_after} stars:>={min_stars}"
            print(f"  · {cat} / {base}（>{days}d）")
            items = _search_retry(q, per_cat_limit, token)
            kept = 0
            for raw in items:
                r = _shape(raw)
                if is_low_quality(r):
                    continue
                if cat in TOOL_CATS and TOOL_LIB.search(r["full_name"] + " " + r["description"]):
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


def select_daily(pool: dict[str, dict], shown: dict[str, str], today: date, total_limit: int = 7,
                 max_per_tool: int = 2, cooldown_days: int = 3) -> list[dict]:
    """四平台工具各保底 1 个 + 热门 AI 1 个，剩下 2 个名额补给候选最好的工具栏。"""
    cutoff = today - timedelta(days=cooldown_days)

    def last_shown(r: dict) -> date:
        value = shown.get(r["full_name"])
        return date.fromisoformat(value) if value else date.min

    def is_fresh(r: dict) -> bool:
        return last_shown(r) < cutoff

    by_cat: dict[str, list[dict]] = {c: [] for c in SEARCH_CATS}
    for r in pool.values():
        for c in r["categories"]:
            if c in by_cat:
                by_cat[c].append(r)

    chosen: dict[str, dict] = {}
    cat_count: dict[str, int] = {c: 0 for c in SEARCH_CATS}

    def add(r: dict) -> None:
        if r["full_name"] in chosen:
            return
        chosen[r["full_name"]] = r
        for c in r["categories"]:
            if c in cat_count:
                cat_count[c] += 1

    for c, items in by_cat.items():
        quota = CATEGORIES[c].get("quota", 1)
        candidates = sorted(items, key=lambda r: (0 if is_fresh(r) else 1, last_shown(r), -rank_score(r)))
        for r in candidates:
            if cat_count[c] >= quota or len(chosen) >= total_limit:
                break
            add(r)

    for only_fresh in (True, False):
        for r in sorted(pool.values(), key=rank_score, reverse=True):
            if len(chosen) >= total_limit:
                break
            if only_fresh and not is_fresh(r):
                continue
            tools = [c for c in r["categories"] if c in TOOL_CATS]
            if not tools or all(cat_count[c] >= max_per_tool for c in tools):
                continue
            add(r)

    if len(chosen) < total_limit:
        for r in sorted(pool.values(), key=rank_score, reverse=True):
            if len(chosen) >= total_limit:
                break
            add(r)

    return sorted(chosen.values(), key=rank_score, reverse=True)[:total_limit]
