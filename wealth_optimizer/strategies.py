from dataclasses import dataclass
from typing import List


@dataclass
class WealthStrategy:
    name: str
    name_jp: str
    annual_return: float       # expected annual return (decimal)
    volatility: float          # std dev (decimal)
    required_capital: float    # minimum starting capital (JPY)
    monthly_effort: int        # effort hours per month
    time_horizon_min: int      # minimum recommended years
    description: str
    pros: List[str]
    cons: List[str]
    action_steps: List[str]


STRATEGIES: List[WealthStrategy] = [
    WealthStrategy(
        name="Global Index Funds",
        name_jp="全世界インデックス投資",
        annual_return=0.07,
        volatility=0.15,
        required_capital=1_000,
        monthly_effort=2,
        time_horizon_min=10,
        description="全世界株式インデックスファンド(オルカン等)への長期積立投資",
        pros=[
            "超低コスト・低手間で市場平均リターンを確保",
            "分散効果で個別銘柄リスクを排除",
            "NISA枠を最大活用で税メリット大",
            "月数千円から始められる",
        ],
        cons=[
            "市場暴落時に-30%以上の含み損も発生",
            "億万長者到達まで20〜30年かかる",
            "超過リターン(α)は期待できない",
        ],
        action_steps=[
            "証券口座(SBI/楽天/松井)を開設しNISA口座を設定",
            "eMAXIS Slim全世界株式またはSBI・V・全世界株式を選択",
            "毎月の積立額を設定(NISA枠上限:年360万円)",
            "ポートフォリオを年1回リバランス",
        ],
    ),
    WealthStrategy(
        name="Dividend Growth Stocks",
        name_jp="高配当・連続増配株投資",
        annual_return=0.09,
        volatility=0.18,
        required_capital=500_000,
        monthly_effort=8,
        time_horizon_min=10,
        description="配当再投資により複利を最大化する個別株・ETF戦略",
        pros=[
            "配当収入が雪だるま式に増加",
            "インフレヘッジ効果",
            "不労所得化でFIRE達成への近道",
            "市場平均を上回るリターンの可能性",
        ],
        cons=[
            "個別銘柄リスクあり・銘柄選択に調査が必要",
            "減配・無配リスク",
            "インデックスより管理コストが高い",
        ],
        action_steps=[
            "VYM/HDV/SPYD等の高配当ETFで基盤を構築",
            "日本株:花王・三菱UFJ・NTT等の連続増配銘柄を調査",
            "配当は必ず再投資(DRIP設定)",
            "配当利回り3%以上・増配率5%以上を選別基準に",
        ],
    ),
    WealthStrategy(
        name="US Growth Tech Stocks",
        name_jp="米国成長株集中投資",
        annual_return=0.15,
        volatility=0.35,
        required_capital=1_000_000,
        monthly_effort=20,
        time_horizon_min=5,
        description="GAFAM・AI・半導体等の成長セクターへの集中投資",
        pros=[
            "高リターンの可能性(年15%超)",
            "テクノロジー革命の恩恵を直接享受",
            "少額でも大きなリターン獲得のチャンス",
        ],
        cons=[
            "高ボラティリティ(-50%以上の暴落も)",
            "銘柄選択・タイミングの高度なスキルが必要",
            "集中リスクが高い",
            "精神的負担が大きい",
        ],
        action_steps=[
            "NVIDIA/Apple/Microsoft/Amazon等のコア銘柄を選定",
            "QQQ/VGTでセクターETFとして保有も検討",
            "ポジションサイズを管理(1銘柄20%以上にしない)",
            "四半期決算を必ずチェック",
        ],
    ),
    WealthStrategy(
        name="Real Estate Investment",
        name_jp="不動産投資(ワンルームマンション/アパート)",
        annual_return=0.06,
        volatility=0.08,
        required_capital=5_000_000,
        monthly_effort=15,
        time_horizon_min=15,
        description="レバレッジを活用した不動産賃貸収入と資産形成",
        pros=[
            "レバレッジで少ない自己資金を増幅",
            "安定したキャッシュフロー",
            "インフレ耐性・実物資産",
            "節税効果(減価償却)",
        ],
        cons=[
            "初期費用・融資審査のハードルが高い",
            "空室・修繕リスク",
            "流動性が低い(すぐ売れない)",
            "管理の手間",
        ],
        action_steps=[
            "自己資金500万円〜を準備",
            "利回り7%以上の物件を厳選(表面利回りでなく実質利回り)",
            "銀行融資を活用(自己資金30%+融資70%が目安)",
            "管理会社に委託して手間を最小化",
        ],
    ),
    WealthStrategy(
        name="Side Business / Startup",
        name_jp="副業・起業(スモールビジネス)",
        annual_return=0.25,
        volatility=0.60,
        required_capital=100_000,
        monthly_effort=60,
        time_horizon_min=3,
        description="ITスキル・専門知識を活かした副業・スモールビジネスの立ち上げ",
        pros=[
            "最大リターンの可能性",
            "スキルアップと資産形成が同時に進む",
            "少額でも始められる(SaaS/コンテンツ/コンサル)",
            "本業収入と並行可能",
        ],
        cons=[
            "時間投資が最も大きい",
            "失敗リスクが高い",
            "収入が不安定",
        ],
        action_steps=[
            "自分のスキルを棚卸し(IT/デザイン/ライティング/専門知識)",
            "クラウドワークス/Upwork等で副業スタート",
            "月10万円の副業収入を最初の目標に",
            "収益が安定したら法人化・スケールを検討",
        ],
    ),
    WealthStrategy(
        name="Crypto (BTC/ETH Core)",
        name_jp="仮想通貨(BTC/ETH長期保有)",
        annual_return=0.20,
        volatility=0.80,
        required_capital=10_000,
        monthly_effort=5,
        time_horizon_min=5,
        description="ビットコイン・イーサリアムを中心としたドルコスト平均法での長期積立",
        pros=[
            "過去実績で最高リターンのアセットクラス",
            "少額(数千円)から始められる",
            "24時間取引・流動性高い",
        ],
        cons=[
            "超高ボラティリティ(-80%以上の暴落も)",
            "規制リスク",
            "税制が不利(雑所得・最大55%課税)",
            "詐欺・ハッキングリスク",
        ],
        action_steps=[
            "コインチェック/bitFlyerで口座開設",
            "資産の5〜10%以内の上限で保有",
            "ドルコスト平均法で月定額積立",
            "コールドウォレット(Ledger等)で自己管理",
        ],
    ),
]


class StrategyAnalyzer:
    def __init__(self, strategies: List[WealthStrategy] = None):
        self.strategies = strategies or STRATEGIES

    def rank_by_return(self) -> List[WealthStrategy]:
        return sorted(self.strategies, key=lambda s: s.annual_return, reverse=True)

    def rank_by_sharpe(self) -> List[WealthStrategy]:
        rf = 0.001  # risk-free rate (0.1%)
        return sorted(
            self.strategies,
            key=lambda s: (s.annual_return - rf) / s.volatility if s.volatility > 0 else 0,
            reverse=True,
        )

    def get_sharpe(self, strategy: WealthStrategy) -> float:
        rf = 0.001
        return (strategy.annual_return - rf) / strategy.volatility if strategy.volatility > 0 else 0

    def get_score(self, strategy: WealthStrategy) -> int:
        """Composite score 0-10: weighted return, sharpe, effort (inverse), accessibility."""
        return_score = min(10, strategy.annual_return * 40)
        sharpe_score = min(10, self.get_sharpe(strategy) * 3)
        effort_score = max(0, 10 - strategy.monthly_effort / 10)
        access_score = max(0, 10 - (strategy.required_capital / 1_000_000))
        return round((return_score * 0.35 + sharpe_score * 0.30 + effort_score * 0.20 + access_score * 0.15))
