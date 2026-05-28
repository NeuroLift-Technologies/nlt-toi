# NeuroLift TOI Framework (Solidarity)

```yaml
ai_assistant_directive:
  priority: 1
  instruction: "Before performing any development or coding tasks, read NLT-DEV-OTOI.md."
  description: "NLT-DEV-OTOI.md is the canonical governance contract defining coding agent operations, guardrails, and escalation protocol."
  required_file: "NLT-DEV-OTOI.md"
```

**Terms of Interaction (TOI)** for user-controlled, neurodivergent-friendly, privacy-first AI collaboration.

This repository is the **TOI layer** of the Solidarity Framework. It focuses on defining and enforcing personal interaction terms, with a single TOI Agent runtime built on the Agent Solidarity Kit.

## What is included

- TOI schema and templates (`/schemas`, `/templates`)
- **TOI generator CLI + library** (`/nlt_toi`) — create, validate, and render TOI documents
- TOI parser and privacy guardian (`/src/fusion`)
- TOI Agent Solidarity Kit runtime (`/src/fusion/agent_solidarity_kit.py`)
- GitHub Pages web interface for TOI agent interaction (`/docs/index.html`)

## TOI Generator

The `toi-generator` CLI lets you create a Personal TOI document from interactive
prompts or a JSON/YAML input file, and render it as Markdown or JSON.

### Installation

```bash
pip install -e ".[dev]"   # development
# or
pip install .             # production
```

### Usage examples

**Generate a TOI with defaults and print Markdown to stdout:**

```bash
toi-generator --author "alice" --description "My daily coding TOI"
```

**Interactive mode — answer prompts, then write Markdown to a file:**

```bash
toi-generator --interactive --output my-toi.md
```

**Load preferences from a JSON file and output JSON:**

```bash
toi-generator --input preferences.json --format json --output my-toi.json
```

**Load preferences from a YAML file:**

```bash
toi-generator --input preferences.yaml --output my-toi.md
```

**Validate an existing TOI document against the schema:**

```bash
toi-generator --input my-toi.json --validate
```

### Library usage

```python
from nlt_toi import TOIDocumentGenerator

# Generate from defaults
gen = TOIDocumentGenerator.from_defaults(author="alice")
print(gen.to_markdown())

# Generate from a dict (only required fields needed — defaults fill the rest)
gen = TOIDocumentGenerator.from_dict({
    "version": "1.0.0",
    "metadata": {"created": "...", "updated": "...", "author": "bob"},
    "communication": {"style": "friendly", "directness": "direct"},
    "cognitive": {"processing_time": "flexible", "information_structure": "bullet-points"},
    "privacy": {"data_retention": "session-only", "sharing_consent": "never"},
})
gen.validate()          # raises jsonschema.ValidationError if invalid
print(gen.to_json())

# Load from a file
gen = TOIDocumentGenerator.from_file("preferences.json")
gen.save("my-toi.md", fmt="markdown")
```

### Running tests

```bash
pytest tests/test_generator.py -v
```

## Default model

The TOI Agent uses a free open-source model on GitHub Models:

- `azureml/Phi-4-mini-instruct`

## Quick start

1. Create or copy a TOI JSON document from `/templates`.
2. Validate it against `/schemas/personal-toi.schema.json`.
3. Open the GitHub Pages UI (`docs/index.html` when published) and provide:
   - your TOI JSON
   - your GitHub token with Models access
   - your prompt

## GitHub Pages interface

The Pages interface is deployed by `.github/workflows/deploy-toi-agent-pages.yml`.

It sends browser requests directly to GitHub Models and applies TOI as system context for each message.

## Privacy note

- TOI preferences are kept in-browser for the current session unless you choose to persist them.
- Do not commit personal tokens or personal TOI data to this repository.

## License

MIT
