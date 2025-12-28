from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

from .config import RIMConfig


def rolling_zscore(x: pd.Series, window: int) -> pd.Series:
    mu = x.rolling(window, min_periods=max(3, window // 4)).mean()
    sd = x.rolling(window, min_periods=max(3, window // 4)).std(ddof=0).replace(0, np.nan)
    z = (x - mu) / sd
    return z.replace([np.inf, -np.inf], np.nan).fillna(0.0)


def z_to_0_25(z: pd.Series, scale: float = 2.0) -> pd.Series:
    zz = z.clip(-6, 6) / scale
    y = np.tanh(zz)
    return 12.5 * (y + 1.0)


@dataclass(frozen=True)
class FactorOutputs:
    factor_scores_0_25: pd.DataFrame
    rim_score_0_100: pd.Series
    drivers: pd.DataFrame


def _safe_align_to_index(s: pd.Series, idx: pd.DatetimeIndex) -> pd.Series:
    if s.empty:
        return pd.Series(index=idx, dtype=float)
    return s.reindex(idx).ffill().bfill()


def compute_factors(df_inputs: pd.DataFrame, cfg: RIMConfig) -> FactorOutputs:
    """
    Uses unified ingested inputs:
      - pd, pd_neigh, ld, res

    With your CURRENT sample data, RES is from 2023 and PD/LD are from 2025.
    So we must not require full intersection across all columns, otherwise df becomes empty.

    This function:
      - builds PD & LD on PD/LD timeframe
      - uses RES if it overlaps; otherwise sets RES factor neutral (12.5)
      - uses IMB proxy from load ramp (until proper residual / imbalance sources are added)
    """
    cfg.validate()

    required = ["pd", "pd_neigh", "ld", "res"]
    missing = [c for c in required if c not in df_inputs.columns]
    if missing:
        raise KeyError(f"compute_factors missing required columns: {missing}. Have: {list(df_inputs.columns)}")

    df = df_inputs.copy().sort_index()
    df = df[~df.index.isna()]

    # Coerce numeric (io.py already does robust parsing, but keep safe)
    for c in required:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Determine a working index that does NOT force intersection with RES
    # We use the union of pd/pd_neigh/ld timestamps, then drop rows where those are missing.
    core = df[["pd", "pd_neigh", "ld"]].dropna()
    if core.empty:
        raise ValueError(
            "compute_factors: core inputs (pd, pd_neigh, ld) are empty after coercion/dropna. "
            "This indicates ingestion is still broken."
        )
    idx = core.index

    # === PD factor (spread zscore) ===
    spread = (core["pd"] - core["pd_neigh"]).astype(float)
    pd_score = z_to_0_25(rolling_zscore(spread, cfg.zscore_window_h))

    # === LD factor (level + ramp) ===
    load = core["ld"].astype(float)
    ramp_abs = load.diff().abs().fillna(0.0)
    ld_z = 0.7 * rolling_zscore(load, cfg.zscore_window_h) + 0.3 * rolling_zscore(ramp_abs, cfg.zscore_window_h)
    ld_score = z_to_0_25(ld_z)

    # === RES factor ===
    res_series = df["res"].dropna()
    if res_series.empty:
        # neutral if no res data at all
        res_score = pd.Series(12.5, index=idx)
        res_used = False
    else:
        # try to align res to idx; if no overlap, it becomes all NaN
        res_aligned = res_series.reindex(idx)
        if res_aligned.notna().sum() < max(5, len(idx) // 20):
            # not enough overlap → neutral factor
            res_score = pd.Series(12.5, index=idx)
            res_used = False
        else:
            # use inverse res (low RES => higher risk)
            inv_res = (
    (1.0 / res_aligned.replace(0, np.nan))
    .replace([np.inf, -np.inf], np.nan)
    .ffill()
    .bfill()
)

            inv_res = inv_res.fillna(inv_res.median() if inv_res.notna().any() else 0.0)
            res_score = z_to_0_25(rolling_zscore(inv_res, cfg.zscore_window_h))
            res_used = True

    # === IMB factor (proxy until proper imbalance sources) ===
    # For now: treat sudden load ramps as balancing stress proxy.
    imb_proxy = ramp_abs
    imb_score = z_to_0_25(rolling_zscore(imb_proxy, cfg.zscore_window_h))

    factors = pd.DataFrame(
        {"PD_0_25": pd_score, "LD_0_25": ld_score, "RES_0_25": res_score, "IMB_0_25": imb_score},
        index=idx,
    ).sort_index()

    w = cfg.weights()
    rim_0_100 = (
        factors["PD_0_25"] * w["pd"]
        + factors["LD_0_25"] * w["ld"]
        + factors["RES_0_25"] * w["res"]
        + factors["IMB_0_25"] * w["imb"]
    ) * 4.0

    drivers = pd.DataFrame(
        {
            "pd_spread": spread,
            "ld_load": load,
            "ld_ramp_abs": ramp_abs,
            "res_used_flag": pd.Series(1.0 if res_used else 0.0, index=idx),
            "imb_proxy": imb_proxy,
        },
        index=idx,
    )

    return FactorOutputs(factor_scores_0_25=factors, rim_score_0_100=rim_0_100, drivers=drivers)
