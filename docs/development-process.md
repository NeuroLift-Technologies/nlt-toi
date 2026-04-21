# Development Process and CI Runbooks

This guide explains how contribution workflows are validated in this repository,
which checks run automatically, and how to troubleshoot common failures.

It is intentionally focused on repository automation and quality gates. For
general contribution rules, see [CONTRIBUTING.md](../CONTRIBUTING.md).

## Local Prerequisites for CI Reproduction

GitHub Actions runners provide `python` (3.11) and tool binaries on `PATH`.
Local machines often differ, so use equivalent commands where needed:

- If `python` is unavailable, use `python3`.
- If `pip` is unavailable, use `python3 -m pip`.
- If `bandit` is not on `PATH`, run it as `python3 -m bandit`.

Minimum local tools for CI parity:
- Python 3.11
- `jsonschema` (schema validation workflow dependency)
- `bandit` (security scan workflow dependency)

## Workflow Architecture

The repository uses four GitHub Actions workflows:

| Workflow | File | Purpose |
| --- | --- | --- |
| Accessibility Check | `.github/workflows/accessibility-check.yml` | Enforces accessibility-focused docs and template checks |
| Schema Validation | `.github/workflows/schema-validation.yml` | Validates schema and template JSON structure |
| Security Scan | `.github/workflows/security-scan.yml` | Runs Bandit and lightweight security heuristics |
| Create Branch Cleanup Issues | `.github/workflows/create-branch-cleanup-issues.yml` | Creates maintenance issues for stale merged branches |

### Source of Truth for CI Definitions

GitHub Actions only executes workflow files from the repository root
`.github/workflows/` directory.

This repository also contains older workflow copies under
`nlt-otoi/.github/workflows/` for historical context. Those nested copies are
not loaded by GitHub Actions and should not be used for CI troubleshooting.

When changing automation behavior, always edit the root workflow files first.
Treat nested workflow copies as archival references, not active automation.

## Trigger Matrix

### Accessibility Check
- Triggers on `push` and `pull_request` to `main` or `develop`
- Pull requests targeting any other base branch do not run this workflow
- Runs only when changes touch:
  - `docs/**`, `templates/**`, `schemas/**`
  - `nlt-otoi/docs/**`, `nlt-otoi/templates/**`, `nlt-otoi/schemas/**`

### Schema Validation
- Triggers on `push` and `pull_request` to `main` or `develop`
- Pull requests targeting any other base branch do not run this workflow
- Runs only when changes touch:
  - `schemas/**`
  - `nlt-otoi/schemas/**`
  - `nlt-otoi/tools/validators/**`
  - `nlt-otoi/templates/**`

### Security Scan
- Triggers on `push` and `pull_request` to `main` or `develop`
- Pull requests targeting any other base branch do not run this workflow
- Also runs on a weekly schedule: Monday at 02:00 UTC
- Has no `paths` filter, so all file changes on supported branches trigger it

### Create Branch Cleanup Issues
- Manual trigger only (`workflow_dispatch`)
- Input:
  - `dry_run` (boolean, default `false`)

## First Triage When a Workflow Did Not Run

Before deep debugging, verify the run should have triggered at all:

1. Confirm the event type is supported (`push`, `pull_request`, `schedule`, or
   `workflow_dispatch` as defined per workflow).
2. For PR-triggered runs, confirm the PR base branch is `main` or `develop`.
3. Confirm at least one changed file matches that workflow's `paths` filters.

Useful local command for path filter checks:

```bash
git diff --name-only <base_sha>...<head_sha>
```

## Common Failure Signatures and Fast Fixes

Use this table to quickly map common CI outcomes to likely causes:

| Symptom (Actions log/UI) | Likely cause | First action |
| --- | --- | --- |
| Workflow did not appear for a PR | PR base branch is not `main`/`develop`, or changed files did not match `paths` filters | Confirm PR base branch, then run `git diff --name-only <base_sha>...<head_sha>` |
| `❌ Missing accessibility content in documentation` | Accessibility keywords are absent from scanned docs directories | Add explicit accessibility terms in `docs/` or `nlt-otoi/docs/` |
| `❌ Documentation may not use clear language` | Clear-language keywords are missing from scanned docs | Add wording that includes `clear`, `simple`, `easy`, or `understand` |
| `❌ Invalid JSON in ...` (schema workflow) | A schema/template file failed JSON parsing | Run `python -m json.tool <file>` and fix syntax |
| `❌ N high-severity security issues found` | Bandit reported one or more HIGH findings | Re-run Bandit locally and remediate flagged code paths |
| `⚠️  Potential hardcoded passwords found — please review` | Grep-based secret heuristic matched literal password assignment pattern | Remove hardcoded credentials or migrate them to environment/secret stores |

Note: warning-level findings do not always fail a workflow. Check each workflow's
explicit `exit` behavior in the root `.github/workflows/` definitions.

## Operational Runbooks

### Accessibility Check Runbook

What it does:
1. Checks out the repository and sets up Python 3.11
2. Greps docs for accessibility-related language
3. Validates `nlt-otoi/templates/personal-toi/*.json` with
   `nlt-otoi/tools/validators/toi-validator.py`
4. Greps `nlt-otoi/tools/` for accessibility terms (warning signal)

Behavioral constraints from source:
- The docs grep check is keyword-based, not semantic analysis.
- The grep checks are case-sensitive (`grep -r` without `-i`).
- The workflow expects terms matching:
  - `neurodivergent|ADHD|autism|accessibility`
  - `clear|simple|easy|understand`

Troubleshooting:
- If the check fails after docs edits, confirm the expected terms still appear in
  `docs/` or `nlt-otoi/docs/`.
- Reproduce the keyword checks locally:
  ```bash
  grep -r "neurodivergent\|ADHD\|autism\|accessibility" docs/ nlt-otoi/docs/
  grep -r "clear\|simple\|easy\|understand" docs/ nlt-otoi/docs/
  ```
- If template validation fails, run:
  ```bash
  python3 nlt-otoi/tools/validators/toi-validator.py <template.json>
  ```

### Schema Validation Runbook

What it does:
1. Installs `jsonschema`
2. Parses all root schema JSON files in `schemas/**`
3. Parses all JSON files in `nlt-otoi/schemas/**`
4. Parses all JSON templates in `nlt-otoi/templates/**`

Behavioral constraints from source:
- This workflow checks JSON parse validity (not full semantic schema conformance
  across every document in the repo).
- Although it installs `jsonschema`, the current steps only parse JSON files.
- Any invalid JSON causes a hard failure.

Troubleshooting:
- Validate a single file:
  ```bash
  python -m json.tool schemas/personal-toi.schema.json > /dev/null
  ```
- Validate all touched schema/template files before pushing:
  ```bash
  python - <<'PY'
  import glob, json, sys
  paths = glob.glob('schemas/**/*.json', recursive=True)
  paths += glob.glob('nlt-otoi/schemas/**/*.json', recursive=True)
  paths += glob.glob('nlt-otoi/templates/**/*.json', recursive=True)
  bad = []
  for p in paths:
      try:
          with open(p) as f:
              json.load(f)
      except Exception as exc:
          bad.append((p, exc))
  if bad:
      for p, exc in bad:
          print(f'Invalid JSON: {p}: {exc}')
      sys.exit(1)
  print('All schema/template JSON files parse successfully.')
  PY
  ```

### Security Scan Runbook

What it does:
1. Runs Bandit against `src/` and `nlt-otoi/tools/`
2. Fails the workflow only when HIGH-severity Bandit issues exist
3. Runs a simple grep-based secret detection check for hardcoded passwords
4. Scans schemas for `additionalProperties: true` and reports warnings

Behavioral constraints from source:
- Bandit runs with `--exit-zero`, then a Python gate enforces failure only on
  HIGH-severity findings.
- The Bandit JSON report can contain path errors (for example, missing `src/`);
  the current gate does not fail on report `errors` entries.
- The secret check currently warns but does not fail the job.
- Schema permissiveness findings are informational warnings.

Troubleshooting:
- Reproduce Bandit locally:
  ```bash
  python3 -m pip install bandit
  python3 -m bandit -r src/ nlt-otoi/tools/ -f json -o /tmp/bandit-report.json --exit-zero
  ```
- Inspect high-severity findings in `/tmp/bandit-report.json`.
- Also inspect `errors` in `/tmp/bandit-report.json` (missing scan paths show up
  there even when the workflow still passes).
- For hardcoded credential warnings, move secrets to environment variables or
  secret stores and avoid literal password assignments in committed files.

### Branch Cleanup Issue Automation Runbook

What it does:
- Creates GitHub issues (labelled `maintenance` and `branch-cleanup`) to prompt
  deletion of known stale merged branches.

Important constraints:
- This workflow is manual only and does nothing on push/PR events.
- `dry_run=true` prints a summary and does not create issues.
- The workflow currently checks string values (`'true'` / `'false'`) for
  `inputs.dry_run`.
- The stale branch list is hardcoded in
  `.github/workflows/create-branch-cleanup-issues.yml`.
- There is no de-duplication guard; rerunning with `dry_run=false` can create
  duplicate cleanup issues for the same branches.

How to execute:
1. Open **Actions** in GitHub.
2. Run **Create Branch Cleanup Issues**.
3. Set `dry_run=true` first to preview.
4. Re-run with `dry_run=false` to create issues.

## PR Interface and Contributor Workflow

- PR descriptions are standardized by `.github/PULL_REQUEST_TEMPLATE.md`.
- Contributors should include:
  - change type
  - accessibility impact
  - testing notes
  - documentation updates

Recommended pre-push checklist:
1. Ensure changed docs and templates stay accessible and clear.
2. Ensure changed JSON in schemas/templates parses correctly.
3. Review security impact for any tool or policy changes.
4. Confirm PR description follows the template sections.

