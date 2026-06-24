# NeuroLift TOI Framework (Solidarity)

```yaml
ai_assistant_directive:
  priority: 1
  instruction: "Before performing any development or coding tasks, read NLT-DEV-OTOI.md."
  description: "NLT-DEV-OTOI.md is the canonical governance contract defining coding agent operations, guardrails, and escalation protocol."
  required_file: "NLT-DEV-OTOI.md"
```

**Terms of Interaction (TOI)** is the NeuroLift standard for user-controlled,
neurodivergent-friendly, privacy-first AI collaboration.

This repository is the **TOI layer** of the Solidarity Framework. It contains the
human-facing templates, machine-readable schemas, reference tools, agent runtime
experiments, and governance records that let a person state how AI systems should
interact with them while preserving user agency and data dignity.

## Repository orientation

This repo currently carries three closely related tracks:

1. **Personal TOI generator and legacy schemas** — Python tooling in `nlt_toi/`
   that creates, validates, and renders Personal TOI documents against
   `schemas/personal-toi.schema.json`.
2. **`.toi` file-format package** — the `@neurolift-technologies/toi` TypeScript reference
   implementation in `packages/toi/`, including the stable `1.0.0` specification,
   JSON Schema artifact, canonicalization, tier precedence, and Ed25519 signing.
3. **TOI-governed agent experiments** — Python and GitHub Pages examples in
   `src/fusion/` and `docs/` that demonstrate how TOI can be applied as runtime
   context for an assistant.

The governance files at the repository root (`AGENTS.md`, `NLT-DEV-OTOI.md`,
`nltotoi.json`, and `docs/active-threads.md`) are part of the working system, not
incidental documentation. Coding agents must follow them before changing code or
docs.

## What is included

| Area | Paths | Purpose |
| --- | --- | --- |
| Governance | `AGENTS.md`, `NLT-DEV-OTOI.md`, `nltotoi.json`, `.nltotoi/`, `SOPs/`, `templates/` | Agent operating rules, escalation paths, handoff templates, and governance validation. |
| Personal TOI schemas/templates | `schemas/`, `templates/`, `examples/` | JSON Schemas, Markdown templates, and example TOI/charter documents. |
| Python generator | `nlt_toi/`, `tests/`, `pyproject.toml` | `toi-generator` CLI and library for generating, rendering, and validating Personal TOI documents. |
| Fusion runtime examples | `src/fusion/`, `docs/` | TOI parser, privacy guardian, OTOI orchestrator, Agent Solidarity Kit prototype, and browser demo. |
| `.toi` TypeScript package | `packages/toi/` | Stable `.toi` specification, TypeScript parser/schema/types, canonicalization, signing, and conformance tests. |
| Contributor docs | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`, `docs/development-process.md` | Community expectations, security reporting, changelog, and CI runbooks. |
| Historical/nested materials | `nlt-otoi/` | Earlier OTOI project structure retained for templates, guides, validators, and reference context. |

## Quick start: Python Personal TOI generator

Install the development package from the repository root:

```bash
pip install -e ".[dev]"
```

Generate a TOI with defaults and print Markdown to stdout:

```bash
toi-generator --author "alice" --description "My daily coding TOI"
```

Answer accessible prompts and write Markdown to a file:

```bash
toi-generator --interactive --output my-toi.md
```

Load preferences from JSON or YAML and render another format:

```bash
toi-generator --input preferences.json --format json --output my-toi.json
toi-generator --input preferences.yaml --output my-toi.md
```

Validate an existing Personal TOI document against the bundled schema:

```bash
toi-generator --input my-toi.json --validate
```

### Python library usage

```python
from nlt_toi import TOIDocumentGenerator

# Generate from privacy-first defaults.
gen = TOIDocumentGenerator.from_defaults(author="alice")
print(gen.to_markdown())

# Generate from a dict. Required fields can be provided while defaults fill the rest.
gen = TOIDocumentGenerator.from_dict({
    "version": "1.0.0",
    "metadata": {"created": "...", "updated": "...", "author": "bob"},
    "communication": {"style": "friendly", "directness": "direct"},
    "cognitive": {"processing_time": "flexible", "information_structure": "bullet-points"},
    "privacy": {"data_retention": "session-only", "sharing_consent": "never"},
})
gen.validate()  # raises jsonschema.ValidationError if invalid
print(gen.to_json())

# Load from a file and save as Markdown.
gen = TOIDocumentGenerator.from_file("preferences.json")
gen.save("my-toi.md", fmt="markdown")
```

## Quick start: `.toi` TypeScript reference package

The `packages/toi/` workspace is the normative reference implementation for the
stable `.toi` file format.

```bash
cd packages/toi
npm install
npm test
npm run build
```

Use it to parse and validate `.toi` files, preserve forward-compatible unknown
keys, apply tier precedence (`personal`, `community`, `project`), canonicalize
JSON with RFC 8785 semantics, and sign/verify documents with detached Ed25519
signatures.

Primary references:

- Specification: `packages/toi/SPEC.md`
- Generated JSON Schema: `packages/toi/schema/toi-1.0.0.schema.json`
- Source exports: `packages/toi/src/index.ts`
- Conformance fixtures: `packages/toi/test/fixtures/`

### npm distribution

- `@neurolift-technologies/toi` is published on npm at version `1.0.0` under `Apache-2.0`.
- `@neurolift-technologies/asfdk` is not yet published to npm.

## TOI-governed agent demo

The GitHub Pages demo in `docs/` shows one possible TOI-governed assistant UI:

1. Provide a TOI JSON document.
2. Provide a model access token for the demo provider.
3. Send a prompt.
4. The page injects the TOI as system context and displays the response.

The current demo code is intentionally small and provider-specific so it is easy
to inspect. It is **not** a production deployment pattern and should not be read
as a provider commitment. External service choices, production deployment, and
architecture decisions require explicit approval under `NLT-DEV-OTOI.md`.

Privacy expectations for the demo:

- Personal tokens and TOI data should never be committed to this repository.
- Browser sessions should be treated as sensitive when testing personal TOI data.
- Production use needs a human-reviewed privacy, security, and provider plan.

## Documentation map

- Framework definition: `docs/framework-overview.md`
- Developer implementation guide: `docs/implementation-guide.md`
- Best practices: `docs/best-practices.md`
- NeuroLift multi-agent integration playbook: `docs/neurolift-integration.md`
- Development process and CI runbooks: `docs/development-process.md`
- Accessibility context: `nlt-otoi/docs/accessibility/neurodivergent-support.md`
- Platform integration examples: `nlt-otoi/docs/guides/platform-integration.md`

## Development and validation

Run the checks relevant to the area you changed:

```bash
# Python generator tests
pytest tests/test_generator.py -v

# TypeScript package tests
cd packages/toi && npm test && npm run build

# Governance file validation
bash .nltotoi/scripts/validate-governance.sh
```

Notes:

- The governance validation script reports missing or stale required governance
  files; resolve failures before merging governance-related changes.
- The Python generator depends on `jsonschema`; YAML input support requires the
  optional `PyYAML` dependency, which can be installed via the `yaml` extra (e.g., `pip install ".[yaml]"`).
- The TypeScript package requires Node.js 18 or newer.

## Contributing

Start with `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `SECURITY.md`.

Coding agents must additionally read, in order:

1. `NLT-DEV-OTOI.md`
2. `CLAUDE.md`
3. `docs/active-threads.md`

Then self-register, avoid overwriting active peer work, and leave a handoff
record for significant sessions.

## License

Apache-2.0 (see [LICENSE](LICENSE)). The `@neurolift-technologies/toi` package also ships its
own Apache-2.0 license copy at `packages/toi/LICENSE`.
