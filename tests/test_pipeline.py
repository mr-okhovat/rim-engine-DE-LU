from pathlib import Path

import pandas as pd

from rim_engine.config import RIMConfig
from rim_engine.panel import run_end_to_end


def test_end_to_end_runs(tmp_path: Path):
    data_dir = Path("data")

    # Required sample inputs
    assert (data_dir / "de_power_data.csv").exists()
    assert (data_dir / "de_load_data.csv").exists()
    assert (data_dir / "de_res_actual.csv").exists()

    out_dir = tmp_path / "outputs"
    cfg = RIMConfig()

    ts, panel = run_end_to_end(data_dir, out_dir, cfg)

    # Basic sanity
    assert isinstance(ts, pd.DataFrame)
    assert len(ts) > 0, "Timeseries is empty. Ingestion or time parsing failed."

    # Factors expected in v0.1 (4-factor scaffold)
    for c in ["PD_0_25", "LD_0_25", "RES_0_25", "IMB_0_25", "RIM_0_100"]:
        assert c in ts.columns, f"Missing expected column: {c}"

    # Output artifacts
    assert (out_dir / "rim_timeseries.csv").exists()
    assert (out_dir / "risk_panel.json").exists()
    assert (out_dir / "risk_panel.md").exists()

    # Guardrail: residual_fc should NOT be a required ingest input
    # (residual should be derived in processing as ld - res)
    assert "residual_fc" not in ts.columns

