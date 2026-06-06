import pandas as pd
from typing import Optional


class FundamentalAnalysis:
    def __init__(self, info: dict):
        self.info = info
        currency = info.get("currency", "USD")
        self._currency_symbol = "¥" if currency in ("JPY", "CNY") else "€" if currency == "EUR" else "$"

    def _get(self, key: str, default=None):
        val = self.info.get(key, default)
        return val if val is not None else default

    def get_valuation(self) -> dict:
        return {
            "時価総額": self._format_large_number(self._get("marketCap")),
            "PER (株価収益率)": self._round(self._get("trailingPE")),
            "予想PER": self._round(self._get("forwardPE")),
            "PBR (株価純資産倍率)": self._round(self._get("priceToBook")),
            "EV/EBITDA": self._round(self._get("enterpriseToEbitda")),
            "EV/売上": self._round(self._get("enterpriseToRevenue")),
            "PSR (株価売上高倍率)": self._round(self._get("priceToSalesTrailing12Months")),
        }

    def get_profitability(self) -> dict:
        return {
            "売上高": self._format_large_number(self._get("totalRevenue")),
            "粗利益率": self._to_percent(self._get("grossMargins")),
            "営業利益率": self._to_percent(self._get("operatingMargins")),
            "純利益率": self._to_percent(self._get("profitMargins")),
            "ROE (自己資本利益率)": self._to_percent(self._get("returnOnEquity")),
            "ROA (総資産利益率)": self._to_percent(self._get("returnOnAssets")),
            "EPS (1株利益)": self._round(self._get("trailingEps")),
            "予想EPS": self._round(self._get("forwardEps")),
        }

    def get_growth(self) -> dict:
        return {
            "売上高成長率 (前年比)": self._to_percent(self._get("revenueGrowth")),
            "利益成長率 (前年比)": self._to_percent(self._get("earningsGrowth")),
            "EPS成長率 (5年予想)": self._to_percent(self._get("earningsQuarterlyGrowth")),
        }

    def get_financial_health(self) -> dict:
        return {
            "自己資本比率": self._calc_equity_ratio(),
            "流動比率": self._round(self._get("currentRatio")),
            "負債比率 (D/E)": self._round(self._get("debtToEquity")),
            "現金及び現金同等物": self._format_large_number(self._get("totalCash")),
            "総負債": self._format_large_number(self._get("totalDebt")),
            "フリーキャッシュフロー": self._format_large_number(self._get("freeCashflow")),
        }

    def get_dividend(self) -> dict:
        return {
            "配当利回り": self._to_percent(self._get("dividendYield")),
            "1株配当": self._round(self._get("dividendRate")),
            "配当性向": self._to_percent(self._get("payoutRatio")),
            "5年平均配当成長率": self._to_percent(self._get("fiveYearAvgDividendYield")),
        }

    def get_overview(self) -> dict:
        return {
            "銘柄名": self._get("longName") or self._get("shortName", "N/A"),
            "ティッカー": self._get("symbol", "N/A"),
            "セクター": self._get("sector", "N/A"),
            "業種": self._get("industry", "N/A"),
            "国": self._get("country", "N/A"),
            "取引所": self._get("exchange", "N/A"),
            "通貨": self._get("currency", "N/A"),
            "従業員数": self._format_employees(self._get("fullTimeEmployees")),
            "52週高値": self._round(self._get("fiftyTwoWeekHigh")),
            "52週安値": self._round(self._get("fiftyTwoWeekLow")),
            "ベータ値": self._round(self._get("beta")),
        }

    def get_investment_rating(self) -> str:
        per = self._get("trailingPE")
        pbr = self._get("priceToBook")
        roe = self._get("returnOnEquity")
        profit_margin = self._get("profitMargins")
        debt_equity = self._get("debtToEquity")

        score = 0
        reasons = []

        if per is not None:
            if 0 < per < 15:
                score += 2
                reasons.append("PERが割安水準")
            elif 15 <= per <= 25:
                score += 1
                reasons.append("PERが適正水準")
            elif per > 40:
                score -= 1
                reasons.append("PERが割高水準")

        if pbr is not None:
            if 0 < pbr < 1.5:
                score += 2
                reasons.append("PBRが割安水準")
            elif 1.5 <= pbr <= 3:
                score += 1
                reasons.append("PBRが適正水準")

        if roe is not None:
            if roe > 0.15:
                score += 2
                reasons.append("ROEが高水準 (>15%)")
            elif roe > 0.08:
                score += 1
                reasons.append("ROEが良好水準 (>8%)")

        if profit_margin is not None:
            if profit_margin > 0.20:
                score += 1
                reasons.append("高い純利益率 (>20%)")
            elif profit_margin < 0:
                score -= 1
                reasons.append("赤字企業")

        if debt_equity is not None:
            if debt_equity < 0.5:
                score += 1
                reasons.append("低負債比率")
            elif debt_equity > 2.0:
                score -= 1
                reasons.append("高負債リスク")

        return score, reasons

    def _calc_equity_ratio(self) -> str:
        total_assets = self._get("totalAssets")
        total_debt = self._get("totalDebt")
        if total_assets and total_debt:
            equity = total_assets - total_debt
            ratio = equity / total_assets
            return f"{ratio:.1%}"
        return "N/A"

    def _round(self, val, decimals: int = 2):
        if val is None:
            return "N/A"
        try:
            return round(float(val), decimals)
        except (TypeError, ValueError):
            return "N/A"

    def _to_percent(self, val) -> str:
        if val is None:
            return "N/A"
        try:
            return f"{float(val):.2%}"
        except (TypeError, ValueError):
            return "N/A"

    def _format_large_number(self, val) -> str:
        if val is None:
            return "N/A"
        try:
            val = float(val)
            sym = self._currency_symbol
            if abs(val) >= 1e12:
                return f"{sym}{val/1e12:.2f}T"
            elif abs(val) >= 1e9:
                return f"{sym}{val/1e9:.2f}B"
            elif abs(val) >= 1e6:
                return f"{sym}{val/1e6:.2f}M"
            else:
                return f"{sym}{val:,.0f}"
        except (TypeError, ValueError):
            return "N/A"

    def _format_employees(self, val) -> str:
        if val is None:
            return "N/A"
        try:
            return f"{int(val):,}人"
        except (TypeError, ValueError):
            return "N/A"
