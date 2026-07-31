# Changelog

All notable changes to the `@neurolift-technologies/toi` package will be
documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `.github/PULL_REQUEST_TEMPLATE.md` — standard PR template for all contributors
- `.github/workflows/accessibility-check.yml` — automated accessibility compliance checks
- `.github/workflows/schema-validation.yml` — automated JSON schema validation
- `.github/workflows/security-scan.yml` — automated security scanning workflow
- `.github/workflows/create-branch-cleanup-issues.yml` — workflow to create stale branch cleanup issues
- `CODE_OF_CONDUCT.md` — community code of conduct with neurodivergent-inclusive practices
- `SECURITY.md` — security policy and vulnerability reporting process
- `CHANGELOG.md` — this changelog
- `docs/active-threads.md` — current work state and thread tracking

### Changed
- `README.md` — repository structure updated to reflect current published packages
- `CONTRIBUTING.md` — added CI and automation expectations for pull requests

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- `@neurolift-technologies/toi` npm package republished as **1.0.1** to include the
  compiled `dist/` (JS + type declarations). The `1.0.0` tarball shipped without
  `dist/`, so its `main`/`types`/`exports` entry points did not resolve on install;
  `1.0.1` ships `dist/` via the `prepack` build. This also unblocked
  `@neurolift-technologies/otoi`, which imports this package at runtime.

---

## [1.0.0] — 2026-06-XX

### Added
- `packages/toi/` — TypeScript reference library for the `.toi` v1.0.0 standard
  - `SPEC.md` — normative specification
  - `src/index.ts` — full API: parse, serialize, canonicalize, sign, verify, resolve
  - `schema/toi-1.0.0.schema.json` — generated JSON Schema (draft 2020-12)
  - `test/fixtures/` — conformance fixtures (shared with Python library)
- `packages/toi/package.json` — npm package `@neurolift-technologies/toi`
- `README.md` — root README describing the `.toi` standard and both reference implementations
- `AGENTS.md` — repo-local governance gateway for coding agents
- `NLT-DEV-OTOI.md` — canonical governance contract for coding agents
- `nltotoi.json` — discovery manifest and governance file registry

---

## [0.8.0] — 2026-03-XX

### Added
- `CLAUDE.md` — comprehensive guide for AI assistants working with the TOI Framework
- `docs/framework-overview.md` — extracted TOI-OTOI Framework deep dive document

---

## [0.1.0] — 2025-09-XX

### Added
- Initial repository structure
- `schemas/personal-toi.schema.json` — JSON Schema for personal TOI documents (now archived in `legacy/schemas/`)
- `schemas/collaborative-charter.schema.json` — JSON Schema for team charters (now archived in `legacy/schemas/`)
- `templates/personal-toi-template.md` — personal TOI template (now archived in `legacy/templates/`)
- `templates/collaborative-charter-template.md` — team charter template (now archived in `legacy/templates/`)
- `templates/quick-start-template.md` — simplified quick-start template (now archived in `legacy/templates/`)
- `docs/best-practices.md` (now archived in `legacy/docs/`)
- `docs/implementation-guide.md` (now archived in `legacy/docs/`)
- `docs/neurolift-integration.md` (now archived in `legacy/docs/`)
- `examples/neurodivergent-examples/adhd-student-example.json`
- `examples/team-collaboration/remote-dev-team-charter.json`
- `CONTRIBUTING.md`
- `LICENSE` (MIT)

[Unreleased]: https://github.com/NeuroLift-Technologies/nlt-toi/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/NeuroLift-Technologies/nlt-toi/releases/tag/v1.0.0
[0.8.0]: https://github.com/NeuroLift-Technologies/nlt-toi/releases/tag/v0.8.0
[0.1.0]: https://github.com/NeuroLift-Technologies/nlt-toi/releases/tag/v0.1.0
