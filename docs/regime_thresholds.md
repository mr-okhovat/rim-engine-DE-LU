# RIM Engine (DE-LU) — Regime Threshold Policy

## Purpose

This document defines **interpretive thresholds** for the aggregated `RIM_0_100` score.

The goal is to provide a **shared, consistent language** for describing market regimes across teams, without embedding trading rules or automated decisions.

Thresholds are policy guidance, not forecasts.

---

## Threshold Bands

| RIM_0_100 Range | Regime Label | Description |
|---------------|-------------|-------------|
| 0 – 25 | Low | Calm, structurally loose conditions |
| 25 – 50 | Moderate | Normal operating regime |
| 50 – 70 | Elevated | Increasing stress and uncertainty |
| 70 – 100 | High | Structurally tight, high-stress regime |

Thresholds are intentionally coarse to avoid false precision.

---

## Regime Interpretation

### Low (0–25)
- Tight alignment between price, load, and renewables
- No dominant stress driver
- Noise dominates over structure

Typical reading: “Business as usual.”

---

### Moderate (25–50)
- Normal market variability
- One factor may be elevated, but not persistent
- Risks are manageable and explainable

Typical reading: “Pay attention, but no escalation.”

---

### Elevated (50–70)
- Multi-factor stress begins to appear
- Renewables, load, or price dynamics may reinforce each other
- Uncertainty increases and assumptions weaken

Typical reading: “Heightened awareness required.”

---

### High (70–100)
- Structural stress across multiple drivers
- Persistent tightness signals
- Increased sensitivity to shocks

Typical reading: “Environment is difficult; volatility is expected.”

---

## Persistence vs Spikes

- **Short spikes** into a higher regime may reflect transient events.
- **Persistent readings** over multiple hours/days indicate structural conditions.
- Interpretation should consider duration, not single timestamps.

The RIM Engine does not predict regime duration.

---

## How Teams Should Use This Policy

This policy supports:
- consistent internal communication,
- escalation decisions,
- contextualizing PnL volatility,
- aligning risk discussions across teams.

It does not prescribe actions.

---

## What This Policy Does Not Do

- It does not recommend trades or positions
- It does not define risk limits
- It does not forecast reversals
- It does not claim optimal thresholds

Thresholds are designed for interpretability, not optimization.

---

## Change Control

Threshold definitions should change only if:
- factor definitions materially change, or
- long-term operational experience justifies adjustment.

Any change requires documentation and explicit communication.
