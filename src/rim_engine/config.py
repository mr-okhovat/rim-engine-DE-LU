from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple


@dataclass(frozen=True)
class RIMConfig:
    zone: str = "DE-LU"
    freq: str = "h"
    tz: str = "Europe/Berlin"

    w_pd: float = 0.30
    w_ld: float = 0.25
    w_res: float = 0.25
    w_imb: float = 0.20

    zscore_window_h: int = 24
    vol_window_h: int = 24
    vol_long_window_h: int = 72

    regime_edges: Tuple[float, float, float] = (25.0, 50.0, 75.0)

    def weights(self) -> Dict[str, float]:
        return {"pd": self.w_pd, "ld": self.w_ld, "res": self.w_res, "imb": self.w_imb}

    def validate(self) -> None:
        s = sum(self.weights().values())
        if abs(s - 1.0) > 1e-6:
            raise ValueError(f"Factor weights must sum to 1.0. Got {s:.6f}")

    def config_hash(self) -> str:
        import hashlib, json
        payload = {
            "zone": self.zone,
            "freq": self.freq,
            "tz": self.tz,
            "weights": self.weights(),
            "windows": {
                "zscore_h": self.zscore_window_h,
                "vol_h": self.vol_window_h,
                "vol_long_h": self.vol_long_window_h,
            },
            "regime_edges": self.regime_edges,
        }
        s = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(s).hexdigest()[:12]


@dataclass(frozen=True)
class DatasetPaths:
    power_csv: Path
    load_csv: Path
    res_actual_csv: Path

    @staticmethod
    def from_data_dir(data_dir: Path) -> "DatasetPaths":
        return DatasetPaths(
            power_csv=data_dir / "de_power_data.csv",
            load_csv=data_dir / "de_load_data.csv",
            res_actual_csv=data_dir / "de_res_actual.csv",
        )
