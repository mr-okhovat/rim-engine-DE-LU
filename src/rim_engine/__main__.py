from __future__ import annotations

import argparse
from pathlib import Path

from .config import RIMConfig
from .panel import run_end_to_end


def main() -> None:
    p = argparse.ArgumentParser(description="Run RIM Engine 4-factor pipeline on local CSV data.")
    p.add_argument("--data-dir", type=str, default="data")
    p.add_argument("--out-dir", type=str, default="outputs")
    args = p.parse_args()
    cfg = RIMConfig()
    ts, panel = run_end_to_end(Path(args.data_dir), Path(args.out_dir), cfg)
    print(panel["latest"])


if __name__ == "__main__":
    main()
