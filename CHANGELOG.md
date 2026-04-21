# Changelog

All notable changes to the OTOI Framework will be documented in this file.

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
- `docs/development-process.md` — CI architecture, workflow runbooks, and troubleshooting steps

### Changed
- `README.md` — repository structure now includes `docs/development-process.md`
- `CONTRIBUTING.md` — added CI and automation expectations for pull requests

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

---

## [0.8.0] — 2026-03-XX

### Added
- `CLAUDE.md` — comprehensive guide for AI assistants working with the OTOI Framework
- `src/fusion/toi_parser.py` — parses and validates user TOI documents
- `src/fusion/otoi_orchestrator.py` — multi-agent coordination with TOI policy enforcement
- `src/fusion/privacy_guardian.py` — enforces privacy settings from TOI documents
- `examples/neuroLift/` — NeuroLift-specific integration examples and patterns
- `docs/framework-overview.md` — extracted TOI-OTOI Framework deep dive document

### Changed
- `README.md` — separated high-level introduction from technical framework definition

---

## [0.7.0] — 2026-02-XX

### Added
- `nlt-otoi/.github/workflows/accessibility-check.yml`
- `nlt-otoi/.github/workflows/schema-validation.yml`
- `nlt-otoi/.github/workflows/security-scan.yml`
- `nlt-otoi/.github/PULL_REQUEST_TEMPLATE.md`
- `nlt-otoi/.github/ISSUE_TEMPLATE/` — bug, feature, and accessibility issue templates
- `nlt-otoi/CODE_OF_CONDUCT.md`
- `nlt-otoi/CHANGELOG.md`
- `nlt-otoi/CONTRIBUTING.md`
- `nlt-otoi/PROJECT_OVERVIEW.md`
- `nlt-otoi/schemas/v1.0/collaborative-charter-v1.json`
- `nlt-otoi/templates/personal-toi/adhd-optimized-toi.json`
- `nlt-otoi/tools/validators/toi-validator.py`
- `nlt-otoi/tools/generators/toi-generator.py`

---

## [0.6.0] — 2026-01-XX

### Added
- `codex/design-multi-agent-ai-integration-architecture` — enhanced NeuroLift agent architecture
  - `examples/neuroLift/context_capsule.py`
  - `examples/neuroLift/intent_ledger.py`
  - `examples/neuroLift/orchestrator_patterns.py`
  - `examples/neuroLift/playbook_engine.py`

---

## [0.5.0] — 2025-12-XX

### Added
- Initial GitHub issue templates (`.github/ISSUE_TEMPLATE/`)
  - `bug_report.yml`
  - `feature_request.yml`
  - `accessibility.yml`
  - `documentation.yml`
  - `question.yml`
- `README.md` — detailed TOI-OTOI framework description
- `GEMINI_TOPOGRAPHY.py` — comprehensive Gemini AI analysis guide

---

## [0.1.0] — 2025-09-XX

### Added
- Initial repository structure
- `schemas/personal-toi.schema.json` — JSON Schema for personal TOI documents
- `schemas/collaborative-charter.schema.json` — JSON Schema for team charters
- `templates/personal-toi-template.md` — personal TOI template
- `templates/collaborative-charter-template.md` — team charter template
- `templates/quick-start-template.md` — simplified quick-start template
- `docs/best-practices.md`
- `docs/implementation-guide.md`
- `docs/neurolift-integration.md`
- `examples/neurodivergent-examples/adhd-student-example.json`
- `examples/team-collaboration/remote-dev-team-charter.json`
- `CONTRIBUTING.md`
- `LICENSE` (MIT)

[Unreleased]: https://github.com/NeuroLift-Technologies/nlt-otoi/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/NeuroLift-Technologies/nlt-otoi/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/NeuroLift-Technologies/nlt-otoi/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/NeuroLift-Technologies/nlt-otoi/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/NeuroLift-Technologies/nlt-otoi/compare/v0.1.0...v0.5.0
[0.1.0]: https://github.com/NeuroLift-Technologies/nlt-otoi/releases/tag/v0.1.0
