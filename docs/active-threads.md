# Active Threads

### Thread: TOI-LICENSE-PKG
**Status:** open
**Owner:** Joshua W. Dorsey, Sr.
**Started:** 2026-05-29
**Last updated:** 2026-05-29
**Summary:** The `@neurolift/toi` package declares `"license": "Apache-2.0"` in `packages/toi/package.json` but ships no `LICENSE` text file. Three independent PR reviewers (Gemini, Codex, Copilot) flagged the gap on PR #5; the README's license link was de-linked in the interim to avoid a dangling reference. Adding the bundled Apache-2.0 text was deliberately deferred per maintainer instruction during the foundation pour.
**Blockers:** Awaiting maintainer decision to add the bundled Apache-2.0 LICENSE text (or to change the declared license).
**Next action:** In the follow-up PR, add `packages/toi/LICENSE` (Apache-2.0, "Copyright 2026 NeuroLift Technologies, LLC") and restore the README license reference.

### Thread: TOI-LICENSE-ROOT
**Status:** open
**Owner:** Joshua W. Dorsey, Sr.
**Started:** 2026-05-29
**Last updated:** 2026-05-29
**Summary:** The repository root `LICENSE` is still MIT ("Copyright (c) 2024 NeuroLift OTOI Framework Contributors"), while the `.toi` standard and package were chosen to be Apache-2.0. A repo-wide MIT→Apache-2.0 relicense touches prior contributors' MIT-licensed work, so it was not done unilaterally during the foundation pour.
**Blockers:** Maintainer to confirm the relicense and reconcile the prior "Contributors" copyright before flipping.
**Next action:** Maintainer to flip the root `LICENSE` to Apache-2.0 in the follow-up PR, or explicitly decide to keep the repo MIT with the package Apache-2.0 inside it (legally compatible).
