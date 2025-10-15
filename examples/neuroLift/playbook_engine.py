"""Composable playbook runner for NeuroLift Thread C workflows."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Sequence, Union

from .context_capsule import ContextCapsule
from .intent_ledger import IntentLedger
from .orchestrator_patterns import AgentRegistry, HandoffRecord, Orchestrator

GuardianHook = Callable[["TimelineEvent", ContextCapsule], Awaitable[None]]


@dataclass(frozen=True)
class PlaybookStep:
    """Single step in a playbook."""

    agent: str
    task: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    require_confirmation: bool = False
    focus_tag: Optional[str] = None


@dataclass
class Playbook:
    """Sequence of steps with shared metadata."""

    name: str
    steps: Sequence[Union[PlaybookStep, Dict[str, Any]]]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized: List[PlaybookStep] = []
        for step in self.steps:
            if isinstance(step, PlaybookStep):
                normalized.append(step)
            else:
                normalized.append(PlaybookStep(**step))
        object.__setattr__(self, "steps", tuple(normalized))

    def iter_steps(self) -> Iterable[PlaybookStep]:
        return iter(self.steps)


@dataclass
class TimelineEvent:
    """Audit artifact linking a step to the resulting handoff."""

    playbook_name: str
    step_index: int
    step: PlaybookStep
    record: HandoffRecord
    started_at: datetime
    completed_at: datetime
    notes: Dict[str, Any] = field(default_factory=dict)


class PlaybookEngine:
    """Coordinates orchestrator dispatches with guardian hooks."""

    def __init__(
        self,
        *,
        registry: AgentRegistry,
        ledger: Optional[IntentLedger] = None,
        orchestrator: Optional[Orchestrator] = None,
    ) -> None:
        self.registry = registry
        self.ledger = ledger or IntentLedger()
        self.orchestrator = orchestrator or Orchestrator(registry, ledger=self.ledger)
        self.timeline: List[TimelineEvent] = []
        self._guardian_hooks: List[GuardianHook] = []

    def register_guardian(self, hook: GuardianHook) -> None:
        """Register a coroutine hook that runs when confirmation is required."""

        self._guardian_hooks.append(hook)

    async def run(
        self,
        playbook: Union[Playbook, Dict[str, Any]],
        *,
        capsule: ContextCapsule,
        thread_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ContextCapsule:
        """Execute the playbook sequentially and return the final capsule."""

        normalized = playbook if isinstance(playbook, Playbook) else Playbook(**playbook)
        shared_metadata = metadata.copy() if metadata else {}
        self.timeline.clear()
        current = capsule

        for index, step in enumerate(normalized.iter_steps()):
            step_metadata = {
                "playbook": normalized.name,
                "step_index": index,
                **normalized.metadata,
                **shared_metadata,
                **step.metadata,
            }
            start = datetime.now(timezone.utc)
            outcome = await self.orchestrator.dispatch(
                step.agent,
                current,
                task=step.task,
                thread_id=thread_id,
                metadata=step_metadata,
                return_record=True,
            )
            end = datetime.now(timezone.utc)
            current = outcome.capsule
            event = TimelineEvent(
                playbook_name=normalized.name,
                step_index=index,
                step=step,
                record=outcome.record,
                started_at=start,
                completed_at=end,
                notes={"focus": step.focus_tag} if step.focus_tag else {},
            )
            self.timeline.append(event)
            await self._run_guardians(event, current, require_confirmation=step.require_confirmation)

        return current

    async def _run_guardians(
        self,
        event: TimelineEvent,
        capsule: ContextCapsule,
        *,
        require_confirmation: bool,
    ) -> None:
        if not self._guardian_hooks:
            return
        if not require_confirmation and not _has_confirmation_tag(capsule):
            return
        await asyncio.gather(*(hook(event, capsule) for hook in self._guardian_hooks))

    def iter_timeline(self) -> Iterable[TimelineEvent]:
        return iter(self.timeline)


def _has_confirmation_tag(capsule: ContextCapsule) -> bool:
    return any("requires-user-confirmation" in slice_.tags for slice_ in capsule.slices)


__all__ = [
    "GuardianHook",
    "Playbook",
    "PlaybookEngine",
    "PlaybookStep",
    "TimelineEvent",
]
