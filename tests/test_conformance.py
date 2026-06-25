"""Fixture-driven conformance, ported from the reference implementation.

Every file under ``fixtures/valid`` MUST parse and validate; every file under
``fixtures/invalid`` MUST be rejected. Valid docs also round-trip (serialize ->
parse -> identical canonical form), and any signed valid fixture must verify —
the signed fixture was produced by the TypeScript reference, so verifying it here
proves cross-implementation interop.
"""
from __future__ import annotations

import pytest

from nlt_toi import (
    ToiError,
    canonicalize,
    is_signed,
    parse_toi,
    safe_parse_toi,
    serialize_toi,
    verify_toi,
)
from tests.conftest import invalid_files, valid_files


@pytest.mark.parametrize("path", valid_files(), ids=lambda p: p.name)
def test_accepts_valid_fixture(path):
    raw = path.read_text(encoding="utf-8")
    doc = parse_toi(raw)
    assert doc["$toi"] == "1.0.0"
    assert safe_parse_toi(raw).success is True
    # Serialization is canonically idempotent.
    canon = canonicalize(doc)
    assert canonicalize(parse_toi(serialize_toi(doc))) == canon


def test_has_valid_fixtures():
    assert len(valid_files()) > 0


def test_verifies_signed_valid_fixtures():
    signed = [p for p in valid_files() if is_signed(parse_toi(p.read_text(encoding="utf-8")))]
    assert len(signed) > 0, "expected at least one signed valid fixture"
    for path in signed:
        assert verify_toi(parse_toi(path.read_text(encoding="utf-8"))) is True


def test_has_invalid_fixtures():
    assert len(invalid_files()) > 0


@pytest.mark.parametrize("path", invalid_files(), ids=lambda p: p.name)
def test_rejects_invalid_fixture(path):
    raw = path.read_text(encoding="utf-8")
    with pytest.raises(ToiError):
        parse_toi(raw)
    assert safe_parse_toi(raw).success is False
