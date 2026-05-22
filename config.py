import os
from dotenv import load_dotenv

load_dotenv()

# Finnhub API (free tier: 60 req/min)
FINNHUB_KEY = os.getenv("FINNHUB_KEY", "")
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

# Market indices Yahoo Finance tickers
INDICES = {
    "纳斯达克100": "^NDX",
    "标普500": "^GSPC",
    "道琼斯工业指数": "^DJI",
}

# News filtering
NEWS_COUNT = 10

# Static keywords for US stock market relevance scoring (case-insensitive)
MARKET_KEYWORDS = [
    "stock", "market", "nasdaq", "dow", "jones", "wall street",
    "NYSE", "IPO", "earnings", "revenue", "profit",
    "investor", "shares", "equity", "index", "ralli", "sell-off", "selloff",
    "sector", "tech stock", "big tech", "magnificent seven",
    "treasury", "yield", "bond", "inflation", "CPI", "PPI",
    "jobs report", "unemployment", "nonfarm", "ISM", "PMI",
    "GDP", "recession", "soft landing",
    "SPDR", "ETF", "VIX", "volatility",
    "retail sales", "consumer spending", "housing market",
    "manufacturing", "factory", "trade deficit",
    "oil price", "crude", "energy sector",
    "chip", "semiconductor", "NVIDIA", "Apple", "Microsoft",
    "Amazon", "Google", "Meta", "Tesla", "AI", "artificial intelligence",
    "blockchain", "crypto", "bitcoin",
]

# Report output
REPORT_OUTPUT_DIR = os.getenv("REPORT_OUTPUT_DIR", "./output")
CACHE_DIR = os.path.join(REPORT_OUTPUT_DIR, ".cache")
