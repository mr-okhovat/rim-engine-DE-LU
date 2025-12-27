from pathlib import Path
import pandas as pd
from rim_engine.config import RIMConfig
from rim_engine.panel import run_end_to_end


def test_end_to_end_runs(tmp_path: Path):
    data_dir = Path("data")
    assert (data_dir / "de_power_data.csv").exists()
    assert (data_dir / "de_load_data.csv").exists()
    assert (data_dir / "de_res_actual.csv").exists()

    out_dir = tmp_path / "outputs"
    cfg = RIMConfig()
    ts, panel = run_end_to_end(data_dir, out_dir, cfg)

    assert isinstance(ts, pd.DataFrame)
    for c in ["PD_0_25", "LD_0_25", "RES_0_25", "IMB_0_25", "RIM_0_100"]:
        assert c in ts.columns
    assert (out_dir / "rim_timeseries.csv").exists()
    assert (out_dir / "risk_panel.json").exists()
    assert (out_dir / "risk_panel.md").exists()
