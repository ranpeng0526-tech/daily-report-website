import pytest
from analyzer.news_summarizer import _fallback_summary, _cache_key
from models import NewsArticle, NewsSummary


class TestFallbackSummary:
    def test_returns_top_3(self):
        articles = [
            NewsArticle(title=f"News {i}", description=f"Desc {i}", url="", source="X", published_at="2026-05-19")
            for i in range(10)
        ]
        result = _fallback_summary(articles)
        assert len(result) == 3
        assert all(isinstance(r, NewsSummary) for r in result)
        assert result[0].title == "News 0"

    def test_fewer_than_3_articles(self):
        articles = [
            NewsArticle(title="Only", description="One", url="", source="X", published_at="2026-05-19")
        ]
        result = _fallback_summary(articles)
        assert len(result) == 1

    def test_empty_articles(self):
        result = _fallback_summary([])
        assert result == []

    def test_fallback_marks_unknown(self):
        articles = [
            NewsArticle(title="T", description="D", url="", source="X", published_at="2026-05-19")
        ]
        result = _fallback_summary(articles)
        assert result[0].impact == "未知"
        assert "AI" in result[0].reason


class TestCacheKey:
    def test_same_input_produces_same_key(self):
        articles = [
            NewsArticle(title="A", description="d", url="", source="X", published_at="2026-05-19"),
            NewsArticle(title="B", description="d", url="", source="X", published_at="2026-05-19"),
        ]
        k1 = _cache_key("2026-05-19", articles)
        k2 = _cache_key("2026-05-19", articles)
        assert k1 == k2

    def test_different_date_produces_different_key(self):
        articles = [NewsArticle(title="A", description="d", url="", source="X", published_at="2026-05-19")]
        k1 = _cache_key("2026-05-19", articles)
        k2 = _cache_key("2026-05-20", articles)
        assert k1 != k2

    def test_different_articles_produces_different_key(self):
        a1 = [NewsArticle(title="A", description="d", url="", source="X", published_at="2026-05-19")]
        a2 = [NewsArticle(title="B", description="d", url="", source="X", published_at="2026-05-19")]
        k1 = _cache_key("2026-05-19", a1)
        k2 = _cache_key("2026-05-19", a2)
        assert k1 != k2

    def test_order_independent(self):
        articles = [
            NewsArticle(title="B", description="d", url="", source="X", published_at="2026-05-19"),
            NewsArticle(title="A", description="d", url="", source="X", published_at="2026-05-19"),
        ]
        articles_rev = [
            NewsArticle(title="A", description="d", url="", source="X", published_at="2026-05-19"),
            NewsArticle(title="B", description="d", url="", source="X", published_at="2026-05-19"),
        ]
        assert _cache_key("2026-05-19", articles) == _cache_key("2026-05-19", articles_rev)
