"""Ed25519 signing and verification over the RFC 8785 canonical form.

The signed payload is always ``canonicalize(document without $signature)`` encoded
as UTF-8. Because canonicalization is order- and formatting-independent, a
signature survives reformatting, key reordering, and round-tripping through any
conformant parser — and interoperates with the reference TypeScript
implementation (a token signed by one verifies in the other).

Crypto is provided by the audited ``cryptography`` library; keys are raw 32-byte
Ed25519 seeds / public points, matching the ``$signature`` envelope (SPEC §11).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .b64url import base64url_to_bytes, bytes_to_base64url
from .canonicalize import canonicalize_to_bytes
from .errors import ToiSignatureError
from .parse import ToiDocument, parse_toi

#: SPEC §11.1: signature fields are unpadded base64url — no ``=`` padding, no whitespace.
_UNPADDED_BASE64URL = re.compile(r"^[A-Za-z0-9_-]+$")

_RAW = serialization.Encoding.Raw
_RAW_PRIVATE = serialization.PrivateFormat.Raw
_RAW_PUBLIC = serialization.PublicFormat.Raw
_NO_ENCRYPTION = serialization.NoEncryption()


@dataclass(frozen=True)
class ToiKeyPair:
    """An Ed25519 key pair. Keys are raw 32-byte seeds / public points."""

    #: 32-byte Ed25519 private seed. Keep secret; never write it into a ``.toi`` file.
    private_key: bytes
    #: 32-byte Ed25519 public key.
    public_key: bytes
    #: The public key as base64url — the form stored in ``$signature.public_key``.
    public_key_base64url: str


def generate_key_pair() -> ToiKeyPair:
    """Generate a fresh Ed25519 key pair."""
    private = Ed25519PrivateKey.generate()
    private_bytes = private.private_bytes(_RAW, _RAW_PRIVATE, _NO_ENCRYPTION)
    public_bytes = private.public_key().public_bytes(_RAW, _RAW_PUBLIC)
    return ToiKeyPair(private_bytes, public_bytes, bytes_to_base64url(public_bytes))


def signing_payload(doc: ToiDocument) -> bytes:
    """The exact bytes that get signed: the canonical form with ``$signature`` removed."""
    return canonicalize_to_bytes(_without_signature(doc))


def is_signed(doc: Any) -> bool:
    """``True`` when *doc* carries a ``$signature`` envelope (not a validity claim)."""
    return _is_plain_object(doc) and _is_plain_object(doc.get("$signature"))


def sign_toi(doc: ToiDocument, private_key: bytes) -> ToiDocument:
    """Sign a document, returning a copy with a populated ``$signature`` field.

    The input is validated first, so signing a malformed document raises.

    Raises:
        ToiValidationError: if *doc* is not a valid ``.toi`` document.
        ToiCanonicalizationError: if *doc* holds values not representable as
            canonical JSON.
        ToiSignatureError: if the cryptographic operation fails.
    """
    validated = parse_toi(doc)
    unsigned = _without_signature(validated)
    payload = canonicalize_to_bytes(unsigned)
    try:
        private = Ed25519PrivateKey.from_private_bytes(private_key)
        signature = private.sign(payload)
        public_bytes = private.public_key().public_bytes(_RAW, _RAW_PUBLIC)
    except Exception as err:  # noqa: BLE001 — wrapped into the library's taxonomy
        raise ToiSignatureError("Failed to sign .toi document") from err
    unsigned["$signature"] = {
        "alg": "ed25519",
        "public_key": bytes_to_base64url(public_bytes),
        "value": bytes_to_base64url(signature),
    }
    return unsigned


def verify_toi(doc: ToiDocument) -> bool:
    """Verify a document's embedded ``$signature`` against its canonical payload.

    Fully defensive: returns ``False`` for a missing, malformed, undecodable, or
    non-matching signature, and never raises.
    """
    if not _is_plain_object(doc):
        return False
    raw = doc.get("$signature")
    if not _is_plain_object(raw):
        return False
    if raw.get("alg") != "ed25519":
        return False
    public_key_b64 = raw.get("public_key")
    value_b64 = raw.get("value")
    if not isinstance(public_key_b64, str) or not isinstance(value_b64, str):
        return False
    # SPEC §11.1: reject padded / whitespaced encodings rather than normalizing them.
    if not _UNPADDED_BASE64URL.match(public_key_b64) or not _UNPADDED_BASE64URL.match(value_b64):
        return False
    try:
        public_bytes = base64url_to_bytes(public_key_b64)
        signature = base64url_to_bytes(value_b64)
    except ValueError:
        return False
    try:
        payload = canonicalize_to_bytes(_without_signature(doc))
        Ed25519PublicKey.from_public_bytes(public_bytes).verify(signature, payload)
        return True
    except Exception:  # noqa: BLE001 — un-canonicalizable content / bad key bytes / mismatch: not verifiable
        return False


def _without_signature(doc: ToiDocument) -> ToiDocument:
    return {key: value for key, value in doc.items() if key != "$signature"}


def _is_plain_object(value: Any) -> bool:
    return isinstance(value, dict)
