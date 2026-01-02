# RIM Engine (DE-LU) — Reference Run (Golden Run)

## Purpose

This document defines a **deterministic reference run** for the RIM Engine. It serves as a reproducibility receipt:

- same inputs + same version → same outputs
- provides a stable baseline for validating future changes
- supports partner trust without introducing forecasting claims

This is not a backtest. It is an operational reproducibility check.

---

## Preconditions

- Repo installed in editable mode:
  ```bash
  source .venv/bin/activate
  pip install -e .
