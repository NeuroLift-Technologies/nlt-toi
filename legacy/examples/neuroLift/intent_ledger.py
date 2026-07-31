"""Intent ledger primitives for NeuroLift Thread B workflows.

The ledger keeps Josh in control by making every interpretation explicit and
editable. Entries are append-only, timestamped, and scoreable so the guardian
layer can detect drift or degraded handoffs.
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, MutableMapping, Optional
from uuid import uuid4

Status = str


@dataclass
class IntentEntry:
    """Represents one user intent or agent interpretation."""

    intent_id: str
    agent: str
    task: str
    status: Status = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    capsule_cursor: Optional[str] = None
    thread_id: Optional[str] = None
    score: Optional[float] = None
    notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_note(self, note: str) -> None:
        self.notes.append(note)
        self.updated_at = datetime.now(timezone.utc)

    def set_status(self, status: Status, *, score: Optional[float] = None) -> None:
        self.status = status
        if score is not None:
            self.score = score
        self.updated_at = datetime.now(timezone.utc)

    def merge_metadata(self, metadata: Dict[str, Any]) -> None:
        if metadata:
            self.metadata.update(metadata)
            self.updated_at = datetime.now(timezone.utc)


class IntentLedger:
    """Append-only ledger for agent handoffs and user overrides."""

    def __init__(self) -> None:
        self._entries: MutableMapping[str, IntentEntry] = OrderedDict()

    # region recording -----------------------------------------------------------------
    def record(
        self,
        *,
        agent: str,
        task: str,
        capsule_cursor: Optional[str],
        thread_id: Optional[str],
        metadata: Optional[Dict[str, Any]] = None,
        intent_id: Optional[str] = None,
    ) -> IntentEntry:
        """Add a new ledger entry with ``pending`` status."""

        entry_id = intent_id or uuid4().hex
        entry = IntentEntry(
            intent_id=entry_id,
            agent=agent,
            task=task,
            capsule_cursor=capsule_cursor,
            thread_id=thread_id,
        )
        if metadata:
            entry.merge_metadata(metadata)
        self._entries[entry_id] = entry
        return entry

    def acknowledge(
        self,
        intent_id: str,
        *,
        note: Optional[str] = None,
        status: Status = "acknowledged",
        score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> IntentEntry:
        """Mark an entry as acknowledged and optionally attach score + note."""

        entry = self._require(intent_id)
        entry.set_status(status, score=score)
        if note:
            entry.add_note(note)
        if metadata:
            entry.merge_metadata(metadata)
        return entry

    def flag(
        self,
        intent_id: str,
        *,
        note: str,
        metadata: Optional[Dict[str, Any]] = None,
        status: Status = "flagged",
    ) -> IntentEntry:
        """Flag an entry that needs review by the human orchestrator."""

        entry = self._require(intent_id)
        entry.set_status(status)
        entry.add_note(note)
        if metadata:
            entry.merge_metadata(metadata)
        return entry

    def override(
        self,
        intent_id: str,
        *,
        replacement_task: Optional[str] = None,
        note: Optional[str] = None,
    ) -> IntentEntry:
        """Record a human override and keep history intact."""

        entry = self._require(intent_id)
        entry.set_status("overridden")
        if replacement_task:
            entry.metadata["replacement_task"] = replacement_task
        if note:
            entry.add_note(note)
        return entry

    # endregion ------------------------------------------------------------------------

    def get(self, intent_id: str) -> IntentEntry:
        return self._require(intent_id)

    def to_list(self) -> List[IntentEntry]:
        return list(self._entries.values())

    def export_thread(self, thread_id: str) -> List[IntentEntry]:
        return [entry for entry in self._entries.values() if entry.thread_id == thread_id]

    def __len__(self) -> int:  # pragma: no cover - simple delegation
        return len(self._entries)

    def __iter__(self) -> Iterable[IntentEntry]:  # pragma: no cover - simple delegation
        return iter(self._entries.values())

    def _require(self, intent_id: str) -> IntentEntry:
        try:
            return self._entries[intent_id]
        except KeyError as exc:  # pragma: no cover - defensive branch
            raise KeyError(f"Unknown intent_id '{intent_id}'") from exc


__all__ = ["IntentEntry", "IntentLedger"]
