from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd

OUTPUT_DIR = Path("outputs")
PANEL_FILE = OUTPUT_DIR / "rim_panel.csv"
REPORT_JSON = OUTPUT_DIR / "eval_report.json"
REPORT_MD = OUTPUT_DIR / "eval_report.md"


# Keep thresholds centralized. If you later formalize docs/regime_thresholds.md into code,
# this function becomes an adapter to that canonical definition.
def derive_regime(rim: float) -> str:
    """
    Deterministic regime label derived from RIM_0_100.

    Default v1 thresholds (conservative, monotonic):
    - low:      [0, 25)
    - moderate: [25, 50)
    - elevated: [50, 75)
    - high:     [75, 100]
    """
    if rim < 25:
        return "low"
    if rim < 50:
        return "moderate"
    if rim < 75:
        return "elevated"
    return "high"


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
    durations = []
    current = None
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
            "low_lt": 25,
            "moderate_lt": 50,
            "elevated_lt": 75,
            "high_ge": 75,
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
        "- low: RIM < 25\n"
        "- moderate: 25 ≤ RIM < 50\n"
        "- elevated: 50 ≤ RIM < 75\n"
        "- high: RIM ≥ 75\n"
    )

    print("Evaluation complete.")
    print(f"Wrote: {REPORT_JSON}")
    print(f"Wrote: {REPORT_MD}")


if __name__ == "__main__":
    main()
