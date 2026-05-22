import re
from collections import Counter
from datetime import datetime

import requests
import urllib3

from config import FINNHUB_KEY, FINNHUB_BASE_URL, MARKET_KEYWORDS
from logger import setup_logger
from models import NewsArticle

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = setup_logger(__name__)

# Minimum word length and stop words for dynamic keyword extraction
_STOP_WORDS = {
    "the", "and", "for", "with", "from", "that", "this", "have", "been",
    "will", "not", "are", "its", "has", "over", "more", "new", "after",
    "says", "into", "year", "just", "like", "what", "when", "make",
    "could", "would", "should", "about", "than", "they", "their",
    "which", "there", "being", "some", "were", "your", "also", "into",
}


def _extract_dynamic_keywords(articles: list[dict], top_n: int = 10) -> list[str]:
    """Extract frequent capitalized words from headlines as dynamic keywords."""
    words: list[str] = []
    for art in articles:
        title = (art.get("headline") or "").strip()
        # Collect capitalized words (likely proper nouns / tickers)
        for word in title.split():
            if word[0].isupper() and len(word) >= 2:
                clean = word.strip(".,!?:;()[]{}'\"")
                if clean.lower() not in _STOP_WORDS:
                    words.append(clean.lower())
    freq = Counter(words)
    return [w for w, _ in freq.most_common(top_n)]


def _market_relevance_score(title: str, summary: str, extra_keywords: list[str] | None = None) -> int:
    """Score an article's relevance to US stock market. Higher = more relevant."""
    text = f"{title} {summary}".lower()
    score = 0
    all_keywords = list(MARKET_KEYWORDS)
    if extra_keywords:
        all_keywords.extend(extra_keywords)
    for kw in all_keywords:
        kw_lower = kw.lower()
        # For short keywords (≤2 chars), require word boundaries to avoid false
        # positives (e.g. "AI" matching inside "rain")
        if len(kw_lower) <= 2:
            if re.search(rf"\b{re.escape(kw_lower)}\b", text):
                score += 1
        elif kw_lower in text:
            score += 1
    return score


def fetch_top_news(count: int = 10, target_date: str | None = None) -> list[NewsArticle]:
    """Fetch latest US stock market news from Finnhub.

    target_date: YYYY-MM-DD — if provided, prefers articles from this date.
    """
    if not FINNHUB_KEY:
        logger.error("FINNHUB_KEY is not configured")
        return []

    try:
        url = f"{FINNHUB_BASE_URL}/news"
        params = {"category": "general", "token": FINNHUB_KEY}
        resp = requests.get(url, params=params, timeout=15, verify=False)
        resp.raise_for_status()
        articles = resp.json()

        if not articles:
            logger.warning("Finnhub: no news returned")
            return []

        # Extract dynamic keywords from today's headlines
        extra_keywords = _extract_dynamic_keywords(articles)

        # Filter & score
        results: list[NewsArticle] = []
        date_filter = None
        if target_date:
            date_filter = datetime.strptime(target_date, "%Y-%m-%d").date()

        for art in articles:
            title = (art.get("headline") or "").strip()
            summary = (art.get("summary") or "").strip()
            if not title or not summary:
                continue

            ts = art.get("datetime", 0)
            pub_dt = datetime.fromtimestamp(ts)
            pub_date = pub_dt.date()

            # If target_date is given, prefer that date; fall back to near dates
            if date_filter and pub_date != date_filter:
                continue

            score = _market_relevance_score(title, summary, extra_keywords)
            results.append(NewsArticle(
                title=title,
                description=summary,
                url=art.get("url", ""),
                source=art.get("source", "Unknown"),
                published_at=pub_dt.strftime("%Y-%m-%d %H:%M"),
                _score=score,
            ))

        # If date filter yields too few results, lift the filter
        if date_filter and len(results) < 5:
            logger.info(f"Only {len(results)} articles match {target_date}, lifting date filter")
            results.clear()
            for art in articles:
                title = (art.get("headline") or "").strip()
                summary = (art.get("summary") or "").strip()
                if not title or not summary:
                    continue
                ts = art.get("datetime", 0)
                pub_dt = datetime.fromtimestamp(ts)
                score = _market_relevance_score(title, summary, extra_keywords)
                results.append(NewsArticle(
                    title=title,
                    description=summary,
                    url=art.get("url", ""),
                    source=art.get("source", "Unknown"),
                    published_at=pub_dt.strftime("%Y-%m-%d %H:%M"),
                    _score=score,
                ))

        # Sort by relevance score, top N
        results.sort(key=lambda x: x._score, reverse=True)
        results = results[:count]

        logger.info(f"Finnhub: fetched {len(results)} articles (filtered from {len(articles)}, "
                     f"dynamic keywords: {extra_keywords[:5]})")
        return results

    except requests.RequestException as e:
        logger.error(f"Finnhub request failed: {e}")
        return []
