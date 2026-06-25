# NeuroLift TOI Framework (Solidarity)

```yaml
ai_assistant_directive:
  priority: 1
  instruction: "Before performing any development or coding tasks, read NLT-DEV-OTOI.md."
  description: "NLT-DEV-OTOI.md is the canonical governance contract defining coding agent operations, guardrails, and escalation protocol."
  required_file: "NLT-DEV-OTOI.md"
```

**Terms of Interaction (`.toi`)** is the NeuroLift standard for user-controlled,
neurodivergent-friendly, privacy-first AI collaboration — a small, portable,
human-editable JSON file that states how AI systems should interact with a person.

This repository is the **TOI layer** of the Solidarity Framework. It ships two
**reference implementations of the same `.toi` v1.0.0 standard** — one in Python
(`nlt-toi`) and one in TypeScript (`@neurolift-technologies/toi`) — plus the
human-facing templates, governance records, and runtime experiments.

> The Python library is a faithful port of the TypeScript reference: the on-disk
> format, RFC 8785 canonicalization, and Ed25519 signature envelope are identical,
> so **a document signed by one implementation verifies in the other.**

## Repository orientation

1. **`.toi` Python reference library** — `nlt_toi/` (`src/nlt_toi/`): parse,
   validate, RFC 8785 canonicalize, tier-precedence resolve, and Ed25519
   sign/verify. Published to PyPI as `nlt-toi`.
2. **`.toi` TypeScript reference library** — `packages/toi/`: the normative
   reference, the `1.0.0` specification (`SPEC.md`), the JSON Schema artifact, and
   the conformance fixtures. Published to npm as `@neurolift-technologies/toi`.
3. **TOI-governed agent experiments** — Python and GitHub Pages examples in
   `src/fusion/` and `docs/` demonstrating TOI as runtime context for an assistant.

The governance files at the repository root (`AGENTS.md`, `NLT-DEV-OTOI.md`,
`nltotoi.json`, and `docs/active-threads.md`) are part of the working system, not
incidental documentation. Coding agents must follow them before changing code or docs.

## What is included

| Area | Paths | Purpose |
| --- | --- | --- |
| Governance | `AGENTS.md`, `NLT-DEV-OTOI.md`, `nltotoi.json`, `.nltotoi/`, `SOPs/`, `templates/` | Agent operating rules, escalation paths, handoff templates, and governance validation. |
| `.toi` Python library | `src/nlt_toi/`, `tests/`, `pyproject.toml` | Python reference implementation: parse/validate/canonicalize/sign/verify/resolve, with the npm conformance fixtures. |
| `.toi` TypeScript library | `packages/toi/` | Normative reference: `.toi` specification, parser/schema/types, canonicalization, signing, and conformance tests. |
| Schemas / templates | `schemas/`, `templates/`, `examples/` | JSON Schemas, Markdown templates, and example documents. |
| Fusion runtime examples | `src/fusion/`, `docs/` | TOI parser, privacy guardian, OTOI orchestrator prototype, and browser demo. |
| Contributor docs | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md` | Community expectations, security reporting, changelog, and CI runbooks. |

## Quick start: `nlt-toi` (Python)

```bash
pip install nlt-toi
```

```python
from nlt_toi import (
    parse_toi, safe_parse_toi, serialize_toi,
    canonicalize, generate_key_pair, sign_toi, verify_toi,
    resolve_toi,
)

# Parse + validate (accepts a JSON string or an already-parsed dict).
doc = parse_toi('''
{
  "$toi": "1.0.0",
  "$tier": "personal",
  "identity": { "author": "alice" },
  "communication": { "tone": "direct", "verbosity": "concise" }
}
''')

# Sign and verify. The Ed25519 signature is detached over the canonical payload
# (the document with $signature removed) and carried back in the $signature key.
keys = generate_key_pair()
signed = sign_toi(doc, keys.private_key)
assert verify_toi(signed) is True

# RFC 8785 canonical form — the exact bytes that get signed.
print(canonicalize(doc))

# Resolve precedence: personal > community > project > platform defaults.
project_doc = parse_toi('{"$toi":"1.0.0","$tier":"project","identity":{"author":"acme"}}')
community_doc = parse_toi('{"$toi":"1.0.0","$tier":"community","identity":{"author":"team"}}')
personal_doc = doc  # the personal-tier document above
effective = resolve_toi([project_doc, community_doc, personal_doc])
```

Non-throwing parsing is available via `safe_parse_toi`, which returns a
`SafeParseResult` (`.success`, `.data`, `.error`) instead of raising.

The public API mirrors `@neurolift-technologies/toi` (in `snake_case`):
`parse_toi`/`safe_parse_toi`/`is_toi`/`serialize_toi`, `canonicalize`/
`canonicalize_to_bytes`, `generate_key_pair`/`sign_toi`/`verify_toi`/`is_signed`/
`signing_payload`, and `resolve_toi`/`sort_by_precedence`/`compare_tier`.

## Quick start: `@neurolift-technologies/toi` (TypeScript)

```bash
cd packages/toi
npm install && npm test && npm run build
```

Primary references for the standard:

- Specification: `packages/toi/SPEC.md`
- Generated JSON Schema: `packages/toi/schema/toi-1.0.0.schema.json`
- Source exports: `packages/toi/src/index.ts`
- Conformance fixtures: `packages/toi/test/fixtures/` (the Python library is tested
  against this same fixture set)

## TOI-governed agent demo

The GitHub Pages demo in `docs/` shows one possible TOI-governed assistant UI: it
injects a TOI JSON document as system context for a prompt. The demo code is
intentionally small and provider-specific so it is easy to inspect. It is **not** a
production deployment pattern. External service choices, production deployment, and
architecture decisions require explicit approval under `NLT-DEV-OTOI.md`. Personal
tokens and TOI data must never be committed to this repository.

## Documentation map

- Framework definition: `docs/framework-overview.md`
- Developer implementation guide: `docs/implementation-guide.md`
- Best practices: `docs/best-practices.md`
- NeuroLift multi-agent integration playbook: `docs/neurolift-integration.md`
- Development process and CI runbooks: `docs/development-process.md`

## Development and validation

```bash
# Python .toi library tests (uses the npm conformance fixtures)
pytest

# TypeScript reference tests
cd packages/toi && npm test && npm run build

# Governance file validation
bash .nltotoi/scripts/validate-governance.sh
```

Notes:

- The Python library depends on `jsonschema` (validation) and `cryptography`
  (Ed25519). It targets Python 3.9+.
- The governance validation script reports missing or stale required governance
  files; resolve failures before merging governance-related changes.
- The TypeScript package requires Node.js 18 or newer.

## Contributing

Start with `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `SECURITY.md`. Coding agents
must additionally read, in order: `NLT-DEV-OTOI.md`, `CLAUDE.md`,
`docs/active-threads.md`, then self-register and leave a handoff record for
significant sessions.

## License

Apache-2.0 (see [LICENSE](LICENSE)). The `@neurolift-technologies/toi` package also
ships its own Apache-2.0 license copy at `packages/toi/LICENSE`.
