from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


@dataclass
class Task:
    month: int
    date_label: str
    category: str       # SETUP / INVEST / TAX / REVIEW
    priority: str       # HIGH / MEDIUM / LOW
    action: str
    ticker: Optional[str] = None
    amount_jpy: float = 0.0
    note: str = ""


@dataclass
class ExecutionPlan:
    generated_date: date
    initial_capital: float
    monthly_budget: float
    target_jpy: float
    tasks: List[Task] = field(default_factory=list)
    summary: str = ""

    def by_month(self, n: int = 12) -> dict:
        result: dict = {}
        for t in self.tasks:
            if 0 <= t.month < n:
                result.setdefault(t.month, []).append(t)
        return result

    def month0_tasks(self) -> List[Task]:
        return [t for t in self.tasks if t.month == 0]


NISA_ANNUAL_LIMIT = 3_600_000
IDECO_MONTHLY_LIMIT_EMPLOYEE = 23_000
IDECO_MONTHLY_LIMIT_SELF = 68_000


class ExecutionPlanner:
    def __init__(
        self,
        initial_capital: float,
        monthly_budget: float,
        age: int,
        is_self_employed: bool = False,
        has_nisa: bool = False,
        has_ideco: bool = False,
        optimal_tickers: Optional[List[str]] = None,
        top_stocks: Optional[list] = None,
    ):
        self.capital = initial_capital
        self.budget = monthly_budget
        self.age = age
        self.is_self_employed = is_self_employed
        self.has_nisa = has_nisa
        self.has_ideco = has_ideco
        self.optimal_tickers = optimal_tickers or []
        self.top_stocks = top_stocks or []

    def generate(self, months: int = 12, target: float = 100_000_000) -> ExecutionPlan:
        plan = ExecutionPlan(
            generated_date=date.today(),
            initial_capital=self.capital,
            monthly_budget=self.budget,
            target_jpy=target,
        )

        self._add_setup_tasks(plan)
        self._add_monthly_invest_tasks(plan, months)
        self._add_quarterly_reviews(plan, months)
        self._add_tax_tasks(plan, months)

        plan.summary = self._build_summary()
        return plan

    def _add_setup_tasks(self, plan: ExecutionPlan):
        if not self.has_nisa:
            plan.tasks.append(Task(0, "今すぐ", "SETUP", "HIGH",
                "NISA口座を開設する",
                note="SBI証券 or 楽天証券を選択。つみたて投資枠+成長投資枠の両方を申請"))
        if not self.has_ideco and self.age < 65:
            plan.tasks.append(Task(0, "今すぐ", "SETUP", "HIGH",
                "iDeCo口座を開設する",
                note="掛金は全額所得控除→節税効果大。SBI証券かマネックス証券が低コスト"))
        plan.tasks.append(Task(0, "今すぐ", "SETUP", "HIGH",
            "毎月の固定費を洗い出し・削減する",
            note="格安SIM/保険見直し/サブスク解約で月2〜3万円削減目標"))
        plan.tasks.append(Task(0, "今すぐ", "SETUP", "MEDIUM",
            "家計簿アプリで支出を可視化する (マネーフォワードME推奨)",
            note="収支を把握することで投資余力が明確になる"))

    def _add_monthly_invest_tasks(self, plan: ExecutionPlan, months: int):
        ideco_max = IDECO_MONTHLY_LIMIT_SELF if self.is_self_employed else IDECO_MONTHLY_LIMIT_EMPLOYEE
        nisa_monthly = min(self.budget * 0.70, NISA_ANNUAL_LIMIT / 12)
        ideco_monthly = min(self.budget * 0.10, ideco_max) if self.age < 65 else 0.0
        remaining = max(0.0, self.budget - nisa_monthly - ideco_monthly)

        for m in range(months):
            d = date.today() + timedelta(days=m * 30)
            label = f"{d.year}年{d.month}月"

            # Core: NISA つみたて枠
            plan.tasks.append(Task(m, label, "INVEST", "HIGH",
                "【NISA つみたて枠】eMAXIS Slim 全世界株式(オルカン) 積立",
                ticker="0331418A", amount_jpy=nisa_monthly,
                note=f"毎月{nisa_monthly:,.0f}円 自動積立設定"))

            # iDeCo
            if ideco_monthly > 0:
                plan.tasks.append(Task(m, label, "INVEST", "HIGH",
                    "【iDeCo】eMAXIS Slim 米国株式(S&P500) 積立",
                    amount_jpy=ideco_monthly,
                    note=f"毎月{ideco_monthly:,.0f}円 所得控除あり"))

            # Remaining → top screened stocks or optimal ETFs
            if remaining > 5_000:
                candidates = self.top_stocks[:3] if self.top_stocks else []
                if candidates:
                    per_stock = remaining / len(candidates)
                    for stk in candidates:
                        plan.tasks.append(Task(m, label, "INVEST", "MEDIUM",
                            f"【特定口座】{stk.name} ({stk.ticker}) 購入",
                            ticker=stk.ticker, amount_jpy=per_stock,
                            note=f"スクリーニングスコア: {stk.score}/100"))
                elif self.optimal_tickers:
                    per_etf = remaining / min(3, len(self.optimal_tickers))
                    for tkr in self.optimal_tickers[:3]:
                        plan.tasks.append(Task(m, label, "INVEST", "MEDIUM",
                            f"【特定口座】{tkr} ETF 購入",
                            ticker=tkr, amount_jpy=per_etf))

    def _add_quarterly_reviews(self, plan: ExecutionPlan, months: int):
        for m in range(3, months, 3):
            d = date.today() + timedelta(days=m * 30)
            label = f"{d.year}年{d.month}月"
            plan.tasks.append(Task(m, label, "REVIEW", "MEDIUM",
                "四半期レビュー: ポートフォリオ確認・リバランス判断",
                note="各資産クラスのウェイトが±5%ずれたらリバランス実施"))

    def _add_tax_tasks(self, plan: ExecutionPlan, months: int):
        dec_month = next((m for m in range(months) if (date.today() + timedelta(days=m * 30)).month == 12), None)
        if dec_month is not None:
            d = date.today() + timedelta(days=dec_month * 30)
            label = f"{d.year}年{d.month}月"
            plan.tasks.append(Task(dec_month, label, "TAX", "HIGH",
                "損益通算: 含み損銘柄を売却し課税利益を圧縮",
                note="特定口座内で利益と損失を相殺して納税額を削減"))
            plan.tasks.append(Task(dec_month, label, "TAX", "HIGH",
                "NISA年間投資枠の残り消化を確認",
                note="枠の繰り越し不可。12月末までに満額利用を目標"))
            plan.tasks.append(Task(dec_month, label, "TAX", "MEDIUM",
                "ふるさと納税の上限額を確認・実行 (還元率約30%相当)",
                note="給与所得等に応じた上限額をシミュレーターで確認後に寄付"))

    def _build_summary(self) -> str:
        nisa_monthly = min(self.budget * 0.70, NISA_ANNUAL_LIMIT / 12)
        ideco_max = IDECO_MONTHLY_LIMIT_SELF if self.is_self_employed else IDECO_MONTHLY_LIMIT_EMPLOYEE
        ideco_monthly = min(self.budget * 0.10, ideco_max) if self.age < 65 else 0.0
        remaining = max(0.0, self.budget - nisa_monthly - ideco_monthly)
        return (
            f"月次投資総額 {self.budget:,.0f}円: "
            f"NISA {nisa_monthly:,.0f}円 / iDeCo {ideco_monthly:,.0f}円 / 特定口座 {remaining:,.0f}円"
        )
