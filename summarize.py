import json
import os
import time
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
RETRY_WAITS = [0, 5, 10]
FALLBACK_MODELS = ["glm-4-flash-250414", "glm-z1-flash"]


PROMPT_TEMPLATE = """请用中文简洁总结这个 GitHub 项目。严格按以下三行格式输出，不要序号、不要 markdown 符号、不要额外解释：
解决什么：<项目要解决的具体问题，1-2 句>
适合谁：<目标用户或典型使用场景，1-2 句>
亮点：<一句话说明它独特或值得关注之处>

项目信息：
名称: {full_name}
语言: {language}
Stars: {stars}
分类: {categories}
Topics: {topics}
描述: {description}
"""


def _fallback(repo: dict) -> str:
    if repo.get("description"):
        return f"原始描述：{repo['description']}\n\n（摘要生成失败，本次展示原文）"
    return "（项目无描述，且摘要生成失败）"


def _post(prompt: str, key: str, base_url: str, model: str) -> tuple[str | None, str]:
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "max_tokens": 2048,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {key}")

    for wait in RETRY_WAITS:
        if wait:
            print(f"    · {model} 限流，{wait}s 后重试")
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            text = (data["choices"][0]["message"]["content"] or "").strip()
            if not text:
                print(f"    ! {model} 返回空内容")
                return None, "empty"
            return text, "ok"
        except urllib.error.HTTPError as e:
            detail = ""
            try:
                detail = e.read().decode("utf-8", "ignore")[:160]
            except Exception:
                pass
            if e.code == 429:
                continue
            if e.code == 404:
                return None, "missing"
            print(f"    ! {model} 调用失败 HTTP {e.code}: {detail}")
            return None, "error"
        except Exception as exc:
            print(f"    ! {model} 调用异常: {exc}")
            continue
    return None, "rate"


def summarize(repo: dict) -> str:
    key = os.environ.get("LLM_API_KEY")
    if not key:
        return _fallback(repo)
    base_url = os.environ.get("LLM_BASE_URL", DEFAULT_BASE_URL)
    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL)

    prompt = PROMPT_TEMPLATE.format(
        full_name=repo["full_name"],
        language=repo["language"] or "-",
        stars=repo["stars"],
        categories=", ".join(repo.get("categories") or []) or "-",
        topics=", ".join(repo["topics"]) or "-",
        description=repo["description"] or "-",
    )

    models = [model]
    if "bigmodel" in base_url:
        models += [m for m in FALLBACK_MODELS if m != model]

    for m in models:
        text, kind = _post(prompt, key, base_url, m)
        if text:
            return text
        if kind not in ("rate", "empty"):
            break
    return _fallback(repo)
