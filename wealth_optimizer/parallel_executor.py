"""
並行実行プランナー: 複数戦略を体力制約内で同時進行するためのフェーズ管理。
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json
import os

TRACKER_FILE = os.path.join(os.path.dirname(__file__), ".progress.json")


@dataclass
class WeeklyTask:
    strategy: str
    week: int
    task: str
    hours_needed: float
    category: str   # SETUP / LEARN / CREATE / LAUNCH / GROW
    done: bool = False


@dataclass
class Phase:
    number: int
    name: str
    months: str
    focus: str
    strategies: List[str]
    weekly_hours_budget: float
    rationale: str
    milestones: List[str]


# フェーズ設計: 低体力での最適な段階的立ち上げ
PHASES: List[Phase] = [
    Phase(
        number=1,
        name="即効性重視フェーズ",
        months="今すぐ〜2ヶ月",
        focus="お金を稼ぐ感覚をつかむ & 税制優遇を確保",
        strategies=[
            "AIを使ったコンテンツ制作代行",
            "AIツール活用で業務効率化→昇給交渉",
        ],
        weekly_hours_budget=5.0,
        rationale=(
            "収益化まで最短1〜2ヶ月。AIが実作業を担うため体力消費が最小。"
            "まず「売れた」体験を作ることで次フェーズへの自信とキャッシュを確保する。"
            "同時にNISA/iDeCo口座を開設し投資の自動化を設定（一度設定すれば手間ゼロ）。"
        ),
        milestones=[
            "NISA・iDeCo口座の開設完了",
            "クラウドワークスで最初の受注1件",
            "AIで納品できたことを確認",
            "月3万円の副業収入を達成",
        ],
    ),
    Phase(
        number=2,
        name="ストック資産構築フェーズ",
        months="2〜5ヶ月",
        focus="寝ていても収入が発生する仕組みの種まき",
        strategies=[
            "デジタルコンテンツ販売 (note・Kindle・Udemy)",
            "YouTubeチャンネル (AI・テキスト読み上げ活用)",
        ],
        weekly_hours_budget=7.0,
        rationale=(
            "フェーズ1で月3万円のキャッシュフローが安定したら、"
            "同時に『寝ていても収入が入る』ストック型資産を仕込み始める。"
            "YouTubeは100本が目標なので早めにスタートした方が有利。"
            "noteは週1本のペースで良い。体調の波に合わせて量を調整。"
        ),
        milestones=[
            "noteに有料記事を3本公開",
            "YouTube動画を10本公開",
            "デジタル商品の初回販売を経験",
            "月1万円のストック収入を達成",
        ],
    ),
    Phase(
        number=3,
        name="高単価化フェーズ",
        months="3〜6ヶ月",
        focus="時間単価を上げて作業量あたりの収入を最大化",
        strategies=[
            "オンライン専門家コンサルティング",
        ],
        weekly_hours_budget=4.0,
        rationale=(
            "フェーズ1・2で実績と収入が安定してきたら、"
            "自分の専門知識を高単価で売るコンサルを開始する。"
            "ビザスクは登録から初回案件まで平均1〜2ヶ月。"
            "1件2〜5万円なので月2件で月10万円。体力消費は最小。"
        ),
        milestones=[
            "ビザスク・コーチェックに登録",
            "プロフィールを完成させる",
            "初回コンサル案件を受注",
            "時間単価2万円以上を達成",
        ],
    ),
    Phase(
        number=4,
        name="スケール化フェーズ",
        months="6〜12ヶ月以降",
        focus="仕組み化・自動化・レバレッジ最大化",
        strategies=[
            "スモールSaaS / Webツール開発",
        ],
        weekly_hours_budget=8.0,
        rationale=(
            "フェーズ1〜3で月20〜30万円の副業収入基盤ができたら、"
            "最大リターンのSaaS開発にリソースを投入する。"
            "すでにAIツールの使い方・コンテンツ作成・顧客対話の経験があるため"
            "どんな問題を解くべきかの解像度が上がっている状態でスタートできる。"
        ),
        milestones=[
            "解決する問題を1つ特定",
            "MVP(最小版)を3ヶ月で構築",
            "無料ユーザー10人から検証",
            "月額課金で最初の1万円を達成",
        ],
    ),
]

# 週次タスクリスト (各戦略の最初の8週間)
WEEKLY_TASKS: Dict[str, List[WeeklyTask]] = {
    "AIを使ったコンテンツ制作代行": [
        WeeklyTask("AIコンテンツ代行", 1, "クラウドワークスに登録・プロフィール作成", 1.0, "SETUP"),
        WeeklyTask("AIコンテンツ代行", 1, "ChatGPT/Claude Proに申し込む", 0.5, "SETUP"),
        WeeklyTask("AIコンテンツ代行", 1, "競合のプロフィールを5件調査してポイントを把握", 1.0, "LEARN"),
        WeeklyTask("AIコンテンツ代行", 2, "サンプル記事をAIで3本作りポートフォリオにする", 2.0, "CREATE"),
        WeeklyTask("AIコンテンツ代行", 2, "低単価案件(3,000〜5,000円)に5件応募", 1.0, "LAUNCH"),
        WeeklyTask("AIコンテンツ代行", 3, "初受注→納品→レビューをもらう", 2.0, "LAUNCH"),
        WeeklyTask("AIコンテンツ代行", 4, "リピート依頼または新規2件受注", 2.0, "GROW"),
        WeeklyTask("AIコンテンツ代行", 5, "単価を1.5倍に引き上げた新プランを出品", 0.5, "GROW"),
    ],
    "AIツール活用で業務効率化→昇給交渉": [
        WeeklyTask("業務効率化", 1, "現在の業務でAIに任せられるタスクを10個リストアップ", 1.0, "LEARN"),
        WeeklyTask("業務効率化", 1, "最も時間がかかる1タスクをAIで自動化する", 1.5, "CREATE"),
        WeeklyTask("業務効率化", 2, "週次の削減時間を記録し始める(実績データ作り)", 0.5, "CREATE"),
        WeeklyTask("業務効率化", 3, "削減した時間で上司に見える成果を1つ作る", 2.0, "GROW"),
        WeeklyTask("業務効率化", 6, "削減時間・成果を数値化し昇給交渉の資料にまとめる", 1.0, "GROW"),
        WeeklyTask("業務効率化", 8, "上司に昇給・評価面談を申し込む", 0.5, "LAUNCH"),
    ],
    "デジタルコンテンツ販売 (note・Kindle・Udemy)": [
        WeeklyTask("デジタル販売", 1, "noteアカウント作成・プロフィール設定", 0.5, "SETUP"),
        WeeklyTask("デジタル販売", 1, "売れているnote記事のテーマ・価格を20件調査", 1.0, "LEARN"),
        WeeklyTask("デジタル販売", 2, "自分の専門知識・経験で書けるテーマを5つ出す", 0.5, "CREATE"),
        WeeklyTask("デジタル販売", 2, "最初の有料記事(500〜1,000円)をAI補助で執筆", 2.0, "CREATE"),
        WeeklyTask("デジタル販売", 3, "記事を公開・SNSでシェア", 0.5, "LAUNCH"),
        WeeklyTask("デジタル販売", 4, "2本目の記事を公開", 1.5, "GROW"),
        WeeklyTask("デジタル販売", 6, "5本たまったらKindle化を検討", 1.0, "GROW"),
        WeeklyTask("デジタル販売", 8, "月1万円のデジタル販売収入を目標に継続", 1.0, "GROW"),
    ],
    "YouTubeチャンネル (AI・テキスト読み上げ活用)": [
        WeeklyTask("YouTube", 1, "VOICEVOXインストール・Canva登録", 0.5, "SETUP"),
        WeeklyTask("YouTube", 1, "投資・節約・副業系の人気チャンネルを10個分析", 1.0, "LEARN"),
        WeeklyTask("YouTube", 2, "テスト動画を1本作る(完成度より完成を優先)", 2.0, "CREATE"),
        WeeklyTask("YouTube", 2, "チャンネル開設・アップロード", 0.5, "LAUNCH"),
        WeeklyTask("YouTube", 3, "週1本ペースを維持(体調悪い週はスキップOK)", 2.0, "GROW"),
        WeeklyTask("YouTube", 5, "10本達成→タイトルとサムネの改善", 1.0, "GROW"),
        WeeklyTask("YouTube", 7, "コメント・データを見て伸びているテーマに集中", 1.0, "GROW"),
        WeeklyTask("YouTube", 8, "週2本に増やせそうか体力と相談", 0.5, "GROW"),
    ],
    "オンライン専門家コンサルティング": [
        WeeklyTask("コンサル", 1, "自分の専門領域を3つ言語化する", 1.0, "SETUP"),
        WeeklyTask("コンサル", 1, "ビザスク・コーチェックに登録", 0.5, "SETUP"),
        WeeklyTask("コンサル", 2, "プロフィールを職歴ベースで充実させる", 1.0, "CREATE"),
        WeeklyTask("コンサル", 3, "最初は1時間1万円で受け付け開始", 0.5, "LAUNCH"),
        WeeklyTask("コンサル", 4, "初回コンサル実施・レビューをもらう", 2.0, "LAUNCH"),
        WeeklyTask("コンサル", 6, "レビュー2〜3件後に単価を引き上げる", 0.5, "GROW"),
        WeeklyTask("コンサル", 8, "月2〜4件の定常受注を目指す", 1.0, "GROW"),
    ],
    "スモールSaaS / Webツール開発": [
        WeeklyTask("SaaS", 1, "解決する問題を1つ特定し『誰の何の課題か』を1行で書く", 1.0, "LEARN"),
        WeeklyTask("SaaS", 2, "ターゲットユーザーに5人ヒアリング(Twitter/知人)", 2.0, "LEARN"),
        WeeklyTask("SaaS", 3, "Claude/ChatGPTでMVPのコードを書き始める", 3.0, "CREATE"),
        WeeklyTask("SaaS", 5, "動くものを無料で10人に試してもらう", 2.0, "LAUNCH"),
        WeeklyTask("SaaS", 7, "フィードバックを元に改善・課金準備(Stripe設定)", 2.0, "GROW"),
        WeeklyTask("SaaS", 8, "月980〜2,980円で課金開始", 1.0, "LAUNCH"),
    ],
}


class ProgressTracker:
    """JSON ファイルで進捗を永続化する簡易トラッカー"""

    def __init__(self, path: str = TRACKER_FILE):
        self.path = path
        self._data: dict = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"strategies": {}, "logs": []}

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def start_strategy(self, strategy_name: str, phase: int):
        self._data["strategies"][strategy_name] = {
            "phase": phase,
            "started": True,
            "current_week": 1,
            "completed_tasks": [],
            "monthly_income": 0,
        }
        self._save()

    def log_action(self, strategy_name: str, action: str, income_gained: float = 0):
        from datetime import date
        self._data["logs"].append({
            "date": str(date.today()),
            "strategy": strategy_name,
            "action": action,
            "income_gained": income_gained,
        })
        if strategy_name in self._data["strategies"]:
            self._data["strategies"][strategy_name]["monthly_income"] += income_gained
            self._data["strategies"][strategy_name]["current_week"] += 1
        self._save()

    def complete_task(self, strategy_name: str, task_desc: str):
        if strategy_name in self._data["strategies"]:
            self._data["strategies"][strategy_name]["completed_tasks"].append(task_desc)
        self._save()

    def get_status(self) -> dict:
        return self._data

    def total_monthly_income(self) -> float:
        return sum(v.get("monthly_income", 0) for v in self._data["strategies"].values())

    def get_next_tasks(self, strategy_name: str) -> List[WeeklyTask]:
        week = self._data.get("strategies", {}).get(strategy_name, {}).get("current_week", 1)
        tasks = WEEKLY_TASKS.get(strategy_name, [])
        return [t for t in tasks if t.week >= week][:3]
