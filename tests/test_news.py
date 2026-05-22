import pytest
from fetchers.news import _market_relevance_score


class TestMarketRelevanceScore:
    def test_stock_keyword_scores_high(self):
        score = _market_relevance_score(
            "Stock market rallies on earnings beat",
            "Tech stocks led the rally with NVIDIA and Apple surging"
        )
        assert score >= 5  # stock, market, ralli, earnings, NVIDIA, Apple, tech stock

    def test_irrelevant_article_scores_zero(self):
        score = _market_relevance_score(
            "Local weather forecast for tomorrow",
            "Sunny with a chance of rain in the afternoon"
        )
        assert score == 0

    def test_single_keyword_match(self):
        score = _market_relevance_score(
            "Bitcoin price prediction for 2026",
            "Crypto markets continue to evolve"
        )
        assert score >= 2  # bitcoin, crypto

    def test_case_insensitive(self):
        score_lower = _market_relevance_score("Nasdaq hits new high", "The index continues to climb")
        score_upper = _market_relevance_score("NASDAQ HITS NEW HIGH", "THE INDEX CONTINUES TO CLIMB")
        assert score_lower == score_upper

    def test_empty_input(self):
        score = _market_relevance_score("", "")
        assert score == 0

    def test_extra_keywords_boost_score(self):
        base = _market_relevance_score("DeepSeek AI model shocks market", "")
        boosted = _market_relevance_score("DeepSeek AI model shocks market", "", extra_keywords=["deepseek"])
        assert boosted > base
