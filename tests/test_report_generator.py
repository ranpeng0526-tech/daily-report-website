import json

from models import MarketIndex, NewsSummary
from report import generator


def test_generate_report_writes_latest_json(tmp_path, monkeypatch):
    monkeypatch.setattr(generator, "REPORT_OUTPUT_DIR", str(tmp_path))

    indices = [
        MarketIndex(
            name="S&P 500",
            ticker="^GSPC",
            open=5000.0,
            close=5050.0,
            high=5060.0,
            low=4990.0,
            change_pct=1.0,
            change_5d=2.5,
            change_mtd=3.0,
            date="2026-05-20",
        )
    ]
    top_news = [
        NewsSummary(
            title="Markets rally",
            summary="Stocks rose after earnings.",
            impact="利好",
            reason="盈利预期改善",
        )
    ]

    markdown_path = generator.generate_report(indices, top_news, "2026-05-20")

    latest_json = tmp_path / "latest-report.json"
    assert markdown_path.endswith("2026-05-20-美股晨报.md")
    assert latest_json.exists()

    payload = json.loads(latest_json.read_text(encoding="utf-8"))
    assert payload["date"] == "2026-05-20"
    assert payload["title"] == "每日美股市场晨报"
    assert payload["indices"][0]["name"] == "S&P 500"
    assert payload["top_news"][0]["impact"] == "利好"
    assert payload["market_overview"]["advancers"] == 1
    assert payload["market_overview"]["decliners"] == 0
