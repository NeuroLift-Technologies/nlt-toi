"""Parsing, validation, and serialization for ``.toi`` documents.

:func:`parse_toi` is the throwing front door; :func:`safe_parse_toi` is the
result-returning variant for control flow without exceptions. Both accept either
a JSON string (the on-disk form) or an already-parsed value.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .errors import ToiError, ToiParseError, ToiValidationError
from .schema import schema_issues

#: A parsed ``.toi`` document. Structurally a JSON object; unknown keys preserved.
ToiDocument = Dict[str, Any]

__all__ = [
    "ToiDocument",
    "SafeParseResult",
    "parse_toi",
    "safe_parse_toi",
    "is_toi",
    "serialize_toi",
]


@dataclass(frozen=True)
class SafeParseResult:
    """A non-throwing parse outcome (mirrors the reference discriminated union)."""

    success: bool
    data: Optional[ToiDocument] = None
    error: Optional[ToiError] = None


def parse_toi(input: Any) -> ToiDocument:
    """Parse and validate a ``.toi`` document.

    Args:
        input: A JSON string or an already-parsed value.

    Raises:
        ToiParseError: if *input* is not valid JSON or its root is not an object.
        ToiValidationError: if the document violates the canonical schema.
    """
    document = _to_json_object(input)
    issues = schema_issues(document)
    if issues:
        summary = "; ".join(f"{i.path}: {i.message}" if i.path else i.message for i in issues)
        raise ToiValidationError(f"Invalid .toi document — {summary}", issues)
    return document


def safe_parse_toi(input: Any) -> SafeParseResult:
    """Parse and validate without raising, returning a discriminated result."""
    try:
        document = _to_json_object(input)
    except ToiParseError as err:
        return SafeParseResult(success=False, error=err)
    issues = schema_issues(document)
    if issues:
        summary = "; ".join(f"{i.path}: {i.message}" if i.path else i.message for i in issues)
        return SafeParseResult(
            success=False, error=ToiValidationError(f"Invalid .toi document — {summary}", issues)
        )
    return SafeParseResult(success=True, data=document)


def is_toi(input: Any) -> bool:
    """Return ``True`` when *input* is a valid ``.toi`` document."""
    return safe_parse_toi(input).success


def serialize_toi(doc: Any, *, pretty: bool = True, validate: bool = True) -> str:
    """Serialize a document to its on-disk JSON form.

    By default the document is validated first and pretty-printed (2-space indent,
    trailing newline) for human editing. This is **not** the signing form —
    signatures are computed over the RFC 8785 canonical bytes (see
    :func:`nlt_toi.canonicalize`), independent of on-disk formatting.
    """
    data: Any = parse_toi(doc) if validate else doc
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def _to_json_object(input: Any) -> ToiDocument:
    if isinstance(input, str):
        try:
            value = json.loads(input)
        except (ValueError, TypeError) as err:
            raise ToiParseError("Input is not valid JSON") from err
    else:
        value = input
    if not isinstance(value, dict):
        raise ToiParseError("A .toi document must be a JSON object")
    # JSON object keys are always strings. ``json.loads`` guarantees this, but a
    # hand-built dict passed directly could carry non-string keys that
    # serialize_toi would silently rewrite (e.g. 1 -> "1"), corrupting the
    # canonical form and any signature. Reject them up front.
    if not isinstance(input, str):
        _assert_string_keys(value)
    return value


def _assert_string_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise ToiParseError("A .toi document must use string-keyed JSON objects")
            _assert_string_keys(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            _assert_string_keys(nested)
