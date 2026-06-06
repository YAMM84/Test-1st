import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np
import os
from datetime import datetime

from .fetcher import StockFetcher
from .technical import TechnicalAnalysis
from .fundamental import FundamentalAnalysis


class ReportGenerator:
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.fetcher = StockFetcher(ticker)

    def generate_chart(self, period: str = "1y", output_dir: str = ".") -> str:
        df = self.fetcher.get_history(period=period)
        ta = TechnicalAnalysis(df)

        fig = plt.figure(figsize=(16, 12))
        fig.patch.set_facecolor("#0d1117")
        gs = gridspec.GridSpec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.05)

        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        ax3 = fig.add_subplot(gs[2], sharex=ax1)
        ax4 = fig.add_subplot(gs[3], sharex=ax1)

        for ax in [ax1, ax2, ax3, ax4]:
            ax.set_facecolor("#0d1117")
            ax.tick_params(colors="#8b949e")
            ax.spines["bottom"].set_color("#21262d")
            ax.spines["top"].set_color("#21262d")
            ax.spines["left"].set_color("#21262d")
            ax.spines["right"].set_color("#21262d")
            ax.yaxis.label.set_color("#8b949e")
            ax.xaxis.label.set_color("#8b949e")

        close = df["Close"]
        dates = df.index

        upper_bb, middle_bb, lower_bb = ta.bollinger_bands()
        sma20 = ta.sma(20)
        sma50 = ta.sma(50)

        ax1.plot(dates, close, color="#58a6ff", linewidth=1.5, label="Close", zorder=3)
        ax1.plot(dates, sma20, color="#f0883e", linewidth=1, linestyle="--", label="SMA20", alpha=0.8)
        ax1.plot(dates, sma50, color="#3fb950", linewidth=1, linestyle="--", label="SMA50", alpha=0.8)
        ax1.fill_between(dates, upper_bb, lower_bb, alpha=0.1, color="#58a6ff", label="Bollinger Bands")
        ax1.plot(dates, upper_bb, color="#58a6ff", linewidth=0.5, alpha=0.5)
        ax1.plot(dates, lower_bb, color="#58a6ff", linewidth=0.5, alpha=0.5)

        ax1.set_ylabel("Price", color="#8b949e")
        ax1.legend(loc="upper left", facecolor="#161b22", edgecolor="#21262d", labelcolor="#c9d1d9", fontsize=8)
        ax1.set_title(
            f"{self.ticker} Stock Chart ({period})",
            color="#c9d1d9",
            fontsize=14,
            pad=10,
        )

        colors = ["#3fb950" if c >= o else "#f85149"
                  for c, o in zip(df["Close"], df["Open"])]
        ax2.bar(dates, df["Volume"], color=colors, alpha=0.7)
        vol_ma = ta.volume_sma(20)
        ax2.plot(dates, vol_ma, color="#f0883e", linewidth=1)
        ax2.set_ylabel("Volume", color="#8b949e")

        rsi = ta.rsi()
        ax3.plot(dates, rsi, color="#d2a8ff", linewidth=1.2)
        ax3.axhline(70, color="#f85149", linestyle="--", linewidth=0.8, alpha=0.7)
        ax3.axhline(30, color="#3fb950", linestyle="--", linewidth=0.8, alpha=0.7)
        ax3.fill_between(dates, rsi, 70, where=(rsi > 70), alpha=0.2, color="#f85149")
        ax3.fill_between(dates, rsi, 30, where=(rsi < 30), alpha=0.2, color="#3fb950")
        ax3.set_ylim(0, 100)
        ax3.set_ylabel("RSI", color="#8b949e")
        ax3.set_yticks([30, 50, 70])

        macd_line, signal_line, histogram = ta.macd()
        ax4.bar(dates, histogram, color=["#3fb950" if v >= 0 else "#f85149" for v in histogram], alpha=0.7)
        ax4.plot(dates, macd_line, color="#58a6ff", linewidth=1, label="MACD")
        ax4.plot(dates, signal_line, color="#f0883e", linewidth=1, label="Signal")
        ax4.axhline(0, color="#8b949e", linewidth=0.5)
        ax4.set_ylabel("MACD", color="#8b949e")
        ax4.legend(loc="upper left", facecolor="#161b22", edgecolor="#21262d", labelcolor="#c9d1d9", fontsize=7)

        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)
        plt.setp(ax3.get_xticklabels(), visible=False)

        os.makedirs(output_dir, exist_ok=True)
        filename = f"{self.ticker}_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches="tight", facecolor="#0d1117")
        plt.close()
        return filepath
