"""LLM integration stubs (intentionally not enabled in v0.1.0)."""

from __future__ import annotations
from typing import Dict, Any


def call_analyst_llm(context: Dict[str, Any]) -> Dict[str, Any]:
    raise NotImplementedError("LLM integration is not enabled in v0.1.0. Implement in rim_engine/llm.py")


def call_evaluator_llm(context: Dict[str, Any]) -> Dict[str, Any]:
    raise NotImplementedError("LLM integration is not enabled in v0.1.0. Implement in rim_engine/llm.py")
