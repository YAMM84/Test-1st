from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class ScreenedAsset:
    ticker: str
    name: str
    score: int
    current_price: float
    currency: str
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    roe: Optional[float]
    dividend_yield: Optional[float]
    momentum_1y: Optional[float]
    technical_signal: str
    buy_reasons: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)


UNIVERSE: Dict[str, str] = {
    # Global ETFs
    "VT":    "全世界株式ETF (Vanguard)",
    "VTI":   "米国全株式ETF (Vanguard)",
    "QQQ":   "NASDAQ100 ETF",
    "VYM":   "米国高配当ETF",
    "VNQ":   "米国REIT ETF",
    # US Mega-cap
    "AAPL":  "Apple",
    "MSFT":  "Microsoft",
    "NVDA":  "NVIDIA",
    "AMZN":  "Amazon",
    "META":  "Meta Platforms",
    "GOOGL": "Alphabet",
    "BRK-B": "Berkshire Hathaway",
    "JPM":   "JPMorgan Chase",
    "V":     "Visa",
    # Japan
    "7203.T": "トヨタ自動車",
    "6758.T": "ソニーグループ",
    "8306.T": "三菱UFJ FG",
    "6861.T": "キーエンス",
    "4063.T": "信越化学工業",
    "9432.T": "NTT",
}


class StockScreener:
    def __init__(self, top_n: int = 10):
        self.top_n = top_n

    def run(self, progress_callback=None) -> List[ScreenedAsset]:
        import yfinance as yf
        import sys, os, warnings
        results = []

        for i, (ticker, name) in enumerate(UNIVERSE.items()):
            if progress_callback:
                progress_callback(ticker, i + 1, len(UNIVERSE))
            try:
                devnull = open(os.devnull, "w")
                old_stderr = sys.stderr
                sys.stderr = devnull
                try:
                    t = yf.Ticker(ticker)
                    info = t.info
                finally:
                    sys.stderr = old_stderr
                    devnull.close()
                hist = t.history(period="1y")
                if hist.empty or len(hist) < 20:
                    continue

                current = float(hist["Close"].iloc[-1])
                currency = info.get("currency", "USD")
                start_price = float(hist["Close"].iloc[0])
                momentum = (current - start_price) / start_price if start_price > 0 else None

                pe = info.get("trailingPE") or info.get("forwardPE")
                pb = info.get("priceToBook")
                roe = info.get("returnOnEquity")
                div_yield = info.get("dividendYield") or 0.0
                profit_margin = info.get("profitMargins")
                revenue_growth = info.get("revenueGrowth")

                tech_signal = self._technical_signal(hist)
                score, buy_reasons, risk_flags = self._score(
                    pe, pb, roe, div_yield, momentum, profit_margin, revenue_growth, tech_signal
                )

                results.append(ScreenedAsset(
                    ticker=ticker,
                    name=name,
                    score=score,
                    current_price=current,
                    currency=currency,
                    pe_ratio=round(pe, 1) if pe else None,
                    pb_ratio=round(pb, 2) if pb else None,
                    roe=round(roe * 100, 1) if roe else None,
                    dividend_yield=round(div_yield * 100, 2),
                    momentum_1y=round(momentum * 100, 1) if momentum is not None else None,
                    technical_signal=tech_signal,
                    buy_reasons=buy_reasons,
                    risk_flags=risk_flags,
                ))
            except Exception:
                continue

        results.sort(key=lambda x: x.score, reverse=True)
        return results[: self.top_n]

    def _technical_signal(self, hist) -> str:
        close = hist["Close"]
        if len(close) < 50:
            return "データ不足"
        sma20 = float(close.rolling(20).mean().iloc[-1])
        sma50 = float(close.rolling(50).mean().iloc[-1])
        current = float(close.iloc[-1])
        if current > sma20 > sma50:
            return "強い上昇"
        if current > sma50:
            return "上昇"
        if current < sma20 < sma50:
            return "強い下降"
        return "中立"

    def _score(self, pe, pb, roe, div_yield, momentum, profit_margin, revenue_growth, tech_signal):
        score = 50
        buy_reasons = []
        risk_flags = []

        if pe:
            if 8 < pe < 20:
                score += 15
                buy_reasons.append(f"割安PER {pe:.1f}x (8〜20の範囲)")
            elif 20 <= pe < 35:
                score += 5
            elif pe > 60:
                score -= 15
                risk_flags.append(f"高PER {pe:.0f}x (割高リスク)")

        if pb:
            if pb < 1.5:
                score += 12
                buy_reasons.append(f"低PBR {pb:.2f}x (解散価値以下)")
            elif pb < 3:
                score += 6

        if roe:
            if roe > 0.20:
                score += 15
                buy_reasons.append(f"高ROE {roe*100:.1f}% (優良企業の証拠)")
            elif roe > 0.12:
                score += 8
            elif roe < 0:
                score -= 15
                risk_flags.append("ROEがマイナス (赤字)")

        if div_yield:
            if div_yield > 0.03:
                score += 10
                buy_reasons.append(f"高配当 {div_yield*100:.1f}%")
            elif div_yield > 0.01:
                score += 4

        if momentum is not None:
            if momentum > 0.30:
                score += 15
                buy_reasons.append(f"強モメンタム +{momentum*100:.0f}% (1年)")
            elif momentum > 0.10:
                score += 8
            elif momentum < -0.20:
                score -= 12
                risk_flags.append(f"下落トレンド {momentum*100:.0f}% (1年)")

        if profit_margin and profit_margin > 0.15:
            score += 10
            buy_reasons.append(f"高利益率 {profit_margin*100:.0f}%")

        if revenue_growth and revenue_growth > 0.10:
            score += 8
            buy_reasons.append(f"増収成長 +{revenue_growth*100:.0f}%")

        tech_bonus = {"強い上昇": 10, "上昇": 5, "中立": 0, "強い下降": -10, "下降": -5, "データ不足": 0}
        score += tech_bonus.get(tech_signal, 0)

        return min(100, max(0, score)), buy_reasons, risk_flags
