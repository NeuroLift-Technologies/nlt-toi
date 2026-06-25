"""Canonical constants for the ``.toi`` standard file type.

These values are normative and mirror the reference implementation
(``@neurolift-technologies/toi``). Downstream consumers (e.g. the ``.otoi``
honoring layer) should import them rather than re-declaring literals.
"""
from __future__ import annotations

from typing import Dict, Tuple

#: Format version of the ``.toi`` specification this library implements.
TOI_FORMAT_VERSION = "1.0.0"

#: Canonical file extension for Terms of Interaction documents.
TOI_FILE_EXTENSION = ".toi"

#: Registered media (MIME) type — structured-syntax suffix form per RFC 6839.
TOI_MEDIA_TYPE = "application/toi+json"

#: Prefix marking the reserved namespace. Every ``$``-prefixed key is reserved.
TOI_RESERVED_PREFIX = "$"

#: The reserved top-level keys defined by v1.0.0. Keys outside this set that
#: still begin with ``$`` are reserved for future use (author data → ``custom``).
TOI_RESERVED_KEYS: Tuple[str, ...] = (
    "$toi",
    "$tier",
    "$created",
    "$updated",
    "$id",
    "$license",
    "$signature",
)

#: The three interaction tiers, in descending order of precedence.
TOI_TIERS: Tuple[str, ...] = ("personal", "community", "project")

#: Tier precedence, highest first. A ``personal``-tier file is terminal.
TIER_PRECEDENCE: Tuple[str, ...] = TOI_TIERS

#: Numeric rank for each tier — lower number means higher precedence.
TIER_RANK: Dict[str, int] = {"personal": 0, "community": 1, "project": 2}
