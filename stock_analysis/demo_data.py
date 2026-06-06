import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_demo_history(ticker: str = "DEMO", days: int = 365) -> pd.DataFrame:
    np.random.seed(hash(ticker) % (2**32))
    dates = pd.date_range(end=datetime.now(), periods=days, freq="B")

    start_prices = {
        "AAPL": 170, "MSFT": 380, "GOOGL": 170, "TSLA": 200, "NVDA": 800,
        "AMZN": 185, "META": 490, "DEMO": 150,
    }
    base = start_prices.get(ticker.upper(), 100)

    returns = np.random.normal(0.0004, 0.015, days)
    prices = base * np.cumprod(1 + returns)

    high = prices * (1 + np.abs(np.random.normal(0, 0.008, days)))
    low = prices * (1 - np.abs(np.random.normal(0, 0.008, days)))
    open_prices = prices * (1 + np.random.normal(0, 0.005, days))
    volume = np.random.randint(20_000_000, 80_000_000, days).astype(float)

    df = pd.DataFrame({
        "Open": open_prices,
        "High": high,
        "Low": low,
        "Close": prices,
        "Volume": volume,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
    }, index=dates)
    return df


DEMO_INFO = {
    "AAPL": {
        "longName": "Apple Inc.",
        "symbol": "AAPL",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "country": "United States",
        "exchange": "NASDAQ",
        "currency": "USD",
        "currentPrice": 185.50,
        "marketCap": 2_850_000_000_000,
        "trailingPE": 28.5,
        "forwardPE": 26.2,
        "priceToBook": 45.3,
        "enterpriseToEbitda": 22.1,
        "enterpriseToRevenue": 7.2,
        "priceToSalesTrailing12Months": 7.5,
        "totalRevenue": 383_000_000_000,
        "grossMargins": 0.441,
        "operatingMargins": 0.298,
        "profitMargins": 0.253,
        "returnOnEquity": 1.471,
        "returnOnAssets": 0.224,
        "trailingEps": 6.43,
        "forwardEps": 7.10,
        "revenueGrowth": 0.025,
        "earningsGrowth": 0.131,
        "currentRatio": 1.07,
        "debtToEquity": 147.0,
        "totalCash": 73_100_000_000,
        "totalDebt": 111_100_000_000,
        "freeCashflow": 95_000_000_000,
        "dividendYield": 0.0052,
        "dividendRate": 0.96,
        "payoutRatio": 0.149,
        "fiftyTwoWeekHigh": 199.62,
        "fiftyTwoWeekLow": 164.08,
        "beta": 1.24,
        "fullTimeEmployees": 161_000,
    },
    "MSFT": {
        "longName": "Microsoft Corporation",
        "symbol": "MSFT",
        "sector": "Technology",
        "industry": "Software - Infrastructure",
        "country": "United States",
        "exchange": "NASDAQ",
        "currency": "USD",
        "currentPrice": 415.20,
        "marketCap": 3_080_000_000_000,
        "trailingPE": 35.8,
        "forwardPE": 31.5,
        "priceToBook": 12.8,
        "enterpriseToEbitda": 26.4,
        "enterpriseToRevenue": 12.3,
        "priceToSalesTrailing12Months": 12.1,
        "totalRevenue": 245_000_000_000,
        "grossMargins": 0.695,
        "operatingMargins": 0.452,
        "profitMargins": 0.358,
        "returnOnEquity": 0.388,
        "returnOnAssets": 0.175,
        "trailingEps": 11.45,
        "forwardEps": 13.20,
        "revenueGrowth": 0.155,
        "earningsGrowth": 0.103,
        "currentRatio": 1.77,
        "debtToEquity": 37.2,
        "totalCash": 80_000_000_000,
        "totalDebt": 79_000_000_000,
        "freeCashflow": 74_000_000_000,
        "dividendYield": 0.0072,
        "dividendRate": 3.0,
        "payoutRatio": 0.262,
        "fiftyTwoWeekHigh": 430.82,
        "fiftyTwoWeekLow": 309.45,
        "beta": 0.90,
        "fullTimeEmployees": 228_000,
    },
    "DEMO": {
        "longName": "Demo Corporation Inc.",
        "symbol": "DEMO",
        "sector": "Technology",
        "industry": "Software",
        "country": "Japan",
        "exchange": "TSE",
        "currency": "JPY",
        "currentPrice": 152.30,
        "marketCap": 5_000_000_000,
        "trailingPE": 18.5,
        "forwardPE": 15.2,
        "priceToBook": 2.3,
        "grossMargins": 0.55,
        "operatingMargins": 0.22,
        "profitMargins": 0.18,
        "returnOnEquity": 0.15,
        "returnOnAssets": 0.10,
        "trailingEps": 8.20,
        "forwardEps": 10.0,
        "revenueGrowth": 0.12,
        "currentRatio": 2.5,
        "debtToEquity": 30.0,
        "dividendYield": 0.025,
        "dividendRate": 3.8,
        "fiftyTwoWeekHigh": 175.0,
        "fiftyTwoWeekLow": 120.0,
        "beta": 1.1,
        "fullTimeEmployees": 5_000,
    },
}


def get_demo_info(ticker: str) -> dict:
    info = DEMO_INFO.get(ticker.upper(), DEMO_INFO["DEMO"]).copy()
    info["symbol"] = ticker.upper()
    return info
