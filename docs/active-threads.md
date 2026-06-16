# Active Threads

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
