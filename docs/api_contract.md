# RIM Engine (DE-LU) — API / CLI Contract (v1)

Purpose

This document defines a stable, implementation-agnostic contract for exposing RIM Engine outputs via command-line interfaces (CLI), HTTP APIs, or internal services. It specifies what can be requested, what is returned, how errors are handled, and how compatibility is maintained over time. The contract deliberately avoids forecasting, optimization, or machine-learning behavior.

Scope

In scope:
- Retrieval of deterministic RIM Engine outputs over a defined time window
- Exposure of factor scores and the aggregated risk index
- Exposure of regime labels derived from docs/regime_thresholds.md
- Basic metadata to support auditability and reproducibility

Out of scope:
- Scenario generation
- Probabilistic forecasting
- Trading recommendations or execution logic
- Representation of actual imbalance settlement prices

Versioning

Contract version: v1

Backward compatibility rules:
- New optional fields may be added without changing the version
- Removing or renaming fields, or changing their meaning, requires a new contract version
- Any output schema change must follow docs/output_schema.md change rules

Core concepts

Time window:
- Data is requested for a time window [start, end]
- Both start and end are inclusive
- Data frequency is hourly
- Timezone handling follows the stabilized ingestion and alignment logic; DST behavior is not redefined here

Regime label:
- A categorical interpretation derived from RIM_0_100 using docs/regime_thresholds.md
- Possible values: low, moderate, elevated, high
- Regime labels are descriptive only and are not forecasts

CLI contract (minimal)

Command:
rim-engine run

Flags:
--data-dir <path>       input data directory
--out-dir <path>        output directory
--start <ISO8601>       optional start timestamp
--end <ISO8601>         optional end timestamp
--format <csv|json>     output format if supported
--contract-version      print contract version and exit

Exit codes:
0  success
2  invalid arguments
3  missing or insufficient input data
4  internal error

HTTP API contract (minimal)

Endpoint: health check
GET /health

Response:
status: ok
contract_version: v1

Endpoint: retrieve RIM panel
GET /rim/panel

Query parameters:
start            optional ISO8601 timestamp
end              optional ISO8601 timestamp
format           optional, default json
include_regime   optional, default true

Response fields:
contract_version
market           DE-LU
frequency        hourly
start
end
schema_version
rows
meta

Each row contains:
ts               timestamp (ISO8601, UTC)
PD_0_25
LD_0_25
RES_0_25
IMB_0_25
RIM_0_100
regime

Meta contains:
engine_commit        git commit hash that produced the output
inputs_fingerprint   optional hash of input data
generated_at         generation timestamp

Notes:
- Column definitions and value ranges are defined in docs/output_schema.md
- Regime labels follow docs/regime_thresholds.md
- CSV outputs use “Start date” as the timestamp column; API outputs use “ts”
- engine_commit is mandatory in audit-sensitive environments

Error handling

Errors are returned in a structured form containing:
- contract_version
- error code
- human-readable message
- optional contextual details

Common error codes:
INVALID_ARGUMENT
MISSING_INPUTS
EMPTY_RESULT
INTERNAL_ERROR

Determinism and auditability

For the same engine commit, identical inputs, and identical time window, the output must be identical except for file-format serialization differences. The inclusion of engine_commit enables full traceability and reproducibility, consistent with docs/reference_run.md.

References

docs/output_schema.md
docs/regime_thresholds.md
docs/validation.md
docs/reference_run.md
