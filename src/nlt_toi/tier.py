"""Tier precedence and resolution (§9 of the spec).

Resolution order, highest first: personal > community > project > platform
defaults. A ``personal``-tier file is terminal — any field it specifies cannot be
overridden by a lower tier or by platform defaults.

:func:`resolve_toi` is the precedence *primitive*: it folds several single-tier
documents into one effective view. Full multi-agent orchestration (how an agent
mesh honors that view) is the ``.otoi`` layer's job, not this one.
"""
from __future__ import annotations

import copy
from typing import Any, Dict, List, Mapping, Optional, Sequence

from .constants import TIER_RANK, TOI_RESERVED_PREFIX
from .errors import ToiTierError
from .parse import ToiDocument


def _tier_rank(tier: str) -> int:
    """Numeric rank for *tier*, raising the library's own error for unknown tiers."""
    try:
        return TIER_RANK[tier]
    except KeyError as exc:
        raise ToiTierError(f"Unknown tier: {tier!r}") from exc


def compare_tier(a: str, b: str) -> int:
    """Compare two tiers by precedence. Negative means *a* outranks *b*."""
    return _tier_rank(a) - _tier_rank(b)


def sort_by_precedence(documents: Sequence[ToiDocument]) -> List[ToiDocument]:
    """Return a copy of *documents* ordered highest-precedence first."""
    return sorted(documents, key=lambda d: _tier_rank(d["$tier"]))


def resolve_toi(
    documents: Sequence[ToiDocument],
    platform_defaults: Optional[Mapping[str, Any]] = None,
) -> ToiDocument:
    """Fold one or more single-tier documents into one effective document.

    Merge semantics implement terminal precedence: documents are processed
    highest-tier first, and a field already set by a higher tier is never
    overwritten. Nested objects are deep-filled (a lower tier may supply leaves a
    higher tier left unspecified); arrays and scalars are atomic leaves.

    The result carries the highest tier's ``$toi`` and ``$tier``; per-file
    metadata (``$id``, ``$created``, ``$signature``, …) is intentionally not
    merged, because a synthesized view is not itself a signed source document.

    Raises:
        ToiTierError: if *documents* is empty.
    """
    if not documents:
        raise ToiTierError("resolve_toi requires at least one document")
    ordered = sort_by_precedence(documents)
    top = ordered[0]

    result: Dict[str, Any] = {"$toi": top["$toi"], "$tier": top["$tier"]}
    for doc in ordered:
        _fill_into(result, _strip_reserved(doc))
    if platform_defaults:
        _fill_into(result, platform_defaults)
    return result


def _strip_reserved(doc: Mapping[str, Any]) -> Dict[str, Any]:
    # Exclude the whole reserved namespace ($-prefixed) — including unknown future
    # reserved keys — so per-file metadata never leaks into the effective view.
    return {k: v for k, v in doc.items() if not k.startswith(TOI_RESERVED_PREFIX)}


def _fill_into(target: Dict[str, Any], source: Mapping[str, Any]) -> None:
    """Copy keys from *source* into *target* without overwriting set leaves.

    JSON ``null`` (Python ``None``) is a *set leaf*, not "missing": the reference
    implementation only skips JS ``undefined`` (which has no Python equivalent —
    an unset field is simply an absent key). So a higher tier that sets a field to
    ``null`` keeps it, and a present key is never refilled by a lower tier.
    """
    for key, source_value in source.items():
        target_value = target.get(key)
        if isinstance(target_value, dict) and isinstance(source_value, dict):
            _fill_into(target_value, source_value)
        elif key not in target:
            target[key] = copy.deepcopy(source_value)
