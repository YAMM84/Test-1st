import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional


class StockFetcher:
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self._ticker_obj = yf.Ticker(self.ticker)

    def get_history(self, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        df = self._ticker_obj.history(period=period, interval=interval)
        if df.empty:
            raise ValueError(f"No data found for ticker '{self.ticker}'")
        return df

    def get_info(self) -> dict:
        info = self._ticker_obj.info
        if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
            raise ValueError(f"No info found for ticker '{self.ticker}'")
        return info

    def get_financials(self) -> pd.DataFrame:
        return self._ticker_obj.financials

    def get_balance_sheet(self) -> pd.DataFrame:
        return self._ticker_obj.balance_sheet

    def get_cashflow(self) -> pd.DataFrame:
        return self._ticker_obj.cashflow

    def get_dividends(self) -> pd.Series:
        return self._ticker_obj.dividends

    def get_current_price(self) -> float:
        info = self._ticker_obj.info
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        if price is None:
            history = self.get_history(period="5d")
            price = float(history["Close"].iloc[-1])
        return float(price)

    def get_company_name(self) -> str:
        info = self._ticker_obj.info
        return info.get("longName") or info.get("shortName") or self.ticker
