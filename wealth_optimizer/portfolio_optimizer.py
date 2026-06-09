import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class OptimizedPortfolio:
    tickers: List[str]
    names: List[str]
    weights: np.ndarray
    expected_annual_return: float
    expected_volatility: float
    sharpe_ratio: float
    data_period: str
    optimization_type: str


CANDIDATE_UNIVERSE: Dict[str, str] = {
    "VT":    "全世界株式ETF",
    "VTI":   "米国全株式ETF",
    "QQQ":   "NASDAQ100ETF",
    "VYM":   "米国高配当ETF",
    "VNQ":   "米国REIT ETF",
    "BND":   "米国債券ETF",
    "GLD":   "金ETF",
    "AAPL":  "Apple",
    "MSFT":  "Microsoft",
    "NVDA":  "NVIDIA",
    "AMZN":  "Amazon",
    "GOOGL": "Alphabet",
    "BRK-B": "Berkshire Hathaway",
    "JPM":   "JPMorgan Chase",
    "7203.T": "トヨタ自動車",
    "6758.T": "ソニーグループ",
    "8306.T": "三菱UFJ FG",
    "6861.T": "キーエンス",
}

FALLBACK_ASSETS = ["VT", "VTI", "QQQ", "VYM", "BND", "GLD"]


class EfficientFrontierOptimizer:
    def __init__(self, tickers: Optional[List[str]] = None, period: str = "3y"):
        self.tickers = tickers or list(CANDIDATE_UNIVERSE.keys())
        self.period = period
        self._mean_returns: Optional[np.ndarray] = None
        self._cov_matrix: Optional[np.ndarray] = None
        self._valid_tickers: List[str] = []

    def fetch_and_prepare(self) -> bool:
        try:
            import yfinance as yf
            import warnings
            import sys
            import os
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # Suppress yfinance stderr noise
                devnull = open(os.devnull, "w")
                old_stderr = sys.stderr
                sys.stderr = devnull
                try:
                    raw = yf.download(self.tickers, period=self.period, progress=False, auto_adjust=True)
                finally:
                    sys.stderr = old_stderr
                    devnull.close()

            if raw.empty:
                return self._use_fallback()

            # Handle MultiIndex columns from yf.download
            if hasattr(raw.columns, "levels"):
                close = raw["Close"] if "Close" in raw.columns.get_level_values(0) else raw
            else:
                close = raw

            close = close.dropna(axis=1, thresh=int(len(close) * 0.7))
            if close.shape[1] < 3:
                return self._use_fallback()

            rets = close.pct_change().dropna()
            self._valid_tickers = list(rets.columns)
            self._mean_returns = np.array(rets.mean() * 252)
            self._cov_matrix = np.array(rets.cov() * 252)
            return True
        except Exception:
            return self._use_fallback()

    def _use_fallback(self) -> bool:
        """Pre-computed approximate annual statistics when network is unavailable."""
        assets = FALLBACK_ASSETS
        means = np.array([0.09, 0.10, 0.15, 0.08, 0.03, 0.05])
        corr = np.array([
            [1.00, 0.95, 0.85, 0.80, 0.05, 0.10],
            [0.95, 1.00, 0.88, 0.82, 0.05, 0.08],
            [0.85, 0.88, 1.00, 0.70, 0.00, 0.05],
            [0.80, 0.82, 0.70, 1.00, 0.10, 0.08],
            [0.05, 0.05, 0.00, 0.10, 1.00, 0.05],
            [0.10, 0.08, 0.05, 0.08, 0.05, 1.00],
        ])
        vols = np.array([0.15, 0.16, 0.22, 0.14, 0.05, 0.14])
        cov = corr * np.outer(vols, vols)
        self._valid_tickers = assets
        self._mean_returns = means
        self._cov_matrix = cov
        return True

    def _portfolio_stats(self, weights: np.ndarray):
        ret = float(np.dot(weights, self._mean_returns))
        vol = float(np.sqrt(weights @ self._cov_matrix @ weights))
        sharpe = (ret - 0.001) / vol if vol > 1e-9 else 0.0
        return ret, vol, sharpe

    def maximize_sharpe(self) -> OptimizedPortfolio:
        from scipy.optimize import minimize
        n = len(self._valid_tickers)
        rng = np.random.default_rng(0)
        best_w, best_s = np.ones(n) / n, -np.inf

        def neg_sharpe(w):
            _, _, s = self._portfolio_stats(w)
            return -s

        bounds = [(0.02, 0.45)] * n
        constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1}]

        for _ in range(60):
            w0 = rng.dirichlet(np.ones(n))
            res = minimize(neg_sharpe, w0, method="SLSQP", bounds=bounds, constraints=constraints,
                           options={"ftol": 1e-9, "maxiter": 500})
            if res.success:
                _, _, s = self._portfolio_stats(res.x)
                if s > best_s:
                    best_s, best_w = s, res.x.copy()

        ret, vol, sharpe = self._portfolio_stats(best_w)
        return OptimizedPortfolio(
            tickers=self._valid_tickers,
            names=[CANDIDATE_UNIVERSE.get(t, t) for t in self._valid_tickers],
            weights=best_w,
            expected_annual_return=ret,
            expected_volatility=vol,
            sharpe_ratio=sharpe,
            data_period=self.period,
            optimization_type="シャープ比最大化",
        )

    def minimize_volatility(self) -> OptimizedPortfolio:
        from scipy.optimize import minimize
        n = len(self._valid_tickers)

        def vol_fn(w):
            return float(np.sqrt(w @ self._cov_matrix @ w))

        bounds = [(0.02, 0.45)] * n
        constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
        w0 = np.ones(n) / n
        res = minimize(vol_fn, w0, method="SLSQP", bounds=bounds, constraints=constraints)
        w = res.x if res.success else w0
        ret, vol, sharpe = self._portfolio_stats(w)
        return OptimizedPortfolio(
            tickers=self._valid_tickers,
            names=[CANDIDATE_UNIVERSE.get(t, t) for t in self._valid_tickers],
            weights=w,
            expected_annual_return=ret,
            expected_volatility=vol,
            sharpe_ratio=sharpe,
            data_period=self.period,
            optimization_type="最小分散",
        )
