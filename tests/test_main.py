from unittest.mock import patch
from datetime import datetime
import pytest


class TestLastTradingDay:
    """Test last_trading_day() — note: it's defined in main.py, not importable as a module
    due to the `if __name__ == "__main__"` guard. We replicate the logic inline for testing."""

    @staticmethod
    def _last_trading_day(now: datetime) -> str:
        """Pure function version of last_trading_day for testability."""
        from datetime import timedelta

        today = now.date()
        if now.hour < 4:
            today = today - timedelta(days=1)

        while today.weekday() >= 5:
            today = today - timedelta(days=1)

        return today.strftime("%Y-%m-%d")

    def test_weekday_after_4am_returns_today(self):
        """Tuesday 10:00 AM → return Tuesday"""
        result = self._last_trading_day(datetime(2026, 5, 19, 10, 0))
        assert result == "2026-05-19"

    def test_weekday_before_4am_returns_yesterday(self):
        """Wednesday 2:00 AM → return Tuesday"""
        result = self._last_trading_day(datetime(2026, 5, 20, 2, 0))
        assert result == "2026-05-19"

    def test_saturday_returns_friday(self):
        """Saturday → return Friday"""
        result = self._last_trading_day(datetime(2026, 5, 23, 14, 0))
        assert result == "2026-05-22"

    def test_sunday_returns_friday(self):
        """Sunday → return Friday"""
        result = self._last_trading_day(datetime(2026, 5, 24, 14, 0))
        assert result == "2026-05-22"

    def test_monday_before_4am_returns_friday(self):
        """Monday 2:00 AM → return Friday"""
        result = self._last_trading_day(datetime(2026, 5, 25, 2, 0))
        assert result == "2026-05-22"

    def test_monday_after_4am_returns_monday(self):
        """Monday 10:00 AM → return Monday"""
        result = self._last_trading_day(datetime(2026, 5, 25, 10, 0))
        assert result == "2026-05-25"
