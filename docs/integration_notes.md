# RIM Engine (DE-LU) — Integration Notes

Purpose

This document provides practical integration guidance for developers and partners consuming the RIM Engine outputs via CLI, API, or internal services. It complements the formal API and schema contracts by explaining how pieces fit together operationally and how to avoid breaking changes.

This document is not a specification. It is a handoff and coordination guide.

Scope

These notes apply to:
- CLI consumers
- API implementers
- Internal services reading RIM outputs
- Downstream analytics and dashboards

They do not introduce new functionality.

Canonical sources of truth

The following documents define authoritative behavior:

- docs/output_schema.md
  Defines column names, meanings, ranges, and nullability.

- docs/regime_thresholds.md
  Defines how regime labels (low / moderate / elevated / high) are derived.

- docs/api_contract.md
  Defines request/response structure, versioning, and error semantics.

- docs/validation.md
  Defines what “correct” means for the engine.

If there is a conflict, these documents override ad-hoc interpretations.

CSV vs API field mapping

The engine produces a primary tabular output (CSV or equivalent) and may expose the same data via API.

Key mapping rules:

- CSV timestamp column:
  “Start date”

- API timestamp field:
  “ts” (ISO8601, UTC)

All other factor fields map one-to-one:

PD_0_25
LD_0_25
RES_0_25
IMB_0_25
RIM_0_100

The API may add a derived field:
- regime

This field must be computed strictly using docs/regime_thresholds.md.

Versioning discipline

Two versions exist and must not drift independently:

- schema_version
  Tied to docs/output_schema.md

- contract_version
  Tied to docs/api_contract.md

Rules:
- Adding optional output fields is allowed without version bump.
- Renaming, removing, or changing meaning of fields requires:
  - schema version bump
  - contract version bump
  - documentation update
- CLI, API, and file outputs must remain consistent for the same version.

Reproducibility and auditability

Every integration should preserve traceability.

Required practices:
- Expose or log engine_commit wherever outputs are consumed.
- Treat engine_commit + input data as the identity of a result.
- Do not silently recompute or overwrite outputs without recording the commit.

This aligns with the reference run defined in docs/reference_run.md.

Regime usage guidance

Regime labels are interpretive context only.

Correct usage:
- dashboards
- risk communication
- escalation context
- conditioning downstream analytics

Incorrect usage:
- direct trading rules
- automated execution
- optimization targets

Any action logic must live outside the RIM Engine.

What not to change without coordination

The following must not be changed unilaterally:
- factor definitions
- factor scaling ranges
- aggregation logic
- regime threshold bands
- timestamp semantics

If a change is needed, it must be:
- documented
- versioned
- validated
- communicated

Integration mindset

The RIM Engine is a read-only, deterministic context layer.

Treat it as:
- a stable signal provider
- a shared language for risk
- an upstream dependency that values trust over cleverness

Avoid:
- embedding assumptions
- adding hidden transformations
- reinterpreting scores locally

References

docs/output_schema.md
docs/api_contract.md
docs/regime_thresholds.md
docs/validation.md
docs/reference_run.md
