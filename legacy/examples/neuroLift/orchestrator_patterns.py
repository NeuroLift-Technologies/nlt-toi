"""Prototype orchestrator + handoff patterns for NeuroLift agents.

Provides four building blocks:
1. `AgentRegistry` – declarative capability mapping with affordance metadata.
2. `Orchestrator` – central router for Thread A experiments with intent ledger integration.
3. `HandoffRecord`/`DispatchOutcome` – immutable audit artifacts for Thread B.
4. `EventRelay` – lightweight async bus aligning with Thread B memory flow.

The code is annotated so Josh can remix components quickly. Each class exposes
observability hooks to keep agent actions legible and neurodivergent-friendly.
"""
from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Optional, Protocol
from uuid import uuid4

from .context_capsule import ContextCapsule, ContextSlice, merge_capsules, prune_by_ttl

if TYPE_CHECKING:  # pragma: no cover - support optional intent ledger dependency
    from .intent_ledger import IntentLedger


class AgentCallable(Protocol):
    async def __call__(self, capsule: ContextCapsule, *, task: str) -> ContextCapsule:
        ...


@dataclass
class AgentRegistration:
    name: str
    entrypoint: AgentCallable
    modalities: List[str] = field(default_factory=list)
    affordances: List[str] = field(default_factory=list)
    guardrails: Dict[str, Any] = field(default_factory=dict)


class AgentRegistry:
    """Registry with affordance-aware agent lookup."""

    def __init__(self) -> None:
        self._agents: Dict[str, AgentRegistration] = {}

    def register(self, registration: AgentRegistration) -> None:
        if registration.name in self._agents:
            raise ValueError(f"Agent '{registration.name}' already registered")
        self._agents[registration.name] = registration

    def get(self, name: str) -> AgentRegistration:
        return self._agents[name]

    def suggest(self, *, modality: Optional[str] = None, affordance: Optional[str] = None) -> List[AgentRegistration]:
        candidates = self._agents.values()
        if modality:
            candidates = [agent for agent in candidates if modality in agent.modalities]
        if affordance:
            candidates = [agent for agent in candidates if affordance in agent.affordances]
        return list(candidates)


@dataclass
class HandoffRecord:
    """Structured log entry describing a single agent dispatch."""

    intent_id: str
    agent: str
    task: str
    thread_id: Optional[str]
    before_cursor: Optional[str]
    after_cursor: Optional[str] = None
    added: int = 0
    removed: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def finalize(
        self,
        *,
        after_cursor: Optional[str],
        added: int,
        removed: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update the record after the agent completes."""

        self.after_cursor = after_cursor
        self.added = added
        self.removed = removed
        if metadata:
            self.metadata.update(metadata)
        self.completed_at = datetime.now(timezone.utc)


@dataclass
class DispatchOutcome:
    """Return value for orchestrator dispatch with audit metadata."""

    capsule: ContextCapsule
    record: HandoffRecord


class Orchestrator:
    """Thread A style orchestrator with explicit handoff records and scoring."""

    def __init__(self, registry: AgentRegistry, *, ledger: Optional["IntentLedger"] = None) -> None:
        self.registry = registry
        self.handoff_log: List[HandoffRecord] = []
        self.ledger = ledger

    async def dispatch(
        self,
        agent_name: str,
        capsule: ContextCapsule,
        *,
        task: str,
        thread_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        return_record: bool = False,
    ) -> ContextCapsule | DispatchOutcome:
        registration = self.registry.get(agent_name)
        extra_metadata = metadata.copy() if metadata else {}

        ledger_entry = None
        if self.ledger is not None:
            ledger_entry = self.ledger.record(
                agent=agent_name,
                task=task,
                capsule_cursor=capsule.cursor,
                thread_id=thread_id,
                metadata=extra_metadata,
            )
            intent_id = ledger_entry.intent_id
        else:
            intent_id = extra_metadata.get("intent_id", f"handoff-{uuid4().hex}")

        record = HandoffRecord(
            intent_id=intent_id,
            agent=agent_name,
            task=task,
            thread_id=thread_id,
            before_cursor=capsule.cursor,
            metadata=extra_metadata,
        )

        updated = await registration.entrypoint(capsule, task=task)
        merged = merge_capsules(capsule, updated).with_metadata(**extra_metadata)
        merged = prune_by_ttl(merged, seconds=900)
        diff = merged.diff(capsule)
        added = len(diff["added"])
        removed = len(diff["removed"])
        record.finalize(after_cursor=merged.cursor, added=added, removed=removed, metadata=extra_metadata)
        self.handoff_log.append(record)

        if self.ledger is not None:
            score = _score_handoff(added=added, removed=removed)
            note = extra_metadata.get("note")
            self.ledger.acknowledge(
                intent_id,
                score=score,
                note=note or _default_note(record),
                metadata={"diff": {"added": added, "removed": removed}},
            )

        if return_record:
            return DispatchOutcome(capsule=merged, record=record)
        return merged


class EventRelay:
    """Minimal async pub/sub to support Thread B shared memory experiments."""

    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[[ContextSlice], Awaitable[None]]]] = defaultdict(list)
        self._any_topic: List[Callable[[ContextSlice], Awaitable[None]]] = []

    def subscribe(
        self,
        topic: Optional[str],
        handler: Callable[[ContextSlice], Awaitable[None]],
    ) -> None:
        """Subscribe to a specific topic or all topics when topic is ``None``."""

        if topic is None:
            self._any_topic.append(handler)
        else:
            self._listeners[topic].append(handler)

    async def publish(self, slice_: ContextSlice) -> None:
        tasks = [listener(slice_) for listener in self._listeners[slice_.topic]]
        tasks.extend(listener(slice_) for listener in self._any_topic)
        if tasks:
            await asyncio.gather(*tasks)

    def topics(self) -> List[str]:
        """Return known topics to help drive UI affordances."""

        return sorted(self._listeners.keys())


async def focus_agent(capsule: ContextCapsule, *, task: str) -> ContextCapsule:
    """Example agent that surfaces the most relevant slice for the user."""
    focus_slice = ContextSlice(
        topic="focus-summary",
        payload={"task": task, "highlights": [s.topic for s in capsule.slices[-3:]]},
        tags=["focus", "user-facing"],
        provenance={"agent": "focus-agent"},
    )
    return ContextCapsule([focus_slice])


async def guardian_agent(capsule: ContextCapsule, *, task: str) -> ContextCapsule:
    """Example guardian that flags actions needing confirmation."""
    alerts: List[ContextSlice] = []
    for slice_ in capsule.slices:
        if slice_.provenance.get("requires-confirmation"):
            alerts.append(
                ContextSlice(
                    topic="guardian-alert",
                    payload={"reason": "requires-confirmation", "source": slice_.topic},
                    tags=["pinned", "requires-user-confirmation"],
                    provenance={"agent": "guardian"},
                )
            )
    return ContextCapsule(alerts)


def build_default_registry() -> AgentRegistry:
    registry = AgentRegistry()
    registry.register(
        AgentRegistration(
            name="focus-agent",
            entrypoint=focus_agent,
            modalities=["text"],
            affordances=["summarize", "attention-support"],
        )
    )
    registry.register(
        AgentRegistration(
            name="guardian",
            entrypoint=guardian_agent,
            modalities=["text"],
            affordances=["safety", "oversight"],
        )
    )
    return registry


__all__ = [
    "AgentRegistry",
    "AgentRegistration",
    "DispatchOutcome",
    "HandoffRecord",
    "Orchestrator",
    "EventRelay",
    "build_default_registry",
    "focus_agent",
    "guardian_agent",
]


def _score_handoff(*, added: int, removed: int) -> float:
    """Rudimentary score for a handoff to expose quick quality heuristics."""

    base = 0.4
    base += min(0.5, added * 0.2)
    base -= min(0.3, removed * 0.15)
    return round(max(0.0, min(1.0, base)), 2)


def _default_note(record: HandoffRecord) -> str:
    if record.added and not record.removed:
        return "New slices appended"
    if record.added and record.removed:
        return "Context refreshed"
    if not record.added and record.removed:
        return "Slices pruned for focus"
    return "No capsule change"
