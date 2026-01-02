from __future__ import annotations

from .config import RIMConfig


def map_score_to_regime(score_0_100: float, cfg: RIMConfig) -> str:
    a, b, c = cfg.regime_edges
    if score_0_100 < a:
        return "REGIME_1_NORMAL"
    if score_0_100 < b:
        return "REGIME_2_ATTENTION"
    if score_0_100 < c:
        return "REGIME_3_STRESSED"
    return "REGIME_4_SEVERE"
