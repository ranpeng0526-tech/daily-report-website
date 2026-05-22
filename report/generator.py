import json
import os
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from jinja2 import Template

from config import REPORT_OUTPUT_DIR
from logger import setup_logger
from models import MarketIndex, NewsSummary

logger = setup_logger(__name__)

_TEMPLATE_PATH = Path(__file__).parent / "template.md.j2"


def generate_report(
    indices: list[MarketIndex],
    top_news: list[NewsSummary],
    date_str: str,
) -> str:
    """Generate a Markdown report and save to output directory.

    Returns the file path of the generated report.
    """
    template_text = _TEMPLATE_PATH.read_text(encoding="utf-8")
    template = Template(template_text)
    payload = _build_report_payload(indices, top_news, date_str)
    content = template.render(
        date=date_str,
        indices=indices,
        top_news=top_news,
        market_overview=payload["market_overview"],
        generated_at=payload["generated_at"],
    )

    os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)
    filename = f"{date_str}-美股晨报.md"
    filepath = os.path.join(REPORT_OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    _write_latest_json(indices, top_news, date_str, payload=payload)

    logger.info(f"Report generated: {filepath}")
    return filepath


def _write_latest_json(
    indices: list[MarketIndex],
    top_news: list[NewsSummary],
    date_str: str,
    payload: dict | None = None,
) -> str:
    if payload is None:
        payload = _build_report_payload(indices, top_news, date_str)
    filepath = os.path.join(REPORT_OUTPUT_DIR, "latest-report.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.info(f"Latest report JSON generated: {filepath}")
    return filepath


def _build_report_payload(
    indices: list[MarketIndex],
    top_news: list[NewsSummary],
    date_str: str,
) -> dict:
    valid_indices = [idx for idx in indices if not idx.error]
    advancers = sum(1 for idx in valid_indices if idx.change_pct >= 0)
    decliners = sum(1 for idx in valid_indices if idx.change_pct < 0)

    if advancers >= 2:
        sentiment = "整体市场情绪偏积极。"
    elif decliners >= 2:
        sentiment = "整体市场情绪偏谨慎。"
    else:
        sentiment = "市场涨跌互现，表现分化。"

    return {
        "title": "每日美股市场晨报",
        "date": date_str,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "indices": [asdict(idx) for idx in indices],
        "top_news": [asdict(news) for news in top_news],
        "market_overview": {
            "advancers": advancers,
            "decliners": decliners,
            "sentiment": sentiment,
        },
        "sources": ["Yahoo Finance", "Finnhub"],
    }
