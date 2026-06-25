"""RFC 8785 JSON Canonicalization Scheme (JCS).

Produces the single deterministic serialization of a JSON value that the ``.toi``
standard signs over. Two semantically equal documents always yield byte-identical
output, which is what makes Ed25519 signatures stable across platforms,
re-serializations, and language implementations.

Rules implemented (mirroring the reference TypeScript implementation):
  - Object keys sorted by UTF-16 code unit, recursively (RFC 8785 §3.2.3).
  - Strings escaped with JSON's minimal escaping.
  - Finite numbers serialized in the ECMAScript ``Number::toString`` form RFC 8785
    prescribes; ``NaN`` / ``Infinity`` rejected (not valid JSON).
  - Array order preserved.
  - Only JSON objects (``dict``), arrays (``list``/``tuple``), and the JSON
    primitives are canonicalizable; anything else (``set``, ``bytes``, class
    instances, …) is rejected.

Note: the schema's named fields are non-numeric, but the open ``custom`` section
may hold arbitrary JSON numbers, so number formatting must (and does) match
ECMAScript ``Number::toString`` for byte-for-byte signature parity with the
TypeScript reference.
"""
from __future__ import annotations

import json
import math
from decimal import Decimal
from typing import Any, List, Mapping, Sequence, Union

from .errors import ToiCanonicalizationError

#: A JSON value accepted by the canonicalizer.
JsonValue = Union[None, bool, int, float, str, Sequence["JsonValue"], Mapping[str, "JsonValue"]]

__all__ = ["JsonValue", "canonicalize", "canonicalize_to_bytes"]


def canonicalize(value: Any) -> str:
    """Serialize *value* to its RFC 8785 canonical JSON string."""
    out: List[str] = []
    _write(value, out)
    return "".join(out)


def canonicalize_to_bytes(value: Any) -> bytes:
    """Canonical JSON encoded as UTF-8 bytes — the exact input to sign / verify."""
    return canonicalize(value).encode("utf-8")


def _write(value: Any, out: List[str]) -> None:
    if value is None:
        out.append("null")
        return
    # bool is a subclass of int in Python — must be checked first.
    if isinstance(value, bool):
        out.append("true" if value else "false")
        return
    if isinstance(value, int):
        out.append(str(value))
        return
    if isinstance(value, float):
        out.append(_format_number(value))
        return
    if isinstance(value, str):
        out.append(_encode_string(value))
        return
    if isinstance(value, (list, tuple)):
        out.append("[")
        for i, element in enumerate(value):
            if i > 0:
                out.append(",")
            _write(element, out)
        out.append("]")
        return
    if isinstance(value, dict):
        keys = list(value.keys())
        for k in keys:
            if not isinstance(k, str):
                raise ToiCanonicalizationError(
                    f"Cannot canonicalize an object with a non-string key: {k!r}"
                )
        keys.sort(key=_utf16_code_units)
        out.append("{")
        for i, key in enumerate(keys):
            if i > 0:
                out.append(",")
            out.append(_encode_string(key))
            out.append(":")
            _write(value[key], out)
        out.append("}")
        return
    raise ToiCanonicalizationError(
        f"Cannot canonicalize a value of type {type(value).__name__}"
    )


def _encode_string(s: str) -> str:
    """JSON string token with RFC 8785-conformant minimal escaping."""
    return json.dumps(s, ensure_ascii=False)


def _utf16_code_units(s: str) -> bytes:
    """Sort key reproducing RFC 8785 §3.2.3 ordering (compare by UTF-16 code unit)."""
    return s.encode("utf-16-be")


def _format_number(value: float) -> str:
    """Serialize a finite float in the ECMAScript ``Number::toString`` form.

    RFC 8785 §3.2.2.3 mandates this exact serialization, so it must match the
    TypeScript reference byte-for-byte — Python's ``repr`` does not (it renders
    ``0.000001`` as ``"1e-06"`` and zero-pads exponents). Implemented from
    ECMA-262 ``Number::toString`` using the shortest round-tripping digits.
    """
    if not math.isfinite(value):
        raise ToiCanonicalizationError(f"Cannot canonicalize non-finite number: {value}")
    if value == 0:
        return "0"  # collapses -0.0 to "0", as ECMAScript does
    sign = "-" if value < 0 else ""
    # Shortest decimal that round-trips, decomposed into significant digits + exponent.
    digits_tuple, exponent = Decimal(repr(abs(value))).normalize().as_tuple()[1:]
    digits = "".join(str(d) for d in digits_tuple)
    k = len(digits)          # number of significant digits
    n = exponent + k         # position of the decimal point (ECMA-262 §6.1.6.1.20)
    if k <= n <= 21:
        return sign + digits + "0" * (n - k)
    if 0 < n <= 21:
        return sign + digits[:n] + "." + digits[n:]
    if -6 < n <= 0:
        return sign + "0." + "0" * (-n) + digits
    # Exponential form.
    exp = n - 1
    exp_sign = "+" if exp >= 0 else "-"
    mantissa = digits if k == 1 else digits[0] + "." + digits[1:]
    return f"{sign}{mantissa}e{exp_sign}{abs(exp)}"
