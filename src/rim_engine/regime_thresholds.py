from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegimeThresholdsV1:
    """
    Deterministic thresholds for mapping RIM_0_100 to categorical regimes.

    v1:
      - low:      [0, 25)
      - moderate: [25, 50)
      - elevated: [50, 75)
      - high:     [75, 100]
    """

    low_lt: float = 25.0
    moderate_lt: float = 50.0
    elevated_lt: float = 75.0


THRESHOLDS_V1 = RegimeThresholdsV1()


def derive_regime(rim_0_100: float, t: RegimeThresholdsV1 = THRESHOLDS_V1) -> str:
    if rim_0_100 < t.low_lt:
        return "low"
    if rim_0_100 < t.moderate_lt:
        return "moderate"
    if rim_0_100 < t.elevated_lt:
        return "elevated"
    return "high"
