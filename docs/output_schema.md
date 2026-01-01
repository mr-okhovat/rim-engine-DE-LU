# RIM Engine (DE-LU) — Output Schema Contract (v1)

## Purpose

This document defines the **stable output schema** of the RIM Engine panel for downstream integration (CLI/API/storage/BI). It is the integration contract: consumers should not need to read source code to use the outputs correctly.

## Output Artifacts

The local run produces an output directory containing:
- A primary **hourly panel** (tabular time series) containing factor scores and the aggregate RIM score.

Exact filenames may vary by runner, but the **panel schema and semantics** must remain stable.

## Time Index Contract

- Cadence: **hourly**
- Market scope: **DE-LU**
- Index ordering: strictly increasing by timestamp
- Timezone handling: the pipeline produces a consistent hourly index as implemented in the stabilized ingestion/alignment layer. This contract does not redefine DST behavior; it assumes the stabilized behavior as correct.
- Duplicate timestamps: not permitted in the final panel.

## Columns

All factor scores are bounded, deterministic, and interpretable.

| Column | Type | Range | Meaning |
|------|------|-------|---------|
| PD_0_25 | float | [0, 25] | Price Dynamics stress proxy |
| LD_0_25 | float | [0, 25] | Load Dynamics stress proxy |
| RES_0_25 | float | [0, 25] | Renewable Stress proxy |
| IMB_0_25 | float | [0, 25] | Imbalance Pressure proxy (deterministic; not settlement) |
| RIM_0_100 | float | [0, 100] | Weighted aggregate risk regime index |

## Nullability Rules

- If required inputs for a factor are unavailable for a timestamp, that factor may be null **only if** the pipeline cannot compute it deterministically.
- The pipeline must not silently forward-fill stress scores without explicit design intent.
- `RIM_0_100`:
  - must be computable whenever all required factor inputs exist, and
  - must not be null due to unrelated, non-critical inputs.

## Range and Invariant Constraints

- All scores must be clipped to their defined bounds.
- Increasing stress in one factor’s input (holding others constant) must not reduce `RIM_0_100` (aggregation monotonicity expectation).
- No NaN leakage: where factor computation is defined, the output must be defined.

## Backward Compatibility and Versioning

- Adding optional columns is allowed if existing columns remain unchanged.
- Renaming columns, changing ranges, or changing semantics requires:
  - a schema version bump,
  - an update to this document,
  - and corresponding validation impact notes.

## Example Row (Illustrative Only)

Timestamp: 2025-01-15 13:00  
PD_0_25=6.0, LD_0_25=5.0, RES_0_25=7.0, IMB_0_25=4.0, RIM_0_100=22.0
