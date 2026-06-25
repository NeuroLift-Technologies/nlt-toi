"""Ed25519 sign / verify behavior, including the committed known-answer fixture
(ported from sign.test.ts). The known-answer fixture was produced by the
TypeScript reference, so verifying it here is the cross-implementation proof."""
from __future__ import annotations

import copy
import math

from nlt_toi import (
    canonicalize,
    generate_key_pair,
    is_signed,
    parse_toi,
    sign_toi,
    signing_payload,
    verify_toi,
)
from tests.conftest import VALID_DIR


def _load_valid(name: str):
    return parse_toi((VALID_DIR / name).read_text(encoding="utf-8"))


def test_round_trips_sign_then_verify():
    keys = generate_key_pair()
    signed = sign_toi(_load_valid("josh-personal.toi"), keys.private_key)
    assert is_signed(signed) is True
    assert signed["$signature"]["alg"] == "ed25519"
    assert verify_toi(signed) is True


def test_detects_tampering_with_signed_content():
    keys = generate_key_pair()
    signed = sign_toi(_load_valid("minimal.toi"), keys.private_key)
    tampered = copy.deepcopy(signed)
    tampered["identity"]["author"] = "someone else"
    assert verify_toi(tampered) is False


def test_is_stable_across_reformatting_and_key_reordering():
    keys = generate_key_pair()
    signed = sign_toi(_load_valid("full-coverage.toi"), keys.private_key)
    # Rebuild the dict in a scrambled key order; canonical payload is unchanged.
    shuffled = json_reorder(signed)
    assert verify_toi(shuffled) is True


def json_reorder(doc):
    import json

    keys = list(doc.keys())
    reordered = {k: doc[k] for k in reversed(keys)}
    return json.loads(json.dumps(reordered))


def test_signs_over_canonical_form_with_signature_removed():
    keys = generate_key_pair()
    doc = _load_valid("minimal.toi")
    signed = sign_toi(doc, keys.private_key)
    assert signing_payload(signed).decode("utf-8") == canonicalize(doc)


def test_verifies_committed_known_answer_fixture():
    signed = _load_valid("signed.toi")
    assert verify_toi(signed) is True
    assert signed["$signature"]["public_key"] == "ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmQ"


def test_treats_unsigned_documents_as_unverified_not_errors():
    doc = _load_valid("minimal.toi")
    assert is_signed(doc) is False
    assert verify_toi(doc) is False


def test_rejects_a_wrong_public_key():
    keys = generate_key_pair()
    signed = sign_toi(_load_valid("minimal.toi"), keys.private_key)
    other = generate_key_pair()
    swapped = {**signed, "$signature": {**signed["$signature"], "public_key": other.public_key_base64url}}
    assert verify_toi(swapped) is False


def test_returns_false_never_throws_for_malformed_base64url():
    keys = generate_key_pair()
    signed = sign_toi(_load_valid("minimal.toi"), keys.private_key)
    malformed = {**signed, "$signature": {**signed["$signature"], "value": "@@@"}}
    assert verify_toi(malformed) is False


def test_rejects_padded_or_whitespaced_base64url():
    keys = generate_key_pair()
    signed = sign_toi(_load_valid("minimal.toi"), keys.private_key)
    padded = {**signed, "$signature": {**signed["$signature"], "value": signed["$signature"]["value"] + "="}}
    spaced = {**signed, "$signature": {**signed["$signature"], "public_key": " " + signed["$signature"]["public_key"]}}
    assert verify_toi(padded) is False
    assert verify_toi(spaced) is False


def test_returns_false_when_document_cannot_be_canonicalized():
    keys = generate_key_pair()
    signed = sign_toi(_load_valid("minimal.toi"), keys.private_key)
    broken = {**signed, "custom": {"bad": math.inf}}
    assert verify_toi(broken) is False
