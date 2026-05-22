from dataclasses import dataclass, field


@dataclass
class MarketIndex:
    name: str
    ticker: str
    open: float
    close: float
    high: float
    low: float
    change_pct: float
    change_5d: float = 0.0
    change_mtd: float = 0.0
    date: str = ""
    error: str = ""


@dataclass
class NewsArticle:
    title: str
    description: str
    url: str
    source: str
    published_at: str
    _score: int = field(default=0, repr=False)


@dataclass
class NewsSummary:
    title: str
    summary: str
    impact: str
    reason: str
