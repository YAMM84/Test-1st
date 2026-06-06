import pandas as pd
import numpy as np
from typing import Tuple


class TechnicalAnalysis:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.close = df["Close"]
        self.high = df["High"]
        self.low = df["Low"]
        self.volume = df["Volume"]

    def sma(self, window: int) -> pd.Series:
        return self.close.rolling(window=window).mean()

    def ema(self, window: int) -> pd.Series:
        return self.close.ewm(span=window, adjust=False).mean()

    def rsi(self, window: int = 14) -> pd.Series:
        delta = self.close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(com=window - 1, min_periods=window).mean()
        avg_loss = loss.ewm(com=window - 1, min_periods=window).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def macd(
        self, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        ema_fast = self.ema(fast)
        ema_slow = self.ema(slow)
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    def bollinger_bands(
        self, window: int = 20, num_std: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        middle = self.sma(window)
        std = self.close.rolling(window=window).std()
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)
        return upper, middle, lower

    def atr(self, window: int = 14) -> pd.Series:
        high_low = self.high - self.low
        high_close = (self.high - self.close.shift()).abs()
        low_close = (self.low - self.close.shift()).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=window).mean()

    def volume_sma(self, window: int = 20) -> pd.Series:
        return self.volume.rolling(window=window).mean()

    def get_signals(self) -> dict:
        current = self.close.iloc[-1]
        sma20 = self.sma(20).iloc[-1]
        sma50 = self.sma(50).iloc[-1]
        sma200 = self.sma(200).iloc[-1]
        rsi_val = self.rsi().iloc[-1]
        macd_line, signal_line, _ = self.macd()
        macd_val = macd_line.iloc[-1]
        signal_val = signal_line.iloc[-1]
        upper_bb, _, lower_bb = self.bollinger_bands()
        bb_upper = upper_bb.iloc[-1]
        bb_lower = lower_bb.iloc[-1]

        signals = {
            "price": current,
            "sma20": sma20,
            "sma50": sma50,
            "sma200": sma200,
            "rsi": rsi_val,
            "macd": macd_val,
            "macd_signal": signal_val,
            "bb_upper": bb_upper,
            "bb_lower": bb_lower,
            "trend": "上昇" if current > sma50 else "下降",
            "rsi_status": (
                "買われすぎ" if rsi_val > 70 else "売られすぎ" if rsi_val < 30 else "中立"
            ),
            "macd_crossover": "買いシグナル" if macd_val > signal_val else "売りシグナル",
            "golden_cross": sma20 > sma50,
            "death_cross": sma20 < sma50,
        }
        return signals

    def get_summary_score(self) -> Tuple[int, str]:
        signals = self.get_signals()
        score = 0

        if signals["price"] > signals["sma50"]:
            score += 1
        if signals["price"] > signals["sma200"]:
            score += 1
        if signals["golden_cross"]:
            score += 1
        if signals["rsi"] < 70 and signals["rsi"] > 40:
            score += 1
        if signals["macd_crossover"] == "買いシグナル":
            score += 1
        if signals["price"] < signals["bb_upper"]:
            score += 1

        if score >= 5:
            rating = "強い買い"
        elif score >= 4:
            rating = "買い"
        elif score >= 3:
            rating = "中立"
        elif score >= 2:
            rating = "売り"
        else:
            rating = "強い売り"

        return score, rating
