"""Error taxonomy for the ``.toi`` reference library.

Every error raised by a public API is a :class:`ToiError`, so callers can catch
the whole family with one ``except`` while still discriminating on ``.code``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

#: The closed set of error codes, mirroring the reference implementation.
ToiErrorCode = str  # one of: PARSE | VALIDATION | CANONICALIZATION | SIGNATURE | TIER


@dataclass(frozen=True)
class ToiIssue:
    """A single schema violation, flattened to a dotted path and a message."""

    path: str
    message: str


class ToiError(Exception):
    """Base class for every error raised by this library."""

    code: ToiErrorCode

    def __init__(self, code: ToiErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code


class ToiParseError(ToiError):
    """Input was not well-formed JSON, or its root was not a JSON object."""

    def __init__(self, message: str) -> None:
        super().__init__("PARSE", message)


class ToiValidationError(ToiError):
    """A document violated the canonical ``.toi`` schema."""

    def __init__(self, message: str, issues: Sequence[ToiIssue]) -> None:
        super().__init__("VALIDATION", message)
        self.issues = tuple(issues)


class ToiCanonicalizationError(ToiError):
    """A value could not be canonicalized per RFC 8785 (e.g. a non-finite number)."""

    def __init__(self, message: str) -> None:
        super().__init__("CANONICALIZATION", message)


class ToiSignatureError(ToiError):
    """Signing or verification could not be performed.

    Distinct from "signature did not match" — :func:`nlt_toi.verify_toi` reports a
    non-matching signature by returning ``False``, not by raising.
    """

    def __init__(self, message: str) -> None:
        super().__init__("SIGNATURE", message)


class ToiTierError(ToiError):
    """Tier resolution encountered an inconsistency (e.g. no documents to resolve)."""

    def __init__(self, message: str) -> None:
        super().__init__("TIER", message)
