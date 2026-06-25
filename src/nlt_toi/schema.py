"""The canonical ``.toi`` v1.0.0 schema and validation.

The machine-readable source of truth is the JSON Schema (draft 2020-12) bundled
with this package at ``nlt_toi/schemas/toi-1.0.0.schema.json`` — itself derived
from the reference Zod schema in ``@neurolift-technologies/toi``. Every object in
the schema is *open* (``additionalProperties: {}``), so a v1.0.0 parser preserves
unknown / forward-compatible keys rather than rejecting them.
"""
from __future__ import annotations

import importlib.resources
import json
from copy import deepcopy
from typing import Any, Dict, List

from jsonschema import Draft202012Validator

from .errors import ToiIssue

__all__ = ["toi_schema", "schema_issues"]

_SCHEMA_FILENAME = "toi-1.0.0.schema.json"
_schema_cache: Dict[str, Any] = {}
_validator_cache: List[Draft202012Validator] = []


def _load_schema() -> Dict[str, Any]:
    if not _schema_cache:
        ref = importlib.resources.files(__package__) / "schemas" / _SCHEMA_FILENAME
        _schema_cache.update(json.loads(ref.read_text(encoding="utf-8")))
    return _schema_cache


def toi_schema() -> Dict[str, Any]:
    """Return a fresh copy of the bundled ``.toi`` JSON Schema.

    A copy is returned so callers cannot mutate the cached schema (and thereby the
    cached validator) process-wide.
    """
    return deepcopy(_load_schema())


def _validator() -> Draft202012Validator:
    if not _validator_cache:
        _validator_cache.append(Draft202012Validator(_load_schema()))
    return _validator_cache[0]


def schema_issues(document: Any) -> List[ToiIssue]:
    """Return the schema violations in *document*, empty when it is valid.

    Each issue's ``path`` is the dotted location of the offending value (empty at
    the document root), matching the reference implementation's issue shape.
    """
    issues: List[ToiIssue] = []
    for error in sorted(_validator().iter_errors(document), key=lambda e: list(e.absolute_path)):
        path = ".".join(str(part) for part in error.absolute_path)
        issues.append(ToiIssue(path=path, message=error.message))
    return issues
