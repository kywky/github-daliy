import json
import os
import urllib.request


DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


PROMPT_TEMPLATE = """请用中文简洁总结这个 GitHub 项目，回答 3 个问题（每点 1-2 句，用无序列表，加粗小标题）：
- **解决什么**：项目要解决的具体问题
- **适合谁**：目标用户或典型使用场景
- **亮点**：一句话说明它独特/值得关注之处

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
        return f"原始描述：{repo['description']}\n\n（未配置 LLM_API_KEY，接入后可获得中文摘要）"
    return "（未配置 LLM_API_KEY，且项目无描述）"


def _call_openai_compat(prompt: str, key: str, base_url: str, model: str) -> str | None:
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "max_tokens": 400,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {key}")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        detail = ""
        if hasattr(exc, "read"):
            try:
                detail = exc.read().decode("utf-8", "ignore")[:200]
            except Exception:
                pass
        print(f"  ! LLM 调用失败 ({type(exc).__name__}): {exc} {detail}")
        return None


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
    return _call_openai_compat(prompt, key, base_url, model) or _fallback(repo)
