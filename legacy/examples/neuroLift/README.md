# NeuroLift Agent Integration Examples

This folder contains modular code sketches that align with the architectural threads
outlined in `docs/neurolift-integration.md`.

## Modules
- `context_capsule.py` – immutable data structures for context preservation, diffing, and cursoring.
- `intent_ledger.py` – append-only ledger for intent/interpretation tracking with scoring helpers.
- `orchestrator_patterns.py` – registry, orchestrator, event relay, and handoff records.
- `playbook_engine.py` – composable playbook runner that coordinates orchestrator, ledger, and guardian agents.

## Quickstart Snippet
```python
import asyncio
from examples.neuroLift import (
    ContextCapsule,
    ContextSlice,
    IntentLedger,
    Playbook,
    PlaybookEngine,
    build_default_registry,
)

async def main() -> None:
    registry = build_default_registry()
    ledger = IntentLedger()
    engine = PlaybookEngine(registry=registry, ledger=ledger)
    capsule = ContextCapsule([
        ContextSlice(topic="neuro-session", payload={"phase": "warmup"}),
    ])
    capsule = capsule.with_cursor("session-1:start")

    playbook = Playbook(
        name="focus-then-guard",
        steps=[
            {"agent": "focus-agent", "task": "summarize session"},
            {"agent": "guardian", "task": "check confirmations"},
        ],
    )

    capsule = await engine.run(playbook, capsule=capsule, thread_id="session-1")

    for slice_ in capsule.slices:
        print(slice_.topic, slice_.payload)

    for entry in ledger.to_list():
        print(entry.intent_id, entry.status, entry.score)

    for event in engine.iter_timeline():
        print(event.step.agent, event.record.added, event.record.metadata)

asyncio.run(main())
```

The snippet highlights how the orchestrator keeps the user in control: every
handoff is explicit, the capsule remains diffable, and the ledger records how
interpretations were acknowledged. The playbook engine stitches the flow so
Josh can pause, replay, or rescore any step without losing agency.
