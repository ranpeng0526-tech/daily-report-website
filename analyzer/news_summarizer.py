import hashlib
import json
import os
import subprocess

from config import CACHE_DIR
from logger import setup_logger
from models import NewsArticle, NewsSummary

logger = setup_logger(__name__)

SYSTEM_PROMPT = """你是一位资深美股分析师。用户会提供若干条当天的美股相关新闻，请从中选出最重要的 3 条，并按以下 JSON 格式输出分析结果。

输出严格为 JSON 数组，不要包含任何额外文字：

[
  {
    "title": "新闻原标题（英文）",
    "summary": "一句话中文摘要（30字以内）",
    "impact": "利好/利空/中性",
    "reason": "对市场影响的原因（20字以内）"
  }
]"""


def _cache_key(date_str: str, articles: list[NewsArticle]) -> str:
    """Generate a deterministic cache key from date + article titles."""
    titles = sorted(a.title for a in articles)
    payload = f"{date_str}|{chr(0).join(titles)}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _read_cache(key: str) -> list[NewsSummary] | None:
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    if not os.path.exists(cache_file):
        return None
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [NewsSummary(**item) for item in data]
    except Exception as e:
        logger.warning(f"Cache read failed: {e}")
        return None


def _write_cache(key: str, summaries: list[NewsSummary]) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump([s.__dict__ for s in summaries], f, ensure_ascii=False, indent=2)
        logger.info(f"Cached result to {key}.json")
    except Exception as e:
        logger.warning(f"Cache write failed: {e}")


def summarize_news(articles: list[NewsArticle], date_str: str = "") -> list[NewsSummary]:
    """Use local Claude CLI to pick top 3 news + summarize with market impact."""
    if not articles:
        logger.warning("No articles to summarize")
        return []

    # Check cache first
    key = _cache_key(date_str, articles)
    cached = _read_cache(key)
    if cached:
        logger.info(f"Cache hit: {key}")
        return cached

    news_text_parts = []
    for i, art in enumerate(articles[:10], 1):
        news_text_parts.append(f"[{i}] 标题: {art.title}\n    内容: {art.description}")

    user_message = "以下为今日美股相关新闻，请选出最重要的 3 条并分析：\n\n" + "\n\n".join(news_text_parts)
    prompt = f"{SYSTEM_PROMPT}\n\n{user_message}"

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            logger.error(f"Claude CLI exited with code {result.returncode}: {result.stderr}")
            return _fallback_summary(articles)

        text = result.stdout.strip()

        # Extract JSON array from output (Claude may add commentary)
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1 or start >= end:
            logger.error("No JSON array found in Claude CLI output")
            logger.debug(f"Raw output: {text[:500]}")
            return _fallback_summary(articles)

        json_text = text[start:end + 1]
        raw = json.loads(json_text)
        results = [NewsSummary(**item) for item in raw]
        logger.info(f"Claude CLI: summarized {len(results)} news items")

        # Persist to cache
        _write_cache(key, results)
        return results

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude CLI output as JSON: {e}")
        logger.debug(f"Raw output: {result.stdout if 'result' in dir() else 'N/A'}")
        return _fallback_summary(articles)
    except FileNotFoundError:
        logger.error("claude CLI not found. Make sure Claude Code is installed.")
        return _fallback_summary(articles)
    except subprocess.TimeoutExpired:
        logger.error("Claude CLI timed out (120s)")
        return _fallback_summary(articles)
    except Exception as e:
        logger.error(f"Claude CLI call failed: {e}")
        return _fallback_summary(articles)


def _fallback_summary(articles: list[NewsArticle]) -> list[NewsSummary]:
    """Fallback: return top 3 articles without AI summarization."""
    results: list[NewsSummary] = []
    for art in articles[:3]:
        results.append(NewsSummary(
            title=art.title,
            summary=art.description[:80],
            impact="未知",
            reason="AI 分析暂不可用，请手动运行",
        ))
    return results
