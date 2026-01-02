from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# ======================================================
# Data Quality Report
# ======================================================


@dataclass
class DataQualityReport:
    name: str
    time_col: str
    value_col: str
    sep_used: str
    n_rows_raw: int
    n_rows_valid: int
    first_ts: str | None
    last_ts: str | None
    notes: list[str]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "time_col": self.time_col,
            "value_col": self.value_col,
            "sep_used": self.sep_used,
            "n_rows_raw": self.n_rows_raw,
            "n_rows_valid": self.n_rows_valid,
            "first_ts": self.first_ts,
            "last_ts": self.last_ts,
            "notes": self.notes,
        }


# ======================================================
# Deterministic Ingestion Specification
# ======================================================


@dataclass(frozen=True)
class SeriesSpec:
    """
    Contract for ingesting a single time series.

    If schema fields are provided, ingestion is deterministic.
    """

    name: str

    # Strict schema
    time_col: str | None = None
    value_col: str | None = None
    sep: str | None = None
    datetime_format: str | None = None

    # Fallback heuristics (kept for robustness)
    preferred_value_cols: list[str] | None = None
    preferred_time_cols: list[str] | None = None

    tz: str | None = None
    freq: str = "h"

    def __post_init__(self):
        if self.preferred_value_cols is None:
            object.__setattr__(self, "preferred_value_cols", [])
        if self.preferred_time_cols is None:
            object.__setattr__(self, "preferred_time_cols", [])


# ======================================================
# Helpers
# ======================================================


def _guess_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _to_numeric_robust(s: pd.Series) -> pd.Series:
    """
    Robust numeric parsing for both:
      - "51,882.82" (comma thousands)
      - "51.882,82" (euro style)
      - "51882.82"
    """
    x = s.astype(str).str.replace("\u00a0", " ", regex=False).str.strip()

    has_comma = x.str.contains(",", regex=False)
    has_dot = x.str.contains(".", regex=False)

    # Case 1: comma thousands: 51,882.82 -> remove commas
    comma_thousands = has_comma & has_dot
    x.loc[comma_thousands] = x.loc[comma_thousands].str.replace(",", "", regex=False)

    # Case 2: euro style: 51.882,82 -> remove dots, swap comma to dot
    both = x.str.contains(r"\.", regex=True) & x.str.contains(r",", regex=True)
    euro_style = both & (~comma_thousands)
    x.loc[euro_style] = (
        x.loc[euro_style].str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    )

    # Case 3: only comma decimal: 51882,82 -> swap comma to dot
    only_comma = has_comma & (~has_dot)
    x.loc[only_comma] = x.loc[only_comma].str.replace(",", ".", regex=False)

    # Remove spaces
    x = x.str.replace(" ", "", regex=False)
    return pd.to_numeric(x, errors="coerce")


def _finalize_series(
    name: str,
    idx: pd.Series,
    values: pd.Series,
    tz: str | None,
    freq: str,
) -> pd.DataFrame:
    """
    Finalizes a single series into a clean, hourly (or freq) time series.

    CRITICAL: avoid pandas alignment bugs by using to_numpy() so values are assigned positionally.
    Also: handle Europe/Berlin DST ambiguity deterministically by converting to UTC.
    """
    # Force positional assignment (no index alignment surprises)
    out = pd.DataFrame({name: values.to_numpy()}, index=pd.DatetimeIndex(idx))

    # Remove NaT timestamps early
    out = out[~out.index.isna()].sort_index()
    if out.empty:
        return out

    # Remove duplicates (keep last)
    out = out[~out.index.duplicated(keep="last")]

    # Timezone policy:
    # - If tz provided: localize (drop ambiguous repeated-hour stamps) then convert to UTC
    if tz:
        if out.index.tz is None:
            # AmbiguousTimeError-safe: drop ambiguous timestamps
            out.index = out.index.tz_localize(tz, nonexistent="shift_forward", ambiguous="NaT")
            out = out[~out.index.isna()]
            if out.empty:
                return out
            out.index = out.index.tz_convert("UTC")
        else:
            out.index = out.index.tz_convert("UTC")

    # Resample to target frequency and drop missing
    out = out.resample(freq).mean()
    out = out.dropna()
    return out


# ======================================================
# Core CSV Loader (single-series CSV)
# ======================================================


def load_series_csv(path: Path, spec: SeriesSpec) -> tuple[pd.DataFrame, DataQualityReport]:
    notes: list[str] = []

    sep = spec.sep or ";"
    df = pd.read_csv(path, sep=sep, encoding="utf-8-sig", low_memory=False)
    n_rows_raw = len(df)

    time_col = spec.time_col or _guess_col(df, spec.preferred_time_cols or [])
    value_col = spec.value_col or _guess_col(df, spec.preferred_value_cols or [])

    if time_col is None or value_col is None:
        raise ValueError(
            f"[{spec.name}] Cannot determine time/value columns. "
            f"Available columns: {list(df.columns)[:50]}"
        )

    if spec.datetime_format:
        idx = pd.to_datetime(df[time_col], format=spec.datetime_format, errors="coerce")
    else:
        idx = pd.to_datetime(df[time_col], errors="coerce")

    values = _to_numeric_robust(df[value_col])
    out = _finalize_series(spec.name, idx, values, spec.tz, spec.freq)

    rep = DataQualityReport(
        name=spec.name,
        time_col=time_col,
        value_col=value_col,
        sep_used=sep,
        n_rows_raw=n_rows_raw,
        n_rows_valid=len(out),
        first_ts=str(out.index.min()) if len(out) else None,
        last_ts=str(out.index.max()) if len(out) else None,
        notes=notes,
    )
    return out, rep


# ======================================================
# RES Loader (multi-component CSV -> derived single series)
# ======================================================


def load_res_actual_csv(
    path: Path, tz: str | None, freq: str = "h"
) -> tuple[pd.DataFrame, DataQualityReport]:
    """
    Loads RES actual generation CSV and derives a single total RES series (wind+solar).
    Aggregates:
      - Wind offshore
      - Wind onshore
      - Photovoltaics
    Output column: 'res'
    """
    notes: list[str] = []
    sep = ";"
    dtfmt = "%b %d, %Y %I:%M %p"

    df = pd.read_csv(path, sep=sep, encoding="utf-8-sig", low_memory=False)
    n_rows_raw = len(df)

    if "Start date" not in df.columns:
        raise ValueError(
            f"[res] Missing 'Start date' in {path.name}. Columns: {list(df.columns)[:30]}"
        )

    idx = pd.to_datetime(df["Start date"], format=dtfmt, errors="coerce")

    candidates = [
        "Wind offshore [MWh] Original resolutions",
        "Wind onshore [MWh] Original resolutions",
        "Photovoltaics [MWh] Original resolutions",
    ]
    present = [c for c in candidates if c in df.columns]
    if not present:
        raise ValueError(
            f"[res] None of expected RES component columns found in {path.name}. "
            f"Columns: {list(df.columns)[:50]}"
        )

    res_total = None
    for c in present:
        s = _to_numeric_robust(df[c])
        res_total = s if res_total is None else (res_total + s)

    out = _finalize_series("res", idx, res_total, tz, freq)

    rep = DataQualityReport(
        name="res",
        time_col="Start date",
        value_col=" + ".join(present),
        sep_used=sep,
        n_rows_raw=n_rows_raw,
        n_rows_valid=len(out),
        first_ts=str(out.index.min()) if len(out) else None,
        last_ts=str(out.index.max()) if len(out) else None,
        notes=notes + [f"Aggregated columns: {present}"],
    )
    return out, rep


# ======================================================
# Public API — Load All Inputs
# ======================================================


def load_inputs(
    paths: dict[str, Path],
    tz: str | None,
    freq: str = "h",
) -> tuple[pd.DataFrame, dict[str, DataQualityReport]]:
    """
    Loads and returns a unified dataframe of:
      - pd
      - pd_neigh
      - ld
      - res (derived from RES actual components)

    IMPORTANT:
    - All outputs are in UTC if tz is provided.
    - Resampling happens per-series.
    """
    dtfmt = "%b %d, %Y %I:%M %p"

    SPECS: dict[str, SeriesSpec] = {
        "pd": SeriesSpec(
            name="pd",
            sep=";",
            time_col="Start date",
            value_col="Germany/Luxembourg [€/MWh] Calculated resolutions",
            datetime_format=dtfmt,
            tz=tz,
            freq=freq,
        ),
        "pd_neigh": SeriesSpec(
            name="pd_neigh",
            sep=";",
            time_col="Start date",
            value_col="∅ DE/LU neighbours [€/MWh] Calculated resolutions",
            datetime_format=dtfmt,
            tz=tz,
            freq=freq,
        ),
        "ld": SeriesSpec(
            name="ld",
            sep=";",
            time_col="Start date",
            value_col="Grid load incl. hydro pumped storage [MWh] Calculated resolutions",
            datetime_format=dtfmt,
            tz=tz,
            freq=freq,
        ),
    }

    frames: list[pd.DataFrame] = []
    reports: dict[str, DataQualityReport] = {}

    for key, p in paths.items():
        if key == "res":
            df_k, rep = load_res_actual_csv(Path(p), tz=tz, freq=freq)
        else:
            spec = SPECS.get(key, SeriesSpec(name=key, tz=tz, freq=freq))
            df_k, rep = load_series_csv(Path(p), spec)

        frames.append(df_k)
        reports[key] = rep

    combined = pd.concat(frames, axis=1).sort_index()
    return combined, reports
