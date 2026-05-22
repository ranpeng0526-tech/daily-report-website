import time
from datetime import datetime, timedelta

import yfinance as yf

from config import INDICES
from logger import setup_logger
from models import MarketIndex

logger = setup_logger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def _parse_scalar(series, col: str) -> float:
    """Extract a scalar float from a pandas Series cell (handles multi-level columns)."""
    val = series[col]
    return float(val.iloc[0] if hasattr(val, "iloc") else val)


def fetch_index_data(ticker: str, name: str, target_date: str) -> MarketIndex | None:
    """Fetch a single index's daily data with retry.

    target_date: YYYY-MM-DD — the report date; used to anchor the historical window.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            end_dt = datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=1)
            start_dt = end_dt - timedelta(days=45)

            hist = yf.download(
                ticker,
                start=start_dt.strftime("%Y-%m-%d"),
                end=end_dt.strftime("%Y-%m-%d"),
                progress=False,
                auto_adjust=True,
            )

            if hist.empty:
                logger.warning(f"{name} ({ticker}): no data (attempt {attempt}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * attempt)
                    continue
                return None

            last = hist.iloc[-1]
            close = _parse_scalar(last, "Close")
            open_price = _parse_scalar(last, "Open")
            high = _parse_scalar(last, "High")
            low = _parse_scalar(last, "Low")
            row_date = last.name.strftime("%Y-%m-%d") if hasattr(last.name, "strftime") else str(last.name)

            # Daily change
            if len(hist) >= 2:
                prev_close = _parse_scalar(hist.iloc[-2], "Close")
                change_pct = ((close - prev_close) / prev_close) * 100 if prev_close != 0 else 0.0
            else:
                change_pct = ((close - open_price) / open_price) * 100 if open_price != 0 else 0.0

            # 5-day change (≈5 trading days back)
            change_5d = 0.0
            if len(hist) >= 6:
                close_5d = _parse_scalar(hist.iloc[-6], "Close")
                if close_5d != 0:
                    change_5d = ((close - close_5d) / close_5d) * 100

            # Month-to-date change (first bar whose month matches target month)
            change_mtd = 0.0
            target_month = datetime.strptime(target_date, "%Y-%m-%d").month
            month_start_bars = [i for i in range(len(hist)) if hist.iloc[i].name.month == target_month]
            if len(month_start_bars) >= 2:
                close_month_start = _parse_scalar(hist.iloc[month_start_bars[0]], "Close")
                if close_month_start != 0:
                    change_mtd = ((close - close_month_start) / close_month_start) * 100

            return MarketIndex(
                name=name,
                ticker=ticker,
                open=round(open_price, 2),
                close=round(close, 2),
                high=round(high, 2),
                low=round(low, 2),
                change_pct=round(change_pct, 2),
                change_5d=round(change_5d, 2),
                change_mtd=round(change_mtd, 2),
                date=row_date,
            )

        except Exception as e:
            logger.error(f"{name} ({ticker}) attempt {attempt}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
            else:
                return None

    return None


def fetch_all_indices(target_date: str) -> list[MarketIndex]:
    """Fetch all configured indices. Returns list of MarketIndex (with .error set on failure)."""
    results: list[MarketIndex] = []
    for name, ticker in INDICES.items():
        logger.info(f"Fetching {name} ({ticker})...")
        data = fetch_index_data(ticker, name, target_date)
        if data:
            results.append(data)
        else:
            results.append(MarketIndex(
                name=name, ticker=ticker,
                open=0, close=0, high=0, low=0, change_pct=0,
                error="数据获取失败",
            ))
        time.sleep(1)
    return results
