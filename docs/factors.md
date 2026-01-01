# RIM Engine Factors (DE-LU) — v1

This document explains the four factor scores produced by the RIM Engine. Each factor is scored on a 0–25 scale, then combined into a total RIM score (0–100). The goal is explainable, deterministic risk regime detection — not price forecasting.

## Output summary

The pipeline produces:

- `PD_0_25` — Price Dynamics stress proxy
- `LD_0_25` — Load Dynamics stress proxy
- `RES_0_25` — Renewable Stress proxy (availability/variability)
- `IMB_0_25` — Imbalance Pressure proxy (deterministic proxy in v1)
- `RIM_0_100` — weighted aggregate score scaled to 0–100

## PD (Price Dynamics) — `PD_0_25`

**Purpose:** Detect abnormal spread/tension between DE-LU price and a neighbour/benchmark proxy.

**Inputs:**
- `pd` (DE-LU price series)
- `pd_neigh` (neighbour/benchmark series)

**Logic (v1):**
- Compute spread: `pd - pd_neigh`
- Compute rolling z-score of spread
- Map the z-score to a bounded 0–25 score

**Interpretation:**
Higher PD indicates unusual price tension versus the benchmark, often coincident with stress (tightness, congestion effects, scarcity signals).

