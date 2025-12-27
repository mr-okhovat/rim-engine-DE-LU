\
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import pandas as pd


@dataclass(frozen=True)
class SeriesSpec:
    name: str
    preferred_value_cols: List[str]
    preferred_time_cols: List[str] = None
    tz: Optional[str] = None
    freq: str = "h"

    def __post_init__(self):
        object.__setattr__(self, "preferred_time_cols", self.preferred_time_cols or ["Start date", "timestamp", "time"])


@dataclass
class DataQualityReport:
    name: str
    n_rows_raw: int
    n_rows_hourly: int
    n_gaps: int
    first_ts: str
    last_ts: str
    time_col: str
    value_col: str
    sep_used: str
    notes: List[str]

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "n_rows_raw": self.n_rows_raw,
            "n_rows_hourly": self.n_rows_hourly,
            "n_gaps": self.n_gaps,
            "first_ts": self.first_ts,
            "last_ts": self.last_ts,
            "time_col": self.time_col,
            "value_col": self.value_col,
            "sep_used": self.sep_used,
            "notes": self.notes,
        }


def _sniff_sep(path: Path) -> str:
    txt = path.read_text(encoding="utf-8", errors="ignore")
    head = "\n".join(txt.splitlines()[:3])
    if head.count(";") > head.count(",") and head.count(";") > 1:
        return ";"
    if head.count("\t") > head.count(",") and head.count("\t") > 1:
        return "\t"
    return ","


def _read_csv_robust(path: Path) -> Tuple[pd.DataFrame, str]:
    sep = _sniff_sep(path)
    df = pd.read_csv(path, sep=sep, encoding="utf-8-sig")
    if df.shape[1] == 1 and isinstance(df.columns[0], str) and (";" in df.columns[0]):
        df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
        sep = ";"
    return df, sep


def _guess_time_col(df: pd.DataFrame, preferred: List[str]) -> str:
    for c in preferred:
        if c in df.columns:
            return c
    for c in df.columns:
        parsed = pd.to_datetime(df[c], errors="coerce")
        if parsed.notna().mean() > 0.95:
            return c
    raise ValueError(f"Could not infer timestamp column. Columns: {list(df.columns)}")


def _guess_value_col(df: pd.DataFrame, preferred: List[str]) -> str:
    for c in preferred:
        if c in df.columns:
            return c
    # Choose numeric column with most data
    best = None
    best_n = -1
    for c in df.columns:
        s = pd.to_numeric(df[c], errors="coerce")
        n = int(s.notna().sum())
        if n > best_n:
            best, best_n = c, n
    if best is None:
        raise ValueError("Could not infer value column.")
    return best


def _to_hourly_index(ts: pd.Series, tz: Optional[str]) -> pd.DatetimeIndex:
    idx = pd.to_datetime(ts, errors="coerce")
    if idx.isna().any():
        raise ValueError("Timestamp parse produced NaT values.")
    idx = pd.DatetimeIndex(idx)
    if tz:
        if idx.tz is None:
            idx = idx.tz_localize(tz, ambiguous="infer", nonexistent="shift_forward")
        else:
            idx = idx.tz_convert(tz)
    return idx.floor("h")


def load_series_csv(path: Path, spec: SeriesSpec) -> Tuple[pd.DataFrame, DataQualityReport]:
    df, sep_used = _read_csv_robust(path)
    n_rows_raw = len(df)
    notes: List[str] = []

    time_col = _guess_time_col(df, spec.preferred_time_cols)
    value_col = _guess_value_col(df.drop(columns=[time_col], errors="ignore"), spec.preferred_value_cols)

    idx = _to_hourly_index(df[time_col], tz=spec.tz)
    s = pd.to_numeric(df[value_col], errors="coerce")

    out = pd.DataFrame({spec.name: s.values}, index=idx).sort_index()
    out[spec.name] = pd.to_numeric(out[spec.name], errors="coerce")
    out = out.resample(spec.freq).mean()

    if len(out.index) > 1:
        full = pd.date_range(out.index.min(), out.index.max(), freq=spec.freq, tz=out.index.tz)
        n_gaps = int((~full.isin(out.index)).sum())
    else:
        n_gaps = 0
        notes.append("Not enough rows to evaluate gaps")

    rep = DataQualityReport(
        name=spec.name,
        n_rows_raw=n_rows_raw,
        n_rows_hourly=len(out),
        n_gaps=n_gaps,
        first_ts=str(out.index.min()) if len(out) else "",
        last_ts=str(out.index.max()) if len(out) else "",
        time_col=time_col,
        value_col=value_col,
        sep_used=sep_used,
        notes=notes,
    )
    return out, rep


def load_inputs(paths: Dict[str, Path], tz: Optional[str], freq: str = "h") -> Tuple[pd.DataFrame, Dict[str, DataQualityReport]]:
    pref = {
        "pd": ["Germany/Luxembourg [€/MWh] Calculated resolutions"],
        "pd_neigh": ["∅ DE/LU neighbours [€/MWh] Calculated resolutions"],
        "ld": ["Grid load incl. hydro pumped storage [MWh] Calculated resolutions"],
        "residual_fc": ["Residual load [MWh] Calculated resolutions"],
    }

    frames = []
    reports: Dict[str, DataQualityReport] = {}
    for key, p in paths.items():
        spec = SeriesSpec(name=key, preferred_value_cols=pref.get(key, []), tz=tz, freq=freq)
        df_k, rep = load_series_csv(Path(p), spec)
        frames.append(df_k)
        reports[key] = rep
    return pd.concat(frames, axis=1).sort_index(), reports
