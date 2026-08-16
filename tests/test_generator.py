"""Tests for :mod:`nlt_toi.generator` — high-level document authoring."""
from __future__ import annotations

import json

import pytest

from nlt_toi import (
    DEFAULT_DOCUMENT,
    TOIDocumentGenerator,
    ToiValidationError,
    generate_key_pair,
    is_signed,
    is_toi,
    parse_toi,
    sign_toi,
)


def test_from_defaults_produces_conforming_document():
    gen = TOIDocumentGenerator.from_defaults(author="alice", handle="alice-test")
    assert gen.document["$toi"] == "1.0.0"
    assert gen.document["$tier"] == "personal"
    assert gen.document["identity"]["author"] == "alice"
    assert gen.document["identity"]["handle"] == "alice-test"
    assert is_toi(gen.document) is True


def test_from_defaults_applies_privacy_first_defaults():
    gen = TOIDocumentGenerator.from_defaults(author="alice")
    privacy = gen.document["privacy"]
    assert privacy["retention"] == "session-only"
    assert privacy["cross_platform_sharing"] == "never"
    assert privacy["training_use"] == "prohibited"
    assert privacy["analytics"] == "prohibited"


def test_from_defaults_rejects_bad_tier():
    with pytest.raises(ValueError):
        TOIDocumentGenerator.from_defaults(author="alice", tier="nope")


def test_from_dict_merges_over_defaults():
    gen = TOIDocumentGenerator.from_dict(
        {"communication": {"tone": "friendly"}, "privacy": {"retention": "long-term"}},
        author="bob",
    )
    assert gen.document["communication"]["tone"] == "friendly"
    assert gen.document["privacy"]["retention"] == "long-term"
    # Untouched defaults survive the merge.
    assert gen.document["privacy"]["cross_platform_sharing"] == "never"
    assert gen.document["identity"]["author"] == "bob"
    assert is_toi(gen.document) is True


def test_from_dict_falls_back_to_anonymous_author():
    gen = TOIDocumentGenerator.from_dict({"communication": {"tone": "friendly"}})
    assert gen.document["identity"]["author"] == "anonymous"
    assert is_toi(gen.document) is True


def test_from_dict_preserves_input_tier_when_not_overridden():
    gen = TOIDocumentGenerator.from_dict(
        {"$toi": "1.0.0", "$tier": "community", "identity": {"author": "alice"}}
    )
    assert gen.document["$tier"] == "community"


def test_from_dict_explicit_tier_overrides_input_tier():
    gen = TOIDocumentGenerator.from_dict(
        {"$toi": "1.0.0", "$tier": "community", "identity": {"author": "alice"}},
        tier="project",
    )
    assert gen.document["$tier"] == "project"


def test_from_dict_rejects_invalid_enum():
    with pytest.raises(ToiValidationError):
        TOIDocumentGenerator.from_dict({"communication": {"tone": "gibberish"}}, author="bob")


def test_from_dict_strips_stale_signature_from_signed_input() -> None:
    """Verify that from_dict strips a stale signature from signed input."""
    keys = generate_key_pair()
    signed = sign_toi(
        {"$toi": "1.0.0", "$tier": "personal", "identity": {"author": "alice"}},
        keys.private_key,
    )
    assert is_signed(signed)
    gen = TOIDocumentGenerator.from_dict(signed)
    assert "$signature" not in gen.document
    assert is_signed(gen.document) is False


def test_to_json_round_trips_through_parse():
    gen = TOIDocumentGenerator.from_defaults(author="alice")
    raw = gen.to_json()
    assert raw.endswith("\n")
    assert parse_toi(raw) == parse_toi(gen.to_dict())


def test_to_markdown_includes_preferences():
    md = TOIDocumentGenerator.from_defaults(author="alice").to_markdown()
    assert "# Terms of Interaction" in md
    assert "alice" in md
    assert "Privacy and data" in md
    assert "Session-Only" in md
    assert "Communication" in md


def test_to_dict_is_a_copy():
    gen = TOIDocumentGenerator.from_defaults(author="alice")
    snapshot = gen.to_dict()
    snapshot["identity"]["author"] = "mutated"
    assert gen.document["identity"]["author"] == "alice"


def test_write_emits_valid_json(tmp_path):
    out = tmp_path / "me.toi"
    TOIDocumentGenerator.from_defaults(author="alice").write(str(out))
    assert out.read_text(encoding="utf-8").endswith("\n")
    assert parse_toi(out.read_text(encoding="utf-8"))["identity"]["author"] == "alice"


def test_validate_mutates_document_to_parsed_form():
    gen = TOIDocumentGenerator.from_dict({"communication": {"tone": "casual"}}, author="alice")
    returned = gen.validate()
    assert returned is gen


def test_default_document_is_stable_skeleton():
    assert DEFAULT_DOCUMENT["$toi"] == "1.0.0"
    assert set(DEFAULT_DOCUMENT["privacy"].keys()) >= {
        "retention",
        "cross_platform_sharing",
        "training_use",
        "analytics",
        "override_rights",
        "data_requests",
    }
    assert json.dumps(DEFAULT_DOCUMENT)  # serializable