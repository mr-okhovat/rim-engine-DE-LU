from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd

from rim_engine.regime_thresholds import THRESHOLDS_V1, derive_regime

OUTPUT_DIR = Path("outputs")
PANEL_FILE = OUTPUT_DIR / "rim_panel.csv"
REPORT_JSON = OUTPUT_DIR / "eval_report.json"
REPORT_MD = OUTPUT_DIR / "eval_report.md"


def load_panel() -> pd.DataFrame:
    if not PANEL_FILE.exists():
        raise FileNotFoundError(f"Missing panel file: {PANEL_FILE}")

    df = pd.read_csv(PANEL_FILE, parse_dates=["ts"])

    required = {"ts", "RIM_0_100", "PD_0_25", "LD_0_25", "RES_0_25", "IMB_0_25"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Panel missing required columns: {sorted(missing)}")

    if "regime" not in df.columns:
        df["regime"] = df["RIM_0_100"].apply(derive_regime)

    return df


def regime_share(df: pd.DataFrame) -> dict:
    counts = df["regime"].value_counts().to_dict()
    total = len(df)
    return {k: v / total for k, v in counts.items()}


def average_regime_duration_hours(df: pd.DataFrame) -> float:
    durations: list[int] = []
    current: str | None = None
    length = 0

    for r in df["regime"]:
        if r != current:
            if length > 0:
                durations.append(length)
            current = r
            length = 1
        else:
            length += 1

    if length > 0:
        durations.append(length)

    return sum(durations) / max(len(durations), 1)


def factor_dominance(df: pd.DataFrame) -> dict:
    factors = ["PD_0_25", "LD_0_25", "RES_0_25", "IMB_0_25"]
    high = df[df["regime"].isin(["elevated", "high"])]

    dominance = Counter()
    for _, row in high.iterrows():
        dominant = max(factors, key=lambda f: float(row[f]))
        dominance[dominant] += 1

    return dict(dominance)


def main() -> None:
    df = load_panel()

    report = {
        "rows": int(len(df)),
        "window_start": df["ts"].min().isoformat(),
        "window_end": df["ts"].max().isoformat(),
        "regime_share": regime_share(df),
        "avg_regime_duration_hours": float(average_regime_duration_hours(df)),
        "factor_dominance_elevated_high": factor_dominance(df),
        "thresholds_v1": {
            "low_lt": THRESHOLDS_V1.low_lt,
            "moderate_lt": THRESHOLDS_V1.moderate_lt,
            "elevated_lt": THRESHOLDS_V1.elevated_lt,
            "high_ge": THRESHOLDS_V1.elevated_lt,
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2))

    REPORT_MD.write_text(
        "# RIM Evaluation Report\n\n"
        f"Rows: {report['rows']}\n\n"
        f"Window: {report['window_start']} → {report['window_end']}\n\n"
        "## Regime Share\n"
        + "\n".join(f"- {k}: {v:.2%}" for k, v in report["regime_share"].items())
        + "\n\n"
        "## Average Regime Duration\n"
        f"{report['avg_regime_duration_hours']:.2f} hours\n\n"
        "## Factor Dominance (Elevated/High)\n"
        + (
            "\n".join(f"- {k}: {v}" for k, v in report["factor_dominance_elevated_high"].items())
            or "- (none)"
        )
        + "\n\n"
        "## Thresholds (v1)\n"
        f"- low: RIM < {THRESHOLDS_V1.low_lt:g}\n"
        f"- moderate: {THRESHOLDS_V1.low_lt:g} ≤ RIM < {THRESHOLDS_V1.moderate_lt:g}\n"
        f"- elevated: {THRESHOLDS_V1.moderate_lt:g} ≤ RIM < {THRESHOLDS_V1.elevated_lt:g}\n"
        f"- high: RIM ≥ {THRESHOLDS_V1.elevated_lt:g}\n"
    )

    print("Evaluation complete.")
    print(f"Wrote: {REPORT_JSON}")
    print(f"Wrote: {REPORT_MD}")


if __name__ == "__main__":
    main()
