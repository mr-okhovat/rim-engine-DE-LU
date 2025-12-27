# RIM Engine (DE-LU) — 4-Factor Risk Regime Index

This repository contains a **clean, package-first** implementation of a 4-factor **Risk Intelligence Model (RIM)** for the German/Luxembourg power market.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
python -m rim_engine --data-dir data --out-dir outputs
pytest -q
```

## Outputs
- `outputs/rim_timeseries.csv`
- `outputs/risk_panel.json`
- `outputs/risk_panel.md`
