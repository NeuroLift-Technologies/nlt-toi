"""Context preservation primitives for NeuroLift multi-agent workflows.

This module demonstrates how to capture, version, and share context between
agents while keeping user overrides authoritative. The implementation favors a
functional style so that state transitions and metadata annotations are easy to
reason about and audit.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence


@dataclass(frozen=True)
class ContextSlice:
    """Immutable snapshot of agent-relevant state.

    Attributes:
        topic: Human-legible label (e.g., "neurofeedback-session").
        payload: Arbitrary structured data that the receiving agent understands.
        created_at: Timestamp used for ordering and TTL logic.
        tags: Optional affordance markers ("focus", "requires-user-confirmation").
        provenance: Structured origin metadata (agent name, tool, prompt hash).
    """

    topic: str
    payload: Dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "payload": self.payload,
            "created_at": self.created_at.isoformat(),
            "tags": list(self.tags),
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextSlice":
        created = data.get("created_at")
        created_at = (
            datetime.fromisoformat(created) if isinstance(created, str) else datetime.now(timezone.utc)
        )
        return cls(
            topic=data["topic"],
            payload=data.get("payload", {}),
            created_at=created_at,
            tags=list(data.get("tags", [])),
            provenance=data.get("provenance", {}),
        )


@dataclass(frozen=True)
class ContextCapsule:
    """Bundle of slices plus cursor + metadata to support incremental handoffs."""

    slices: List[ContextSlice]
    cursor: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def filter_by_tag(self, tag: str) -> "ContextCapsule":
        """Return a new capsule containing only slices with a given tag."""
        filtered = [slice_ for slice_ in self.slices if tag in slice_.tags]
        return replace(self, slices=filtered)

    def with_cursor(self, cursor: Optional[str]) -> "ContextCapsule":
        """Return a new capsule with the cursor updated."""

        return replace(self, cursor=cursor)

    def with_metadata(self, **fields: Any) -> "ContextCapsule":
        """Return a capsule with metadata merged in a functional style."""

        merged = {**self.metadata, **fields}
        return replace(self, metadata=merged)

    def append(self, slice_: ContextSlice, *, dedupe: bool = True) -> "ContextCapsule":
        """Return a capsule with the slice appended.

        Args:
            slice_: Context to append.
            dedupe: When True, de-duplicates payloads that share topic + provenance.
        """

        if not dedupe:
            return replace(self, slices=[*self.slices, slice_])

        def unique_key(item: ContextSlice) -> tuple[str, str]:
            return (item.topic, item.provenance.get("agent", ""))

        seen = {unique_key(s): s for s in self.slices}
        seen[unique_key(slice_)] = slice_
        return replace(self, slices=list(seen.values()))

    def diff(self, other: "ContextCapsule") -> Dict[str, Iterable[ContextSlice]]:
        """Produce slices that were added or removed compared to another capsule."""
        current_keys = {(s.topic, s.created_at) for s in self.slices}
        other_keys = {(s.topic, s.created_at) for s in other.slices}

        added = [s for s in self.slices if (s.topic, s.created_at) not in other_keys]
        removed = [s for s in other.slices if (s.topic, s.created_at) not in current_keys]
        return {"added": added, "removed": removed}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slices": [slice_.to_dict() for slice_ in self.slices],
            "cursor": self.cursor,
            "metadata": self.metadata,
        }

    @classmethod
    def from_slices(
        cls,
        slices: Sequence[ContextSlice],
        *,
        cursor: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "ContextCapsule":
        return cls(list(slices), cursor=cursor, metadata=metadata or {})

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextCapsule":
        slices = [ContextSlice.from_dict(item) for item in data.get("slices", [])]
        return cls(
            slices,
            cursor=data.get("cursor"),
            metadata=data.get("metadata", {}),
        )


def merge_capsules(*capsules: ContextCapsule) -> ContextCapsule:
    """Combine capsules, preferring the most recent slice per topic."""
    latest: Dict[str, ContextSlice] = {}
    cursor: Optional[str] = None
    combined_metadata: Dict[str, Any] = {}
    for capsule in capsules:
        for slice_ in capsule.slices:
            existing = latest.get(slice_.topic)
            if not existing or existing.created_at < slice_.created_at:
                latest[slice_.topic] = slice_
        if capsule.cursor is not None:
            cursor = capsule.cursor
        combined_metadata.update(capsule.metadata)
    merged = sorted(latest.values(), key=lambda item: item.created_at)
    return ContextCapsule(slices=merged, cursor=cursor, metadata=combined_metadata)


def prune_by_ttl(capsule: ContextCapsule, *, seconds: int) -> ContextCapsule:
    """Remove slices older than the TTL, preserving focus for current thread."""
    cutoff = datetime.now(timezone.utc).timestamp() - seconds
    retained = [
        slice_
        for slice_ in capsule.slices
        if slice_.created_at.timestamp() >= cutoff or "pinned" in slice_.tags
    ]
    return ContextCapsule(slices=retained, cursor=capsule.cursor, metadata=capsule.metadata)


__all__ = [
    "ContextSlice",
    "ContextCapsule",
    "merge_capsules",
    "prune_by_ttl",
]
