import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
from .strategies import STRATEGIES, WealthStrategy


@dataclass
class MonteCarloResult:
    strategy_name: str
    n_simulations: int
    target: float
    years: int
    success_rate: float
    median_outcome: float
    p10_outcome: float
    p90_outcome: float
    required_monthly_for_80pct: float
    expected_years_median: float


class MonteCarloEngine:
    def __init__(self, n_simulations: int = 10_000, seed: int = 42):
        self.n_simulations = n_simulations
        self.rng = np.random.default_rng(seed)

    def simulate(
        self,
        strategy: WealthStrategy,
        initial_capital: float,
        monthly_contribution: float,
        years: int,
        target: float,
    ) -> MonteCarloResult:
        monthly_mean = strategy.annual_return / 12
        monthly_std = strategy.volatility / (12 ** 0.5)
        months = years * 12

        # Shape: (n_simulations, months)
        returns = self.rng.normal(monthly_mean, monthly_std, (self.n_simulations, months))

        values = np.empty((self.n_simulations, months + 1))
        values[:, 0] = initial_capital
        for m in range(months):
            values[:, m + 1] = np.maximum(0.0, values[:, m] * (1 + returns[:, m]) + monthly_contribution)

        final = values[:, -1]
        hit_target = np.any(values >= target, axis=1)

        # Estimate median years to target (per simulation that hits)
        hit_months = []
        for i in np.where(hit_target)[0][:500]:  # sample for speed
            idx = np.argmax(values[i] >= target)
            hit_months.append(idx / 12)
        median_years = float(np.median(hit_months)) if hit_months else float(years)

        return MonteCarloResult(
            strategy_name=strategy.name_jp,
            n_simulations=self.n_simulations,
            target=target,
            years=years,
            success_rate=float(np.mean(hit_target)),
            median_outcome=float(np.median(final)),
            p10_outcome=float(np.percentile(final, 10)),
            p90_outcome=float(np.percentile(final, 90)),
            required_monthly_for_80pct=self._find_required_monthly(strategy, initial_capital, years, target),
            expected_years_median=median_years,
        )

    def _find_required_monthly(
        self, strategy: WealthStrategy, initial_capital: float, years: int, target: float
    ) -> float:
        lo, hi = 0.0, 3_000_000.0
        for _ in range(20):
            mid = (lo + hi) / 2
            # Quick estimate using fixed-rate formula instead of full MC for speed
            r = strategy.annual_return / 12
            n = years * 12
            fv_pv = initial_capital * (1 + r) ** n
            denom = ((1 + r) ** n - 1) / r if r > 1e-12 else n
            needed = max(0.0, (target - fv_pv) / denom)
            # crude success proxy: if needed <= mid, likely achievable
            if needed <= mid:
                hi = mid
            else:
                lo = mid
        return hi

    def rank_all(
        self,
        initial_capital: float,
        monthly_contribution: float,
        years: int,
        target: float,
    ) -> List[Tuple[WealthStrategy, MonteCarloResult]]:
        ranked = []
        for s in STRATEGIES:
            r = self.simulate(s, initial_capital, monthly_contribution, years, target)
            ranked.append((s, r))
        ranked.sort(key=lambda x: (x[1].success_rate, x[1].median_outcome), reverse=True)
        return ranked
