# RIM Engine (DE-LU) — Operational Runbook

## Purpose

This runbook describes how to **install, run, and troubleshoot** the RIM Engine in a local or development environment.

It is written for engineers and analysts who need to:
- run the engine reliably,
- understand expected behavior,
- interpret failures without inspecting source code.

This document assumes the ingestion, DST handling, and alignment logic are stabilized and correct.

---

## Supported Usage

This runbook covers:
- local execution,
- development and testing workflows,
- deterministic batch runs.

Production orchestration (e.g. scheduling, containerization) is intentionally out of scope.

---

## Installation

### Environment

- Python version: as defined by the project environment
- Virtual environment: required
- Editable install: required for development

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
