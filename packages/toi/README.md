# TOI/OTOI Framework

An open framework for human-defined AI interaction and advocacy.

Companies establish Terms of Service that humans must agree to when using their AI services. Humans should likewise be able to define and declare their Terms of Interaction for the AI systems they engage with.

The TOI/OTOI Framework establishes this reciprocal relationship through two distinct but interdependent components.

## TOI — Terms of Interaction

The human-facing component of the framework.

TOI enables humans to define, declare, own and transport their interaction preferences, cognitive needs, privacy boundaries, consent requirements and expectations.

Through existing preference extraction and AI-assisted population, humans can create a portable, machine-readable `.toi` document without requiring technical expertise.

## OTOI — Orchestrated Terms of Interaction

The AI-facing component of the framework.

OTOI first checks a human's complete TOI against the platform's boundaries: the model provider's limits and the deployer's Terms of Service. Every check must pass. If any check fails, the human is told every conflict, and the TOI is not honored until it is corrected.

When every check passes, the AI understands, acknowledges and honors the human's TOI. For most people, this is the AI they already use and have history with, so the first AI to honor their TOI becomes their Orchestrator and advocate by default. The human can designate a different compatible AI at any time, with one active Orchestrator per project.

In multi-agent collaboration, the Orchestrator is responsible for determining whether other AI systems can honor the human's TOI.

## Separate components. One framework.

TOI and OTOI have distinct responsibilities but must coexist to fulfill the framework's purpose.

A TOI without OTOI is a declaration with no way to be honored. OTOI without TOI has no human-declared terms to honor.

Together, they establish a portable, human-centered relationship between humans and artificial intelligence.

The TOI/OTOI Framework forms the governance foundation of the Solidarity Framework, supported by RRT AIdvocAIte, the Sleepwalker Protocol and the Agent Solidarity Framework Deployment Kit (ASFDK).

**Companies have Terms of Service. Humans deserve Terms of Interaction.**
**Capability ≠ Authority.**
**We're Not Competing. We're Completing.**
**Human & AI Solidarity Without Singularity.**

## Install

```sh
npm install @neurolift-technologies/toi
```

Requires Node.js ≥ 18. Ships as ESM with type declarations.

Published on npm as `@neurolift-technologies/toi` (version `1.0.0`, `Apache-2.0`).

---

## Quick start

```ts
import {
  parseToi,
  serializeToi,
  generateKeyPair,
  signToi,
  verifyToi,
} from "@neurolift-technologies/toi";

// Parse + validate (accepts a JSON string or an already-parsed object).
const doc = parseToi(await readFile("me.toi", "utf8"));

// Sign over the canonical form, then verify.
const { privateKey } = generateKeyPair();
const signed = signToi(doc, privateKey);
verifyToi(signed); // => true

// Serialize back to disk (pretty, trailing newline by default).
await writeFile("me.toi", serializeToi(signed));
```

A minimal valid document is just a version, a tier, and an author:

```json
{
  "$toi": "1.0.0",
  "$tier": "personal",
  "identity": { "author": "your-name-or-pseudonym" }
}
```

---

## File format at a glance

A `.toi` file is a single UTF-8 JSON object. Reserved keys use a `$` prefix; everything else is content.

| Key | Required | Meaning |
| --- | --- | --- |
| `$toi` | yes | Format version (semver). |
| `$tier` | yes | `personal` \| `community` \| `project`. |
| `$created` / `$updated` | no | ISO 8601 timestamps. |
| `$id` | no | UUIDv4 identifying the document. |
| `$license` | no | SPDX license identifier for the document's contents. |
| `$signature` | no | Ed25519 signature envelope (see below). |
| `identity` | yes | `author` (required) + optional handle/organization/pronouns. |
| `cognitive_profile` | no | Processing style, attention model, scaffolding, energy model, supports. |
| `privacy` | no | Retention, sharing, training use, analytics, override/data rights. |
| `agency` | no | Task initiation, suggestions, interruptibility, confirmation, override authority. |
| `communication` | no | Tone, verbosity, structure, jargon tolerance, thread reconnection. |
| `ethical_pillars` | no | Free array of pillar strings. |
| `custom` | no | The only place non-schema content is permitted. |

**Unknown keys are preserved, never rejected** — a v1.0.0 reader round-trips fields it does not understand. See [`SPEC.md`](./SPEC.md) for the exact enums and rules.

---

## Tier resolution

A person may carry several `.toi` documents at different tiers. Precedence is **`personal` > `community` > `project` > platform defaults**, and `personal` is *terminal*: lower tiers only fill gaps the higher tiers left unset. They never override a value the user set.

```ts
import { resolveToi } from "@neurolift-technologies/toi";

const effective = resolveToi([projectDoc, communityDoc, personalDoc], {
  platformDefaults: { communication: { verbosity: "concise" } },
});
// effective.$tier === "personal"; personal values win, others gap-fill.
```

`resolveToi` does not mutate its inputs.

---

## Signing & canonicalization

Signatures bind a document's **content** to a key. The payload is the RFC 8785 (JCS) canonical UTF-8 serialization of the document with `$signature` removed, so a signature survives reformatting and key reordering.

```ts
import { canonicalize, signingPayload, signToi, verifyToi } from "@neurolift-technologies/toi";

canonicalize({ b: 1, a: 2 }); // => '{"a":2,"b":1}'  (sorted, minimal)

const signed = signToi(doc, privateKey);
signed.$signature; // => { alg: "ed25519", public_key: "<base64url>", value: "<base64url>" }
verifyToi(signed); // => true

// Tampering with any signed content makes verification fail.
```

`verifyToi` is defensive: unsigned or malformed documents return `false` rather than throwing. A signature proves the holder of a key signed the content — it does **not** prove identity. Private keys MUST NEVER appear in a `.toi` file.

---

## API reference

All stable exports come from the package root. Deep imports into `src/*` are not covered by semver.

**Parse / validate / serialize**
- `parseToi(input)` — parse a string or object; throws `ToiParseError` / `ToiValidationError`.
- `safeParseToi(input)` — non-throwing; returns `{ success: true, data } | { success: false, error }`.
- `isToi(input)` — boolean type guard.
- `serializeToi(doc, { pretty = true })` — canonical-enough JSON for disk; pretty adds a trailing newline.

**Canonicalization (RFC 8785)**
- `canonicalize(value)` — JCS string.
- `canonicalizeToBytes(value)` — JCS UTF-8 bytes. Throws `ToiCanonicalizationError` on non-finite numbers.

**Signing (Ed25519)**
- `generateKeyPair()` — `{ privateKey, publicKey, publicKeyBase64Url }`.
- `signToi(doc, privateKey)` — returns a copy with a `$signature`.
- `verifyToi(doc)` — boolean.
- `isSigned(doc)` / `signingPayload(doc)` — introspection helpers.

**Tier resolution**
- `resolveToi(docs, { platformDefaults? })`, `sortByPrecedence(docs)`, `compareTier(a, b)`.

**Schema & types**
- `toiSchema`, `toiSignatureSchema` (Zod) — the source of truth.
- `ToiDocument`, `ToiSignature` (inferred types).

**Errors**
- `ToiError` (base) + `ToiParseError`, `ToiValidationError` (carries `issues`), `ToiCanonicalizationError`, `ToiSignatureError`, `ToiTierError`.

**Constants**
- `TOI_FORMAT_VERSION`, `TOI_FILE_EXTENSION`, `TOI_MEDIA_TYPE`, `TOI_RESERVED_KEYS`, `TOI_TIERS`, `TIER_PRECEDENCE`, `TIER_RANK`.

---

## JSON Schema artifact

A JSON Schema (draft 2020-12) is generated from the Zod schema for editor tooling and cross-language validation:

```sh
npm run build:schema   # writes schema/toi-1.0.0.schema.json
```

The Zod schema remains authoritative; the JSON Schema is a derived convenience.

---

## Development

```sh
npm run typecheck   # tsc --noEmit (strict)
npm test            # vitest run — conformance + unit suites
npm run build       # emit dist/ with declarations
```

Conformance fixtures live in [`test/fixtures/`](./test/fixtures): valid documents that must parse, invalid documents that must be rejected, and a deterministic Ed25519 known-answer vector (`signed.toi`) for cross-implementation checks.

---

## License

Apache-2.0 © 2026 NeuroLift Technologies, LLC. SPDX-License-Identifier: `Apache-2.0`.
