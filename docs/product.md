# RIM Engine (DE-LU) — Product Overview

## Positioning

The RIM Engine is a **deterministic, explainable risk-regime classification engine** for the German/Luxembourg power market.
It converts heterogeneous hourly market signals into a **single, interpretable risk index (RIM_0_100)** supported by four transparent factor scores.

It is designed for **situational awareness and risk context**, not for price prediction or automated trading.

## Who This Is For

Primary users:
- Power market risk managers
- Portfolio managers (generation, flexibility, PPA portfolios)
- Trading analytics teams supporting DA/ID desks
- Market operations and planning teams

Secondary users:
- Strategy and digitalization teams
- Quant developers integrating regime awareness into downstream systems
- Consulting teams building explainable market diagnostics

This engine is **not** designed for retail trading or black-box signal generation.

## The Problem It Solves

In the DE-LU market, risk rarely comes from a single variable.
Stress regimes emerge from combinations of:
- price tension versus benchmarks,
- load volatility and ramps,
- renewable availability and variability,
- balance tightness proxies.

Most teams either:
- track too many disconnected indicators, or
- rely on opaque composite scores they cannot explain internally.

The RIM Engine solves this by:
- standardizing heterogeneous signals,
- bounding them into comparable stress scores,
- aggregating them into a stable regime index with a clear narrative.

## What the Engine Produces

**Inputs (conceptual):**
- Hourly DE-LU price series and benchmark proxies
- Load and load-dynamics signals
- Renewable availability / variability proxies
- Deterministic balance-pressure proxies

**Outputs (hourly panel):**
- `PD_0_25` — Price Dynamics stress
- `LD_0_25` — Load Dynamics stress
- `RES_0_25` — Renewable stress
- `IMB_0_25` — Imbalance pressure proxy
- `RIM_0_100` — Aggregated risk regime index

All outputs are:
- bounded,
- deterministic,
- explainable at factor level.

## How It Is Used (Workflow Position)

The RIM Engine sits **upstream of decision-making**, not inside execution.

Typical placement:
- before risk committee reviews,
- before portfolio rebalancing discussions,
- before intraday focus allocation,
- as a contextual layer for dashboards or alerts.

It answers:
> “What kind of market regime are we operating in right now, and why?”

## Decisions It Supports

The engine supports **human decisions**, such as:
- adjusting risk limits or attention levels,
- reallocating analyst or trader focus,
- contextualizing PnL swings,
- explaining stress periods to management,
- distinguishing structural stress from noise.

It does **not** output trade instructions.

## What This Engine Explicitly Does NOT Do

- It does not forecast prices or volumes.
- It does not optimize bids or positions.
- It does not replace trader judgment.
- It does not claim causal attribution.
- It does not represent actual imbalance settlement prices.

Any use beyond regime awareness must be implemented downstream.

## Why Determinism Matters

Every output of the RIM Engine is:
- reproducible,
- traceable to inputs,
- explainable without statistical inference.

This enables:
- internal trust,
- auditability,
- regulatory defensibility,
- stable long-term integration.

If inputs do not change, outputs do not change.

## Integration Patterns

Common integration modes:
- batch generation feeding BI dashboards,
- API-based access for internal tools,
- embedding as a regime flag in analytics pipelines,
- use as a conditioning variable for downstream models.

The engine is intentionally lightweight and dependency-minimal.

## When Not to Use the RIM Engine

Do not use this engine if you need:
- short-term price forecasts,
- probabilistic scenario generation,
- automated trading signals,
- market-wide causal claims.

The RIM Engine is a **risk context layer**, not a trading model.
