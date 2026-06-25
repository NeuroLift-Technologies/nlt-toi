"""``nlt_toi`` — Python reference implementation of the ``.toi`` (Terms of
Interaction) standard file type, ported from ``@neurolift-technologies/toi``.

The on-disk format, RFC 8785 canonicalization, and Ed25519 signature envelope are
identical to the TypeScript reference, so a document signed by one implementation
verifies in the other.

Example::

    from nlt_toi import parse_toi, sign_toi, verify_toi, generate_key_pair

    doc = parse_toi(open("me.toi", encoding="utf-8").read())
    keys = generate_key_pair()
    signed = sign_toi(doc, keys.private_key)
    verify_toi(signed)  # -> True
"""
from __future__ import annotations

from .canonicalize import JsonValue, canonicalize, canonicalize_to_bytes
from .constants import (
    TIER_PRECEDENCE,
    TIER_RANK,
    TOI_FILE_EXTENSION,
    TOI_FORMAT_VERSION,
    TOI_MEDIA_TYPE,
    TOI_RESERVED_KEYS,
    TOI_RESERVED_PREFIX,
    TOI_TIERS,
)
from .errors import (
    ToiCanonicalizationError,
    ToiError,
    ToiErrorCode,
    ToiIssue,
    ToiParseError,
    ToiSignatureError,
    ToiTierError,
    ToiValidationError,
)
from .parse import (
    SafeParseResult,
    ToiDocument,
    is_toi,
    parse_toi,
    safe_parse_toi,
    serialize_toi,
)
from .schema import schema_issues, toi_schema
from .sign import (
    ToiKeyPair,
    generate_key_pair,
    is_signed,
    sign_toi,
    signing_payload,
    verify_toi,
)
from .tier import compare_tier, resolve_toi, sort_by_precedence

__version__ = "1.0.0"

__all__ = [
    # constants / tier model
    "TOI_FORMAT_VERSION",
    "TOI_FILE_EXTENSION",
    "TOI_MEDIA_TYPE",
    "TOI_RESERVED_PREFIX",
    "TOI_RESERVED_KEYS",
    "TOI_TIERS",
    "TIER_PRECEDENCE",
    "TIER_RANK",
    # schema + types
    "toi_schema",
    "schema_issues",
    "ToiDocument",
    # parse / validate / serialize
    "parse_toi",
    "safe_parse_toi",
    "is_toi",
    "serialize_toi",
    "SafeParseResult",
    # canonicalization
    "canonicalize",
    "canonicalize_to_bytes",
    "JsonValue",
    # signing / verification
    "generate_key_pair",
    "sign_toi",
    "verify_toi",
    "is_signed",
    "signing_payload",
    "ToiKeyPair",
    # tier resolution
    "resolve_toi",
    "sort_by_precedence",
    "compare_tier",
    # errors
    "ToiError",
    "ToiParseError",
    "ToiValidationError",
    "ToiCanonicalizationError",
    "ToiSignatureError",
    "ToiTierError",
    "ToiErrorCode",
    "ToiIssue",
    "__version__",
]
