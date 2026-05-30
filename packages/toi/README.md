# @neurolift/toi

Reference implementation of the **`.toi`** (Terms of Interaction) standard file type — part of the NeuroLift Solidarity Framework.

A `.toi` file is a user-authored, JSON-based document that declares **how an AI system should interact with a person**: communication style, cognitive profile, privacy floor, and agency boundaries. It is *data, not instructions* — no field is executable. Documents are forward-compatible, tier-resolvable, and optionally Ed25519-signed.

- **Extension:** `.toi`
- **Media type:** `application/toi+json`
- **Format version:** `1.0.0`
- **Spec:** see [`SPEC.md`](./SPEC.md) (normative)
- **License:** Apache-2.0

This package is the TypeScript reference library: types, validator, parser/serializer, an RFC 8785 (JCS) canonicalizer, and Ed25519 sign/verify — all driven by a single Zod schema that is the source of truth.

---

## Install

```sh
npm install @neurolift/toi
```

Requires Node.js ≥ 18. Ships as ESM with type declarations.

---

## Quick start

```ts
import {
  parseToi,
  serializeToi,
  generateKeyPair,
  signToi,
  verifyToi,
} from "@neurolift/toi";

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
import { resolveToi } from "@neurolift/toi";

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
import { canonicalize, signingPayload, signToi, verifyToi } from "@neurolift/toi";

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

Apache-2.0 © 2026 NeuroLift Technologies, LLC. See [`LICENSE`](./LICENSE).
