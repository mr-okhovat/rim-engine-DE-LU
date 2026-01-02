# RIM Engine (DE-LU) — Validation Plan (v1)

## Purpose

This document defines how we validate the RIM Engine for **deterministic, explainable risk-regime detection** in the **DE-LU power market context**. “Validation” here does not mean forecasting performance. It means: (i) correctness and stability of computation, (ii) interpretability of factor behavior, and (iii) robustness under realistic German market operating conditions.

## Scope and Non-Scope

### In scope
- Deterministic reproducibility: same inputs produce identical outputs.
- Factor-level sanity: PD/LD/RES/IMB move in the expected direction under controlled perturbations.
- Bounds and invariants: all factor scores remain within their defined ranges and the aggregate score behaves consistently.
- Data-quality behavior: predictable handling of missingness, partial overlap, and outliers consistent with the product goal.
- Operational readiness: the pipeline runs reliably and produces a coherent panel suitable for downstream consumption.

### Out of scope (explicitly not claimed)
- Price forecasting, PnL attribution, or trading edge claims.
- Statistical “model validation” (confidence intervals, hypothesis testing) as used for predictive models.
- Any claim of representing true imbalance prices/volumes (IMB is a deterministic proxy as documented).
- Market-wide causal inference or regulatory interpretation beyond what is explicitly implemented.

## Validation Principles

1. **Determinism first:** The engine is designed to be explainable and stable. Validation prioritizes invariants, traceability, and reproducibility over opaque metrics.
2. **Germany-first realism:** Validation scenarios reflect German/EU operational reality (DE-LU hourly cadence, typical volatility regimes, renewables variability, and cross-market coupling artifacts).
3. **Explainability over complexity:** Every check should be defensible to a technical stakeholder and legible to a non-technical stakeholder.
4. **Layered evidence:** We validate at multiple layers (unit → integration → narrative → operational) to reduce false confidence from any single test.
5. **No re-opening solved ingestion/DST/alignment:** These are treated as stabilized. We only revisit if a new test fails.

## Data and Reference Sources (Conceptual)

The validation approach does not require new data integrations. It assumes access to:
- Representative DE-LU hourly time series already supported by the ingestion layer (price, load, renewable proxies, and any neighbor/benchmark proxy used by PD).
- Optional “reference periods” (known stress episodes) for qualitative spot checks, without claiming predictive skill.

This document intentionally avoids specifying vendors or introducing dependencies. Validation must remain possible with current repo inputs and test fixtures.

## Validation Layers

### L0 — Specification conformance (document-level)
Objective: ensure implementation matches documented intent.
Checks:
- `docs/factors.md` remains the source of truth for factor definitions and ranges.
- `PD_0_25`, `LD_0_25`, `RES_0_25`, `IMB_0_25` are each defined on **0–25**, and `RIM_0_100` on **0–100**.
- Weighting and scaling rules are explicit and consistent across docs and code.

Evidence:
- This document + `docs/factors.md` + code references (no new features required).

### L1 — Invariants and boundedness (unit-level)
Objective: guarantee the engine cannot produce invalid score shapes/ranges.
Checks (must always hold):
- Score bounds: each factor ∈ [0, 25], aggregate ∈ [0, 100].
- No NaN leakage to final panel for periods where required inputs exist (defined per factor).
- Monotonic clipping: if an input is extreme, scores saturate rather than explode.
- Deterministic output ordering and stable indexing.

Evidence:
- Existing unit tests (and any future tests) demonstrate these invariants.

### L2 — Deterministic perturbation tests (factor behavior)
Objective: validate directional behavior without ML or forecasting claims.
Method: apply controlled perturbations to inputs and confirm expected score changes.

Examples of expected behavior (directional, not numeric promises):
- PD increases when spread/tension to neighbor/benchmark increases (holding other inputs constant).
- LD increases when load volatility/ramps increase (holding other inputs constant).
- RES increases when renewable variability/availability stress increases (holding other inputs constant).
- IMB increases when the deterministic proxy conditions indicate tighter balance pressure as defined in the factor spec.

Acceptance: the direction of change must be correct and explainable, and the engine must remain within bounds.

Evidence:
- A small suite of deterministic test cases and/or documented “input → expected direction” tables.

### L3 — Regime coherence checks (integration-level)
Objective: ensure the combined score produces coherent regimes and avoids pathological behavior.
Checks:
- Aggregation behaves predictably: increasing one factor (with others held) should not reduce `RIM_0_100`.
- Regime transitions are stable: no “flicker” due to indexing artifacts or missingness handling.
- Cross-factor independence sanity: if only renewables are stressed, the narrative should reflect RES-driven stress rather than inventing PD/LD drivers.

Evidence:
- Integration test runs on representative windows; output panels inspected for stability and coherence.
- Optional: a lightweight “snapshot” comparison against a stored expected panel for a fixed fixture (deterministic).

### L4 — Operational readiness (product-level)
Objective: ensure the engine is usable as a component in a partner workflow.
Checks:
- Local run produces a complete panel with predictable schema and column naming.
- Runtime is stable for typical DE-LU horizons (e.g., months of hourly data) on a standard laptop environment.
- Failures are explicit: missing critical inputs produce clear diagnostics rather than silent corruption.
- Versioning discipline: changes to scoring logic trigger an explicit validation note (see Change Control).

Evidence:
- Successful `python -m scripts.run_local` run log + generated output panel example (no notebooks).
- CI pass + reproducible environment steps.

## Acceptance Criteria (Ship-Ready Gates)

The engine is considered “validation-ready for partner consumption” when all gates are true:

1. **Reproducibility gate:** running the pipeline twice on the same inputs yields identical outputs (hash or exact equality).
2. **Bounds gate:** all scores remain within their defined ranges across the full evaluation window.
3. **Schema gate:** output panel schema and column names are stable and documented.
4. **Directional behavior gate:** L2 perturbation checks pass for PD/LD/RES/IMB.
5. **Aggregation gate:** increasing any single factor input stress does not reduce `RIM_0_100` (holding others).
6. **Operational gate:** local run completes successfully and produces an output artifact suitable for downstream API/CLI consumption.
7. **Narrative gate:** a reviewer can read `docs/factors.md` and explain a high-score period using factor outputs without referencing hidden logic.

## Known Limitations and Guardrails

- The engine detects *risk regime conditions*; it does not forecast prices or revenues.
- IMB is a deterministic proxy and is not equivalent to imbalance market settlement outcomes.
- Regime labels are only as meaningful as the factor spec; changes require explicit change control.
- Validation does not claim exhaustive coverage of all German market edge cases; it prioritizes robust behavior under common operational patterns.

## Evidence Pack (Deliverables for Stakeholders)

When asked “how do you know it works?”, provide:
- `docs/factors.md` (factor definitions and intent)
- `docs/validation.md` (this plan and acceptance gates)
- CI test results (`pytest`)
- A deterministic run artifact (output panel for a fixed fixture window)
- A short narrative example: one calm week vs one stress week, explained only through PD/LD/RES/IMB deltas (no forecasting claims)

## Change Control

To preserve trust:
- Any modification to factor logic, normalization, weighting, clipping, or missingness rules must:
  1) update `docs/factors.md` if definitions change,
  2) update this validation plan if gates/evidence change,
  3) include a short “validation impact” note in the PR description,
  4) add/adjust tests that cover the change deterministically.

Solved ingestion/DST/alignment issues are not revisited unless a new test fails.
