from __future__ import annotations


class RimEngineError(Exception):
    """Base class for all RIM Engine operational errors (not programming errors)."""


class InvalidArgumentsError(RimEngineError):
    """Raised when user inputs/flags/arguments are invalid."""


class MissingInputsError(RimEngineError):
    """Raised when required inputs are missing or insufficient for requested window."""


class EmptyResultError(RimEngineError):
    """Raised when request is valid but yields no rows (after filtering/alignment)."""
