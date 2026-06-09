from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class AllocationResult:
    risk_profile: str
    allocations: Dict[str, float]  # asset_name -> percentage
    expected_return: float
    expected_volatility: float
    notes: List[str]


RISK_PROFILES = {
    "aggressive": {
        "name_jp": "積極型",
        "label_color": "bright_green",
        "allocations": {
            "全世界株式インデックス": 40.0,
            "米国成長株/ETF": 25.0,
            "新興国株式": 10.0,
            "不動産(REIT)": 10.0,
            "仮想通貨(BTC)": 10.0,
            "現金・債券(緊急資金)": 5.0,
        },
        "expected_return": 0.12,
        "expected_vol": 0.22,
    },
    "balanced": {
        "name_jp": "バランス型",
        "label_color": "cyan",
        "allocations": {
            "全世界株式インデックス": 45.0,
            "高配当株/ETF": 20.0,
            "国内外REIT": 10.0,
            "債券(国内/海外)": 15.0,
            "現金・緊急資金": 10.0,
        },
        "expected_return": 0.07,
        "expected_vol": 0.13,
    },
    "conservative": {
        "name_jp": "安定型",
        "label_color": "yellow",
        "allocations": {
            "国内債券": 30.0,
            "外国債券": 20.0,
            "全世界株式インデックス": 25.0,
            "高配当株": 10.0,
            "国内REIT": 5.0,
            "現金・緊急資金": 10.0,
        },
        "expected_return": 0.04,
        "expected_vol": 0.07,
    },
}


def recommend_profile(age: int, risk_tolerance: str, has_debt: bool) -> str:
    if has_debt:
        return "conservative"
    if risk_tolerance == "high":
        return "aggressive" if age < 45 else "balanced"
    if risk_tolerance == "medium":
        return "balanced"
    return "conservative"


def get_allocation(profile: str) -> AllocationResult:
    data = RISK_PROFILES.get(profile, RISK_PROFILES["balanced"])
    return AllocationResult(
        risk_profile=profile,
        allocations=data["allocations"],
        expected_return=data["expected_return"],
        expected_volatility=data["expected_vol"],
        notes=_get_notes(profile),
    )


def get_age_based_allocation(age: int) -> Tuple[str, AllocationResult]:
    """Simple age-based rule: stock% = 110 - age."""
    if age <= 35:
        profile = "aggressive"
    elif age <= 50:
        profile = "balanced"
    else:
        profile = "conservative"
    return profile, get_allocation(profile)


def _get_notes(profile: str) -> List[str]:
    notes = {
        "aggressive": [
            "20〜35歳向け: 時間を最大の武器として高リスク高リターンを追求",
            "毎年1回リバランスを実施",
            "暴落時(-30%超)は追加投資のチャンスと捉える",
            "NISA成長投資枠を成長株・ETFに優先使用",
        ],
        "balanced": [
            "35〜50歳向け: リターンを維持しつつリスクを分散",
            "株式比率65%・安定資産35%のコア戦略",
            "iDeCoと合わせると節税効果最大化",
            "半年〜1年ごとにリバランス",
        ],
        "conservative": [
            "50歳以上または短期資金向け: 資産保全を優先",
            "インフレ分(3%)は最低限確保できる構成",
            "退職後の生活費10年分は現金・債券で確保",
            "一部株式でインフレヘッジを継続",
        ],
    }
    return notes.get(profile, [])
