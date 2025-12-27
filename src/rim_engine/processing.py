\
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


def compute_factors(df_inputs: pd.DataFrame, df_res_actual: pd.DataFrame, cfg: RIMConfig) -> FactorOutputs:
    cfg.validate()

    spread = (df_inputs["pd"] - df_inputs["pd_neigh"]).astype(float)
    pd_score = z_to_0_25(rolling_zscore(spread, cfg.zscore_window_h))

    load = df_inputs["ld"].astype(float)
    ramp_abs = load.diff().abs().fillna(0.0)
    ld_z = 0.7 * rolling_zscore(load, cfg.zscore_window_h) + 0.3 * rolling_zscore(ramp_abs, cfg.zscore_window_h)
    ld_score = z_to_0_25(ld_z)

    res = df_res_actual.copy()
    if "Start date" in res.columns:
        res["Start date"] = pd.to_datetime(res["Start date"], errors="coerce")
        res = res.dropna(subset=["Start date"]).set_index("Start date")
    # Keep only numeric columns (drop e.g., 'End date')
    res = res.apply(pd.to_numeric, errors='coerce')
    if cfg.tz and res.index.tz is None:
        res.index = res.index.tz_localize(cfg.tz, ambiguous="infer", nonexistent="shift_forward")
    res = res.sort_index().resample(cfg.freq).mean()

    ren_cols = [
        "Biomass [MWh] Original resolutions",
        "Hydropower [MWh] Original resolutions",
        "Wind offshore [MWh] Original resolutions",
        "Wind onshore [MWh] Original resolutions",
        "Photovoltaics [MWh] Original resolutions",
        "Other renewable [MWh] Original resolutions",
    ]
    missing = [c for c in ren_cols if c not in res.columns]
    if missing:
        raise KeyError(f"Missing renewable columns: {missing}")

    total_ren = res[ren_cols].sum(axis=1)
    total_gen = res.select_dtypes(include=[np.number]).sum(axis=1).replace(0, np.nan)
    share = (total_ren / total_gen).fillna(0.0)
    inv_share = (1.0 - share).reindex(df_inputs.index).ffill().fillna(0.0)
    res_score = z_to_0_25(rolling_zscore(inv_share, cfg.zscore_window_h))

    residual_actual = (total_gen.fillna(0.0) - total_ren).reindex(df_inputs.index).ffill().fillna(0.0)
    residual_fc = df_inputs["residual_fc"].astype(float)
    mismatch = (residual_fc - residual_actual).abs()
    imb_score = z_to_0_25(rolling_zscore(mismatch, cfg.zscore_window_h))

    factors = pd.DataFrame(
        {"PD_0_25": pd_score, "LD_0_25": ld_score, "RES_0_25": res_score, "IMB_0_25": imb_score},
        index=df_inputs.index,
    )

    w = cfg.weights()
    rim_0_100 = (
        factors["PD_0_25"] * w["pd"]
        + factors["LD_0_25"] * w["ld"]
        + factors["RES_0_25"] * w["res"]
        + factors["IMB_0_25"] * w["imb"]
    ) * 4.0

    drivers = pd.DataFrame(
        {"pd_spread": spread, "ld_load": load, "ld_ramp_abs": ramp_abs, "res_inv_share": inv_share, "imb_mismatch": mismatch},
        index=df_inputs.index,
    )

    return FactorOutputs(factor_scores_0_25=factors, rim_score_0_100=rim_0_100, drivers=drivers)
