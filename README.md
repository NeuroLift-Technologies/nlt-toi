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

This repository is the **TOI layer** of the Solidarity Framework. It ships **two
reference implementations** of the `.toi` v1.0.0 standard:

1. **TypeScript** — `packages/toi/` → npm `@neurolift-technologies/toi@1.0.1`
2. **Python** — `src/nlt_toi/` → PyPI `nlt-toi@1.0.0`

plus governance records, templates, and runtime experiments.

## Repository orientation

1. **`.toi` TypeScript reference library** — `packages/toi/`: the normative
   reference, the `1.0.0` specification (`SPEC.md`), the JSON Schema artifact,
   and the conformance fixtures. Published to npm as
   `@neurolift-technologies/toi@1.0.1`.
2. **`.toi` Python reference library** — `src/nlt_toi/`: feature-parity Python
   implementation with identical on-disk format, RFC 8785 canonicalization, and
   Ed25519 signature envelope. Published to PyPI as `nlt-toi@1.0.0`.
3. **TOI-governed agent experiments** — browser demo and integration examples
   in `docs/` demonstrating TOI as runtime context for an assistant.
4. **Governance & tooling** — `AGENTS.md`, `NLT-DEV-OTOI.md`, `nltotoi.json`,
   `.nltotoi/`, `SOPs/`, `templates/`, and `docs/active-threads.md`.

The governance files at the repository root (`AGENTS.md`, `NLT-DEV-OTOI.md`,
`nltotoi.json`, and `docs/active-threads.md`) are part of the working system, not
incidental documentation. Coding agents must follow them before changing code or docs.

## What is included

| Area | Paths | Purpose |
| --- | --- | --- |
| Governance | `AGENTS.md`, `NLT-DEV-OTOI.md`, `nltotoi.json`, `.nltotoi/`, `SOPs/` | Agent operating rules, escalation paths, handoff templates, and governance validation. |
| `.toi` TypeScript library | `packages/toi/` | Normative reference: `.toi` specification, parser/schema/types, canonicalization, signing, and conformance tests. |
| `.toi` Python library | `src/nlt_toi/` | Feature-parity Python reference: parse/validate/serialize, canonicalization, Ed25519 sign/verify, tier resolution. |
| Schemas / templates | `legacy/schemas/`, `legacy/templates/` | Archived JSON Schemas and Markdown templates (superseded by published packages). |
| Contributor docs | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md` | Community expectations, security reporting, changelog, and CI runbooks. |

## Quick start: `@neurolift-technologies/toi` (TypeScript)

```bash
cd packages/toi
npm install && npm test && npm run build
```

```ts
import {
  parseToi,
  serializeToi,
  generateKeyPair,
  signToi,
  verifyToi,
} from "@neurolift-technologies/toi";

const doc = parseToi(await readFile("me.toi", "utf8"));
const { privateKey } = generateKeyPair();
const signed = signToi(doc, privateKey);
verifyToi(signed); // => true
```

Primary references for the TypeScript standard:

- Specification: `packages/toi/SPEC.md`
- Generated JSON Schema: `packages/toi/schema/toi-1.0.0.schema.json`
- Source exports: `packages/toi/src/index.ts`
- Conformance fixtures: `packages/toi/test/fixtures/`

## Quick start: `nlt-toi` (Python)

```bash
pip install nlt-toi
# or from source:
cd src/nlt_toi && pip install -e .
```

```python
from nlt_toi import parse_toi, sign_toi, verify_toi, generate_key_pair

doc = parse_toi(open("me.toi", encoding="utf-8").read())
keys = generate_key_pair()
signed = sign_toi(doc, keys.private_key)
verify_toi(signed)  # -> True
```

Primary references for the Python standard:

- Package entry: `src/nlt_toi/__init__.py` (see module docstring for full API)
- Specification: `packages/toi/SPEC.md` (shared normative spec)
- JSON Schema: `packages/toi/schema/toi-1.0.0.schema.json` (shared artifact)

Both implementations share:
- The exact same `.toi` v1.0.0 on-disk format
- RFC 8785 (JCS) canonicalization
- Ed25519 signature envelope
- Tier resolution logic (`personal` > `community` > `project`)
- Zod-derived JSON Schema as cross-language validation artifact

A document signed by one implementation verifies in the other.

## TOI-governed agent demo

The GitHub Pages demo in `docs/` shows one possible TOI-governed assistant UI: it
injects a TOI JSON document as system context for a prompt. The demo code is
intentionally small and provider-specific so it is easy to inspect. It is **not** a
production deployment pattern. External service choices, production deployment, and
architecture decisions require explicit approval under `NLT-DEV-OTOI.md`. Personal
tokens and TOI data must never be committed to this repository.

## Documentation map

- Framework definition: `legacy/docs/framework-overview.md` (archived)
- Developer implementation guide: `legacy/docs/implementation-guide.md` (archived)
- Best practices: `legacy/docs/best-practices.md` (archived)
- NeuroLift multi-agent integration playbook: `legacy/docs/neurolift-integration.md` (archived)
- Development process and CI runbooks: `legacy/docs/development-process.md` (archived)
- Active work threads: `docs/active-threads.md`

## Development and validation

```bash
# TypeScript reference tests
cd packages/toi && npm test && npm run build

# Python reference tests (from source)
cd src/nlt_toi && python -m pytest

# Governance file validation
bash .nltotoi/scripts/validate-governance.sh
```

Notes:

- The TypeScript package requires Node.js 18 or newer.
- The Python package requires Python 3.11+.
- The governance validation script reports missing or stale required governance
  files; resolve failures before merging governance-related changes.

## Contributing

Start with `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `SECURITY.md`. Coding agents
must additionally read, in order: `NLT-DEV-OTOI.md`, `CLAUDE.md`,
`docs/active-threads.md`, then self-register and leave a handoff record for
significant sessions.

## License

Apache-2.0 (see [LICENSE](LICENSE)). The `@neurolift-technologies/toi` package also
ships its own Apache-2.0 license copy at `packages/toi/LICENSE`. The `nlt-toi`
PyPI package includes the same license.