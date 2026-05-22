import argparse
import sys
from datetime import datetime, timedelta

from config import REPORT_OUTPUT_DIR
from logger import setup_logger
from fetchers.market_data import fetch_all_indices
from fetchers.news import fetch_top_news
from analyzer.news_summarizer import summarize_news
from report.generator import generate_report

logger = setup_logger("main")


def last_trading_day() -> str:
    """Return the most recent trading day (Mon-Fri) in YYYY-MM-DD.

    If today is a weekday and it's after US market close (4 PM ET ≈ 4 AM Beijing),
    today is the last trading day. Otherwise use the previous weekday.
    """
    now = datetime.now()
    today = now.date()
    if now.hour < 4:
        today = today - timedelta(days=1)

    while today.weekday() >= 5:  # Sat=5, Sun=6
        today = today - timedelta(days=1)

    return today.strftime("%Y-%m-%d")


def run_daily_report(date_str: str | None = None) -> str | None:
    """Execute the full daily report pipeline. Returns the report file path."""
    if date_str is None:
        date_str = last_trading_day()

    logger.info(f"========== 开始生成 {date_str} 美股晨报（基于收盘数据）==========")

    logger.info("[1/3] 获取三大指数数据...")
    indices = fetch_all_indices(target_date=date_str)

    logger.info("[2/3] 获取美股新闻 + AI 分析...")
    articles = fetch_top_news(target_date=date_str)
    top_news = summarize_news(articles, date_str=date_str)

    logger.info("[3/3] 生成日报...")
    filepath = generate_report(indices, top_news, date_str)

    logger.info(f"========== 日报生成完成: {filepath} ==========")
    return filepath


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="每日美股市场晨报")
    parser.add_argument(
        "--date", "-d",
        type=str,
        default=None,
        help="指定报告日期 (YYYY-MM-DD)，默认为最近一个交易日",
    )
    args = parser.parse_args()

    if args.date:
        try:
            datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            logger.error(f"日期格式错误: {args.date}，应为 YYYY-MM-DD")
            sys.exit(1)

    try:
        run_daily_report(date_str=args.date)
    except KeyboardInterrupt:
        logger.info("用户中断")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"日报生成失败: {e}")
        sys.exit(1)
