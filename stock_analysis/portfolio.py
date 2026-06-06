import json
import os
from datetime import datetime
from typing import Optional
import pandas as pd


PORTFOLIO_FILE = os.path.expanduser("~/.stock_portfolio.json")


class Portfolio:
    def __init__(self, filepath: str = PORTFOLIO_FILE):
        self.filepath = filepath
        self.holdings = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.holdings, f, ensure_ascii=False, indent=2)

    def add(self, ticker: str, shares: float, buy_price: float, note: str = ""):
        ticker = ticker.upper()
        entry = {
            "shares": shares,
            "buy_price": buy_price,
            "buy_date": datetime.now().strftime("%Y-%m-%d"),
            "note": note,
        }
        if ticker in self.holdings:
            existing = self.holdings[ticker]
            total_shares = existing["shares"] + shares
            avg_price = (
                existing["shares"] * existing["buy_price"] + shares * buy_price
            ) / total_shares
            self.holdings[ticker] = {
                "shares": total_shares,
                "buy_price": round(avg_price, 4),
                "buy_date": existing["buy_date"],
                "note": note or existing.get("note", ""),
            }
        else:
            self.holdings[ticker] = entry
        self._save()

    def remove(self, ticker: str):
        ticker = ticker.upper()
        if ticker in self.holdings:
            del self.holdings[ticker]
            self._save()
            return True
        return False

    def get_summary(self, current_prices: dict) -> list[dict]:
        rows = []
        for ticker, data in self.holdings.items():
            current = current_prices.get(ticker)
            if current is None:
                continue
            shares = data["shares"]
            buy_price = data["buy_price"]
            cost = shares * buy_price
            value = shares * current
            pnl = value - cost
            pnl_pct = (pnl / cost) * 100 if cost > 0 else 0
            rows.append(
                {
                    "ticker": ticker,
                    "shares": shares,
                    "buy_price": buy_price,
                    "current_price": current,
                    "cost": cost,
                    "value": value,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "note": data.get("note", ""),
                }
            )
        return rows

    def get_tickers(self) -> list[str]:
        return list(self.holdings.keys())

    def is_empty(self) -> bool:
        return len(self.holdings) == 0
