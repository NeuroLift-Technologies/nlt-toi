"""Parse / serialize / guard behavior and error taxonomy (ported from parse.test.ts)."""
from __future__ import annotations

import json

import pytest

from nlt_toi import (
    ToiParseError,
    ToiValidationError,
    is_toi,
    parse_toi,
    safe_parse_toi,
    serialize_toi,
)

MINIMAL = {"$toi": "1.0.0", "$tier": "personal", "identity": {"author": "x"}}


def test_accepts_objects_and_json_strings():
    assert parse_toi(MINIMAL)["$tier"] == "personal"
    assert parse_toi(json.dumps(MINIMAL))["$tier"] == "personal"


def test_preserves_unknown_keys():
    doc = parse_toi({**MINIMAL, "$futureReserved": 1, "extra": {"a": True}})
    assert doc["$futureReserved"] == 1
    assert doc["extra"] == {"a": True}


def test_safe_parse_surfaces_parse_error_for_bad_json():
    result = safe_parse_toi("not json{")
    assert result.success is False
    assert isinstance(result.error, ToiParseError)


def test_safe_parse_surfaces_validation_error_with_issues():
    result = safe_parse_toi({"$toi": "1.0.0", "$tier": "nope", "identity": {"author": "x"}})
    assert result.success is False
    assert isinstance(result.error, ToiValidationError)
    assert len(result.error.issues) > 0


def test_rejects_non_object_json_roots_as_parse_errors():
    for raw in ("[]", "42", "null"):
        with pytest.raises(ToiParseError):
            parse_toi(raw)


def test_is_toi_guards_values():
    assert is_toi(MINIMAL) is True
    assert is_toi({}) is False
    assert is_toi("nope") is False


def test_pretty_serialization_round_trips_and_ends_with_newline():
    s = serialize_toi(MINIMAL)
    assert s.endswith("\n")
    assert parse_toi(s) == parse_toi(MINIMAL)


def test_compact_serialization_has_no_newline():
    s = serialize_toi(MINIMAL, pretty=False)
    assert "\n" not in s


def test_reports_offending_path_in_validation_issues():
    result = safe_parse_toi({**MINIMAL, "communication": {"tone": "bad"}})
    assert result.success is False
    assert isinstance(result.error, ToiValidationError)
    assert any("communication" in i.path for i in result.error.issues)


def test_rejects_malformed_signature_encodings():
    result = safe_parse_toi(
        {**MINIMAL, "$signature": {"alg": "ed25519", "public_key": "@@@", "value": "@@@"}}
    )
    assert result.success is False
    assert isinstance(result.error, ToiValidationError)
