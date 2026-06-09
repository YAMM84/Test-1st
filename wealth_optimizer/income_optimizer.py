from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class IncomeStrategy:
    name: str
    category: str                  # CAREER / SIDE_HUSTLE / PASSIVE / PRODUCT
    physical_energy: int           # 1=最低限 〜 5=高体力 (体力消費)
    mental_stress: int             # 1=穏やか 〜 5=高ストレス
    time_flexibility: int          # 1=固定 〜 5=完全自由
    income_potential_monthly: int  # 達成可能な月収増加額 (円)
    startup_months: int            # 収入が出るまでの期間 (月)
    scalability: int               # 1=頭打ち 〜 5=指数的スケール
    remote_possible: bool
    description: str
    how_to_start: List[str]
    tools_needed: List[str]
    energy_note: str               # 体力がない人向けの具体的な注意点


ALL_STRATEGIES: List[IncomeStrategy] = [
    # ── CAREER ──────────────────────────────────────────────
    IncomeStrategy(
        name="ITスキルでリモート転職",
        category="CAREER",
        physical_energy=1,
        mental_stress=2,
        time_flexibility=3,
        income_potential_monthly=150_000,
        startup_months=3,
        scalability=3,
        remote_possible=True,
        description="プログラミング・データ分析・クラウドインフラのスキルを習得しフルリモート求人へ転職。体力不要で在宅完結。",
        how_to_start=[
            "Progateや独学大全でPython/SQL基礎を3ヶ月学ぶ",
            "ポートフォリオ(GitHub)を1〜2本作る",
            "Wantedly・Findy・転職ドラフトでリモート求人に絞って応募",
        ],
        tools_needed=["PC", "VSCode(無料)", "GitHub(無料)"],
        energy_note="在宅・自分のペースで作業可能。体力がなくてもデスクワークのみで完結。",
    ),
    IncomeStrategy(
        name="AIツール活用で業務効率化→昇給交渉",
        category="CAREER",
        physical_energy=1,
        mental_stress=1,
        time_flexibility=4,
        income_potential_monthly=50_000,
        startup_months=1,
        scalability=2,
        remote_possible=True,
        description="ChatGPT・Claude等を使って現在の業務を2〜3倍速化し、空いた時間で成果を出して昇給交渉する。最も即効性が高い。",
        how_to_start=[
            "現在の業務でAIに任せられるタスクをリストアップ",
            "ChatGPT/Claude Proに月3,000円投資して業務自動化",
            "削減した時間で付加価値業務に集中→実績を作り昇給交渉",
        ],
        tools_needed=["ChatGPT Pro(月3,000円)", "Claude Pro(月3,000円)"],
        energy_note="むしろ体力消費を減らしながら成果を上げる戦略。疲労度が下がることで継続しやすい。",
    ),
    # ── SIDE_HUSTLE ──────────────────────────────────────────
    IncomeStrategy(
        name="スキルシェア型フリーランス (IT・デザイン・ライティング)",
        category="SIDE_HUSTLE",
        physical_energy=1,
        mental_stress=2,
        time_flexibility=5,
        income_potential_monthly=100_000,
        startup_months=2,
        scalability=2,
        remote_possible=True,
        description="クラウドワークス・Lancers・Upworkで自分のスキルを時間制で販売。体調に合わせて仕事量を調整できる。",
        how_to_start=[
            "クラウドワークスに登録し得意分野で実績0→3件を目標に受注",
            "最初は安価でも実績を作ることを優先",
            "実績3件できたら単価を段階的に引き上げる",
        ],
        tools_needed=["PC", "各プラットフォーム(無料登録)"],
        energy_note="体調の良い時だけ働ける。締め切りを余裕あるものだけ選択可。週10〜15時間からスタート推奨。",
    ),
    IncomeStrategy(
        name="AIを使ったコンテンツ制作代行",
        category="SIDE_HUSTLE",
        physical_energy=1,
        mental_stress=1,
        time_flexibility=5,
        income_potential_monthly=80_000,
        startup_months=1,
        scalability=3,
        remote_possible=True,
        description="AI(ChatGPT/Claude)でブログ記事・SNS投稿・メルマガ・動画台本を作成し、中小企業に月額提供。体力消費ほぼゼロ。",
        how_to_start=[
            "ランサーズで『記事作成』カテゴリを見てニーズを把握",
            "AIで試作品3つ作りポートフォリオにする",
            "月額5〜10万円の継続契約を3社獲得することを目標",
        ],
        tools_needed=["ChatGPT/Claude Pro(月3,000〜6,000円)"],
        energy_note="AIが実作業の8割を担う。監修・編集だけなら1日1〜2時間で月5〜10万円も現実的。",
    ),
    IncomeStrategy(
        name="オンライン専門家コンサルティング",
        category="SIDE_HUSTLE",
        physical_energy=1,
        mental_stress=2,
        time_flexibility=4,
        income_potential_monthly=200_000,
        startup_months=3,
        scalability=2,
        remote_possible=True,
        description="自分の職歴・専門知識をオンラインで販売。ビザスク・コーチェックで1時間2〜5万円の相談対応。体力不要。",
        how_to_start=[
            "ビザスクに登録し自分の専門領域を3つ書く",
            "最初は1時間1万円で受けて実績を積む",
            "口コミが2〜3件たまったら単価を上げる",
        ],
        tools_needed=["Zoom(無料)", "ビザスク登録(無料)"],
        energy_note="1回1〜2時間の会話のみ。日程調整で体調の良い日だけ入れられる。移動ゼロ。",
    ),
    # ── PASSIVE / PRODUCT ────────────────────────────────────
    IncomeStrategy(
        name="デジタルコンテンツ販売 (note・Kindle・Udemy)",
        category="PRODUCT",
        physical_energy=1,
        mental_stress=1,
        time_flexibility=5,
        income_potential_monthly=50_000,
        startup_months=2,
        scalability=4,
        remote_possible=True,
        description="自分の知識・経験をPDF・電子書籍・オンライン講座として一度作り、繰り返し販売。完全ストック型収入。",
        how_to_start=[
            "noteで500〜1,000円の有料記事を5本書く(まず1万円稼ぐ)",
            "反応が良いテーマをKindle本またはUdemy講座に展開",
            "一度公開したら半永久的に収入が発生",
        ],
        tools_needed=["note(無料)", "Kindle Direct Publishing(無料)", "Canva(無料)"],
        energy_note="制作は自分のペースで分割して進められる。公開後は自動販売。体調が悪い日も収入が入る。",
    ),
    IncomeStrategy(
        name="YouTubeチャンネル (AI・テキスト読み上げ活用)",
        category="PRODUCT",
        physical_energy=1,
        mental_stress=1,
        time_flexibility=5,
        income_potential_monthly=100_000,
        startup_months=6,
        scalability=5,
        remote_possible=True,
        description="顔出し・声出し不要のスライド動画やAI音声解説チャンネル。投資・健康・雑学系は需要が高い。",
        how_to_start=[
            "CanvaでスライドをAI音声読み上げ(VOICEVOX等)で動画化",
            "週1〜2本ペース(体調に合わせて)で100本を目標に",
            "収益化(1,000人・4,000時間)まで約6〜12ヶ月",
        ],
        tools_needed=["Canva Pro(月1,500円)", "VOICEVOX(無料)"],
        energy_note="撮影・外出・体力消費ゼロ。寝転がりながらスライド作成も可能。蓄積型なので休んでも資産が残る。",
    ),
    IncomeStrategy(
        name="スモールSaaS / Webツール開発",
        category="PRODUCT",
        physical_energy=1,
        mental_stress=2,
        time_flexibility=5,
        income_potential_monthly=500_000,
        startup_months=6,
        scalability=5,
        remote_possible=True,
        description="月額課金の小さなWebサービスを作る。月5,000円×100人=月50万円。プログラミングスキルが必要だが最大リターン。",
        how_to_start=[
            "自分や周囲が困っている小さな問題を1つ特定",
            "Claude/ChatGPTにコード補助させながら最小版(MVP)を3ヶ月で作る",
            "最初は無料で10人に使ってもらいフィードバック収集",
            "月980〜2,980円のサブスクとして課金開始",
        ],
        tools_needed=["PC", "Vercel/Supabase(無料枠あり)", "Stripe(決済)"],
        energy_note="開発は細切れでも進められる。1日1〜2時間の作業でもコードは積み上がる。AIがコード補助するため技術ハードルも下がっている。",
    ),
]


def filter_by_energy(strategies: List[IncomeStrategy], max_physical: int = 2, max_stress: int = 3) -> List[IncomeStrategy]:
    return [s for s in strategies if s.physical_energy <= max_physical and s.mental_stress <= max_stress]


def rank_by_energy_efficiency(strategies: List[IncomeStrategy]) -> List[IncomeStrategy]:
    """収入ポテンシャル / (体力+ストレス) で効率スコアを計算してソート"""
    def score(s: IncomeStrategy) -> float:
        energy_cost = s.physical_energy + s.mental_stress
        income_score = s.income_potential_monthly / 10_000
        scalability_bonus = s.scalability * 0.5
        flexibility_bonus = s.time_flexibility * 0.3
        startup_penalty = s.startup_months * 0.2
        return (income_score + scalability_bonus + flexibility_bonus - startup_penalty) / energy_cost
    return sorted(strategies, key=score, reverse=True)


@dataclass
class IncomeGrowthScenario:
    name: str
    current_income: float
    year_by_year: List[float]  # 各年の月収
    strategy_mix: List[str]


class IncomeSimulator:
    def __init__(self, current_monthly_income: float, has_low_energy: bool = True):
        self.base = current_monthly_income
        self.has_low_energy = has_low_energy

    def project(self, strategies: List[IncomeStrategy], years: int = 10) -> IncomeGrowthScenario:
        """選択した戦略を組み合わせた収入成長を投影する"""
        year_income = [self.base]
        current = self.base

        # 各年の積み上げ効果をシミュレート
        sorted_by_startup = sorted(strategies, key=lambda s: s.startup_months)

        for yr in range(1, years + 1):
            added = 0.0
            for s in sorted_by_startup:
                start_yr = (s.startup_months + 11) // 12
                if yr >= start_yr:
                    # 成熟度に応じて収入が段階的に増える
                    maturity = min(1.0, (yr - start_yr + 1) / 3)
                    added += s.income_potential_monthly * maturity * (0.6 if self.has_low_energy else 1.0)
            # 複利的な成長（スキル・実績の蓄積効果）
            growth_multiplier = 1 + 0.03 * yr * (0.5 if self.has_low_energy else 1.0)
            year_income.append(current + added * growth_multiplier)

        return IncomeGrowthScenario(
            name="低体力最適化プラン" if self.has_low_energy else "標準プラン",
            current_income=self.base,
            year_by_year=year_income,
            strategy_mix=[s.name for s in strategies],
        )
