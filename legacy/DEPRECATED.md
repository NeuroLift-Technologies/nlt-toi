# Deprecated & Archived Content

This directory contains legacy Python-era files and documents that have been
superseded by the current published packages. These files are preserved for
historical reference but are no longer active in the repository's primary
workflows.

## What is archived here

| Path | Reason |
|---|---|
| `nlt_toi/` | Root-level flat Python package (v0.2.0). Superseded by `src/nlt_toi/` (PyPI `nlt-toi` 1.0.0). |
| `src/fusion/` | Old OTOI orchestrator Python code. Superseded by the `nlt-otoi` PyPI package. |
| `examples/neuroLift/` | Old Python examples. Superseded by current published packages. |
| `schemas/personal-toi.schema.json` | Self-deprecated; replaced by `packages/toi/schema/toi-1.0.0.schema.json`. |
| `schemas/collaborative-charter.schema.json` | Superseded by the published TS package schema. |
| `toi-otoi-agents.md` | Old adoption agent specification. |
| `nlt-otoi/` | Vendored copy of the OTOI framework. Superseded by the published `nlt-otoi` PyPI package. |
| `tests/` | Python pytest suite. Superseded by `packages/toi/test/` (npm conformance fixtures). |
| `templates/` | Python-era OTOI templates. Superseded by current governance templates. |
| `GEMINI_TOPOGRAPHY.py` | Legacy topography documentation. |
| `mcp-config.yaml` | Deprecated tooling configuration. |
| `file-structure.md` | Stale file-structure document referencing `.github-private`. |
| `docs/development-process.md` | Python CI runbook. Superseded by current CI workflows. |
| `docs/framework-overview.md` | Contains outdated "Python Implementation" section. |
| `docs/implementation-guide.md` | References deprecated schemas and Python code. |
| `docs/neurolift-integration.md` | References old Python examples. |
| `docs/best-practices.md` | OTOI-era best practices document. |

## Current active packages

- **npm**: `@neurolift-technologies/toi@1.0.1` — `packages/toi/`
- **PyPI**: `nlt-toi@1.0.0` — `src/nlt_toi/`

## Notes

- No files in this directory have been deleted. They are archived for reference
  only.
- If you need a legacy file, it is still available here.
- For the current API, refer to the published packages and the root README.
