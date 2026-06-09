from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SimulationResult:
    years_to_target: Optional[int]
    final_value: float
    year_by_year: list = field(default_factory=list)
    total_contributed: float = 0.0
    total_growth: float = 0.0


class CompoundGrowthSimulator:
    def __init__(
        self,
        initial_capital: float,
        annual_return_rate: float,
        monthly_contribution: float = 0.0,
    ):
        self.initial_capital = initial_capital
        self.annual_return_rate = annual_return_rate
        self.monthly_contribution = monthly_contribution

    def simulate(self, years: int = 40, target: Optional[float] = None) -> SimulationResult:
        r = self.annual_return_rate / 12
        value = self.initial_capital
        year_by_year = [(0, value)]
        years_to_target: Optional[int] = None
        total_contributed = self.initial_capital

        for month in range(1, years * 12 + 1):
            value = value * (1 + r) + self.monthly_contribution
            total_contributed += self.monthly_contribution
            if month % 12 == 0:
                yr = month // 12
                year_by_year.append((yr, value))
                if target and years_to_target is None and value >= target:
                    years_to_target = yr

        return SimulationResult(
            years_to_target=years_to_target,
            final_value=value,
            year_by_year=year_by_year,
            total_contributed=total_contributed,
            total_growth=value - total_contributed,
        )

    def required_monthly_contribution(self, target: float, years: int) -> float:
        """Return monthly contribution needed to hit target in exactly `years`."""
        r = self.annual_return_rate / 12
        n = years * 12
        fv_of_pv = self.initial_capital * (1 + r) ** n
        denominator = ((1 + r) ** n - 1) / r if abs(r) > 1e-12 else n
        pmt = (target - fv_of_pv) / denominator
        return max(0.0, pmt)

    def years_to_target_no_contrib(self, target: float, max_years: int = 100) -> Optional[int]:
        if self.initial_capital <= 0:
            return None
        import math
        r = self.annual_return_rate
        if r <= 0:
            return None
        try:
            n = math.log(target / self.initial_capital) / math.log(1 + r)
            return int(math.ceil(n)) if n <= max_years else None
        except (ValueError, ZeroDivisionError):
            return None
