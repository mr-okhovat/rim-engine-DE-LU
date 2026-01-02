from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .config import DatasetPaths, RIMConfig
from .io import DataQualityReport, load_inputs
from .processing import compute_factors
from .regimes import map_score_to_regime


def build_risk_panel(
    ts: pd.DataFrame, cfg: RIMConfig, reports: dict[str, DataQualityReport]
) -> dict:
    ts_nonan = ts.dropna()
    if ts_nonan.empty:
        raise ValueError("No data available to build risk panel. Check ingestion and timestamps.")

    latest = ts_nonan.iloc[-1]
    rim = float(latest["RIM_0_100"])
    reg = map_score_to_regime(rim, cfg)

    return {
        "zone": cfg.zone,
        "config_hash": cfg.config_hash(),
        "latest_timestamp": str(ts.index.max()),
        "latest": {
            "RIM_0_100": rim,
            "regime": reg,
            "factors_0_25": {
                "PD": float(latest["PD_0_25"]),
                "LD": float(latest["LD_0_25"]),
                "RES": float(latest["RES_0_25"]),
                "IMB": float(latest["IMB_0_25"]),
            },
        },
        "ingestion_reports": {k: v.to_dict() for k, v in reports.items()},
    }


def panel_to_markdown(panel: dict) -> str:
    latest = panel["latest"]
    f = latest["factors_0_25"]

    lines = [
        f"# RIM Risk Panel — {panel['zone']}",
        "",
        f"- Config hash: `{panel['config_hash']}`",
        f"- Latest timestamp: `{panel['latest_timestamp']}`",
        f"- RIM score (0–100): **{latest['RIM_0_100']:.2f}**",
        f"- Regime: **{latest['regime']}**",
        "",
        "## Factor scores (0–25)",
        "",
        f"- PD: {f['PD']:.2f}",
        f"- LD: {f['LD']:.2f}",
        f"- RES: {f['RES']:.2f}",
        f"- IMB: {f['IMB']:.2f}",
        "",
        "## Ingestion quality (summary)",
    ]

    for name, rep in panel["ingestion_reports"].items():
        lines.append(
            f"- **{name}**: rows_raw={rep['n_rows_raw']}, rows_valid={rep['n_rows_valid']}, "
            f"sep='{rep['sep_used']}', time='{rep['time_col']}', value='{rep['value_col']}'"
        )

    lines.append("")
    return "\n".join(lines)


def run_end_to_end(data_dir: Path, out_dir: Path, cfg: RIMConfig) -> tuple[pd.DataFrame, dict]:
    paths = DatasetPaths.from_data_dir(data_dir)

    inputs, reports = load_inputs(
        paths={
            "pd": paths.power_csv,
            "pd_neigh": paths.power_csv,
            "ld": paths.load_csv,
            "res": paths.res_actual_csv,
        },
        tz=cfg.tz,
        freq=cfg.freq,
    )

    fo = compute_factors(inputs, cfg)

    ts = fo.factor_scores_0_25.copy()
    ts["RIM_0_100"] = fo.rim_score_0_100
    ts = ts.sort_index()

    out_dir.mkdir(parents=True, exist_ok=True)
    ts.to_csv(out_dir / "rim_timeseries.csv", index=True)

    panel = build_risk_panel(ts, cfg, reports)
    (out_dir / "risk_panel.json").write_text(json.dumps(panel, indent=2), encoding="utf-8")
    (out_dir / "risk_panel.md").write_text(panel_to_markdown(panel), encoding="utf-8")

    return ts, panel
