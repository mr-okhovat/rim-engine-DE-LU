# RIM Engine — Deterministic Evaluation Plan

## Purpose
This document defines how the RIM Engine is evaluated using historical data.
The goal is to validate interpretability, stability, and operational usefulness
— not predictive accuracy.

## Principles
- Fully deterministic (same inputs → same outputs)
- No forecasting or ML
- Germany-specific operational context
- Evaluation does not modify the engine

## Evaluation Dimensions

### 1. Regime Distribution
- Share of time spent in each regime (low / moderate / elevated / high)
- Used to detect pathological calibration (e.g. always-high or always-low)

### 2. Regime Persistence
- Average duration of contiguous regimes
- Transition counts between regimes
- Excessive regime “chatter” is considered undesirable

### 3. Stress Alignment (Proxy-Based)
High regimes are compared against stress proxies:
- Price volatility (rolling std)
- Large hourly price ramps (|Δprice|)
- High net-load ramps (Δload – ΔRES)

This is not prediction; it is coincidence analysis.

### 4. Factor Contribution
During elevated/high regimes:
- Relative contribution of PD / LD / RES / IMB
- Used to explain *why* stress was detected

### 5. Stability Checks
- Small window shifts should not cause regime collapse
- Ensures robustness against edge effects

## Outputs
Evaluation produces:
- Machine-readable JSON report
- Human-readable Markdown summary

These outputs are inputs to product validation, not trading decisions.
