# Active Threads

### Thread: TOI-NPM-DIST-FIX
**Status:** published — PR in review for merge
**Owner:** Claude (Claude Code)
**Started:** 2026-06-22
**Last updated:** 2026-06-22
**Summary:** The published `@neurolift-technologies/toi@1.0.0` tarball shipped without its compiled `dist/`, so its `main`/`types`/`exports` entry points did not resolve on install — the package was non-functional (and it blocked building/publishing `@neurolift-technologies/otoi`, which imports it at runtime). Bumped `packages/toi/package.json` to `1.0.1`; verified the build (tsc), tests (65 passing), and a publish dry-run confirming `dist/` ships via the `prepack` build. **`@neurolift-technologies/toi@1.0.1` is now published** (Apache-2.0, tarball includes `dist/`), which unblocked **`@neurolift-technologies/otoi@1.1.0`** — also built and published (Apache-2.0). A clean `npm install @neurolift-technologies/otoi@1.1.0` + ESM import was verified end-to-end. Delivered via PR off `origin/main`.
**Blockers:** None — both packages published (the maintainer supplied the 2FA OTPs).
**Review feedback applied:** synced `packages/toi/package-lock.json` root version to `1.0.1` (Codex) and added `publishConfig.access: "public"` (Gemini Code Assist + Codex). CodeRabbit was rate-limited (no review).
**Next action:** Merge this PR (#18) to land the `1.0.1` bump in `main`. Optional follow-up: `npm deprecate` the broken `toi@1.0.0` and `otoi@1.0.0` so they warn on install (needs an OTP).

### Thread: TOI-LICENSE-PKG
**Status:** resolved
**Owner:** GHCPT (GitHub Copilot agent)
**Started:** 2026-05-29
**Last updated:** 2026-05-29
**Summary:** The `@neurolift/toi` package now includes `packages/toi/LICENSE` with Apache-2.0 text and package metadata remains aligned with `"license": "Apache-2.0"`.
**Blockers:** None.
**Next action:** Keep package LICENSE and README/SPDX references aligned in future releases.

### Thread: TOI-LICENSE-ROOT
**Status:** resolved
**Owner:** GHCPT (GitHub Copilot agent)
**Started:** 2026-05-29
**Last updated:** 2026-05-29
**Summary:** Maintainer confirmed MIT→Apache-2.0. Root `LICENSE` now uses Apache-2.0 terms; root README license section was updated to Apache-2.0.
**Blockers:** None.
**Next action:** Verify downstream docs and release metadata remain consistent with Apache-2.0.

### Thread: README-REPO-ORIENTATION
**Status:** resolved
**Owner:** Codex (GPT-5.3-Codex)
**Started:** 2026-05-31
**Last updated:** 2026-05-31
**Summary:** Read repo governance/context first, surveyed repository documentation and implementation areas, then refreshed the root README to reflect the current Python generator, `.toi` TypeScript package, agent demo, documentation map, validation commands, and Apache-2.0 licensing. Also aligned Python package metadata license text with the repository Apache-2.0 license.
**Blockers:** None.
**Next action:** Keep README, package metadata, and active release/package docs aligned when the `.toi` package or TOI agent demo changes.

### Thread: TOI-NPM-SCOPE-RENAME
**Status:** resolved
**Owner:** Claude (Claude Code)
**Started:** 2026-06-16
**Last updated:** 2026-06-16
**Summary:** Renamed the npm package scope `@neurolift` → `@neurolift-technologies` (to match the GitHub org) across current/canonical references: `packages/toi` `package.json` + lockfile name, `src/index.ts` header/example import, `scripts/build-schema.ts` description, `schema/toi-1.0.0.schema.json` description, package README/SPEC, and the root README. Historical records (the resolved threads above and the dated agent-log handoffs) were intentionally left referencing `@neurolift/toi`. Coordinated with sibling renames in nlt-otoi (`@neurolift-technologies/otoi`) and nlt-redteam (connector deps + OTOI contracts).
**Blockers:** None in-repo. Publishing `@neurolift-technologies/{toi,otoi}` to npm/GitHub Packages remains a maintainer-owned prerequisite before downstream `npm install`/CI can resolve them.
**Next action:** Publish the renamed packages under the new scope, then keep package metadata, imports, and docs aligned on future releases.

### Thread: TOI-NPM-RECEIPTS-DOC
**Status:** resolved
**Owner:** Claude (Claude Code)
**Started:** 2026-06-22
**Last updated:** 2026-06-22
**Summary:** Documented npm publication status in the READMEs — root README gained an "npm distribution" subsection and `packages/toi/README.md` a one-line note stating `@neurolift-technologies/toi` is published on npm at `1.0.0` (Apache-2.0) and `@neurolift-technologies/asfdk` is not yet published. Recovered from orphaned local edits left over from a 2026-06-19 verification pass; sanitized of internal evidence references since this repo is public. Delivered via PR #17 (branch `docs/toi-npm-receipts`) after fast-forwarding the local clone to current `main` (OTOI 1.0.2).
**Blockers:** None.
**Next action:** Keep the npm publication notes accurate as packages are (re)published; update the ASFDK note once it is on npm.
