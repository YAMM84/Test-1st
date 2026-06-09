from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Milestone:
    name: str
    target_jpy: float
    target_label: str
    phase: str
    years_estimate: str
    key_actions: List[str]
    mindset: str


MILESTONES = [
    Milestone(
        name="緊急資金の確保",
        target_jpy=1_000_000,
        target_label="100万円",
        phase="防御フェーズ",
        years_estimate="0〜2年",
        key_actions=[
            "生活費6ヶ月分を高金利普通預金/MMFに確保",
            "高利率クレジットカード負債を完済",
            "月収の20%以上を強制貯蓄に回す仕組みを作る",
            "固定費(サブスク・保険)を見直し月2〜3万円削減",
        ],
        mindset="投資の前に『守り』を固める。緊急資金なき投資は砂上の楼閣。",
    ),
    Milestone(
        name="投資元本の積み上げ",
        target_jpy=5_000_000,
        target_label="500万円",
        phase="基盤構築フェーズ",
        years_estimate="3〜7年",
        key_actions=[
            "NISA口座でインデックス積立を毎月自動化(月3〜10万円)",
            "iDeCoで老後資産形成+節税(所得控除)",
            "副業・スキルアップで年収+50〜100万円を目指す",
            "支出管理アプリで収支を可視化・最適化",
        ],
        mindset="複利の種まき期間。小さな額でも続けることが最重要。",
    ),
    Milestone(
        name="複利加速フェーズ開始",
        target_jpy=10_000_000,
        target_label="1,000万円",
        phase="加速フェーズ",
        years_estimate="5〜12年",
        key_actions=[
            "ポートフォリオの年間リターンが月収を超え始める",
            "高配当株・REITで不労所得の柱を構築",
            "副業収入を投資元本に全額回す",
            "節税対策を本格化(法人設立も検討)",
        ],
        mindset="1,000万円の壁を越えると複利の威力を実感できる転換点。",
    ),
    Milestone(
        name="準富裕層の壁を突破",
        target_jpy=30_000_000,
        target_label="3,000万円",
        phase="拡大フェーズ",
        years_estimate="8〜18年",
        key_actions=[
            "不動産投資を検討(自己資金30%+融資70%)",
            "ポートフォリオを本格的に分散(国際分散)",
            "収入の複数化(本業+副業+投資+配当+家賃)",
            "プライベートバンク・IFA活用を検討",
        ],
        mindset="収入源が3本柱以上になると富の加速度が増す。",
    ),
    Milestone(
        name="富裕層入り",
        target_jpy=50_000_000,
        target_label="5,000万円",
        phase="富裕層フェーズ",
        years_estimate="10〜22年",
        key_actions=[
            "年間配当・家賃収入200万円以上でFIRE射程圏内",
            "税務戦略を最適化(法人/持株会/海外口座)",
            "資産の守りを強化(生命保険・相続対策)",
            "レバレッジ戦略でさらなる加速",
        ],
        mindset="資産が仕事をするようになる。時間の自由が視野に入る。",
    ),
    Milestone(
        name="億万長者達成!",
        target_jpy=100_000_000,
        target_label="1億円",
        phase="億万長者フェーズ",
        years_estimate="12〜30年",
        key_actions=[
            "年間投資リターン500〜700万円超(7%で計算)",
            "FIRE完全達成・労働からの経済的自立",
            "慈善・エンジェル投資・次世代への資産承継",
            "ライフスタイル最適化(時間・場所・人間関係)",
        ],
        mindset="1億円は終点でなく新たなスタート。複利はここからさらに加速する。",
    ),
]


class BillionaireRoadmap:
    def __init__(self, current_assets: float = 0, monthly_savings: float = 0, annual_return: float = 0.07):
        self.current_assets = current_assets
        self.monthly_savings = monthly_savings
        self.annual_return = annual_return

    def get_milestones(self) -> List[Milestone]:
        return MILESTONES

    def estimate_next_milestone(self) -> Optional[Milestone]:
        for m in MILESTONES:
            if self.current_assets < m.target_jpy:
                return m
        return None

    def years_to_100m(self) -> Optional[int]:
        from .simulator import CompoundGrowthSimulator
        sim = CompoundGrowthSimulator(self.current_assets, self.annual_return, self.monthly_savings)
        result = sim.simulate(years=60, target=100_000_000)
        return result.years_to_target

    def get_motivational_stats(self) -> dict:
        from .simulator import CompoundGrowthSimulator
        sim = CompoundGrowthSimulator(self.current_assets, self.annual_return, self.monthly_savings)
        result_20 = sim.simulate(years=20)
        result_30 = sim.simulate(years=30)
        result_40 = sim.simulate(years=40)
        return {
            "20年後": result_20.final_value,
            "30年後": result_30.final_value,
            "40年後": result_40.final_value,
            "1億円達成まで": self.years_to_100m(),
        }
