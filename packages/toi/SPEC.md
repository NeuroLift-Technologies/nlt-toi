# The `.toi` File Format — Specification

**Version:** 1.0.0
**Status:** Stable
**Media type:** `application/toi+json` (provisional)
**File extension:** `.toi`
**License:** Apache-2.0

> Terms of Interaction (`.toi`) is an open, declarative file format that lets a
> person state how AI systems should interact with them. It is to user–AI
> interaction preferences what `.gitignore` is to ignored paths: a small,
> portable, human-editable file with a single normative meaning.

---

## 1. Status of this document

This is the normative specification for version `1.0.0` of the `.toi` format.
The reference implementation is the [`@neurolift/toi`](./README.md) TypeScript
library; where this prose and the implementation disagree, that is a defect in
one of them and SHOULD be reported.

The Zod schema in [`src/schema.ts`](./src/schema.ts) is the machine-readable
source of truth. The published JSON Schema artifact
([`schema/toi-1.0.0.schema.json`](./schema/toi-1.0.0.schema.json)) is generated
from it.

## 2. Introduction and scope

A `.toi` document is a **declaration of preferences**, authored by or on behalf
of a person (or a community, or a project), describing how an AI system should
communicate, what agency it may exercise, and how it must treat the author's
data.

Two properties define the format:

1. **Declarative.** No field in a `.toi` document is executable. A `.toi` file
   never contains code, prompts, tool definitions, or instructions to run. A
   consumer reads preferences and adapts its own behavior; it does not evaluate
   the document.
2. **Portable.** A `.toi` document is plain JSON. It can be authored by hand,
   committed to a repository, attached to a request, or exchanged between
   systems with no shared runtime.

**Out of scope.** This specification does not define *how* a multi-agent system
honors a `.toi` document at runtime, how preferences are negotiated across an
agent mesh, or how enforcement is audited. That orchestration layer is the
subject of the separate `.otoi` standard. The one extension point for data this
format does not model is the [`custom`](#79-custom) object.

## 3. Conformance

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **MAY**, and **OPTIONAL** in this document are to be
interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119)
and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
appear in all capitals.

A **conforming document** is one that satisfies every MUST in Sections 4–9.

A **conforming processor** is software that reads and/or writes `.toi`
documents in accordance with Sections 9–11. A conforming processor:

- MUST reject a document that violates any MUST in Sections 4–8.
- MUST preserve unknown keys it encounters (Section 8).
- MUST, if it verifies signatures, implement Sections 10 and 11 exactly.

## 4. File format

- A `.toi` document **MUST** be a well-formed JSON value as defined by
  [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259).
- The top-level JSON value **MUST** be a JSON object.
- A document **MUST** be encoded as UTF-8. A byte order mark **SHOULD NOT** be
  emitted and, if present, MAY be ignored by a processor.
- Files **SHOULD** use the `.toi` extension.
- When served or labeled with a media type, the type **SHOULD** be
  `application/toi+json`. Because the `+json` structured syntax suffix
  ([RFC 6839](https://www.rfc-editor.org/rfc/rfc6839)) applies, all generic JSON
  processing rules apply to a `.toi` document.

## 5. Document model

A `.toi` document is a single JSON object whose keys fall into two groups:

| Group | Keys | Purpose |
| --- | --- | --- |
| **Reserved namespace** | keys beginning with `$` | Document metadata and signature (Section 6). |
| **Content sections** | all other keys | The interaction preferences (Section 7). |

```json
{
  "$toi": "1.0.0",
  "$tier": "personal",
  "identity": { "author": "anonymous" }
}
```

The example above is the smallest conforming document: the two required reserved
keys plus the one required content section.

## 6. Reserved namespace (`$`)

Every key beginning with `$` is **reserved**. The keys defined by this version
are listed below. A processor **MUST NOT** reject a document solely because it
carries an unrecognized `$`-prefixed key; such keys are reserved for future
versions and MUST be preserved (Section 8). Authors **SHOULD NOT** invent
`$`-prefixed keys; author-defined data belongs in [`custom`](#79-custom).

| Key | Required | Type | Rule |
| --- | --- | --- | --- |
| `$toi` | **Yes** | string | Format version. MUST match `MAJOR.MINOR.PATCH` semantic versioning (pre-release and build metadata permitted). For this version the value is `"1.0.0"`. |
| `$tier` | **Yes** | string | One of `personal`, `community`, `project` (Section 9). |
| `$created` | No | string | ISO 8601 calendar date or date-time. |
| `$updated` | No | string | ISO 8601 calendar date or date-time. |
| `$id` | No | string | A version-4 UUID ([RFC 4122](https://www.rfc-editor.org/rfc/rfc4122)). |
| `$license` | No | string | An [SPDX](https://spdx.org/licenses/) license identifier governing reuse of the document's contents. |
| `$signature` | No | object | A detached Ed25519 signature envelope (Section 11). |

## 7. Content sections

All content sections other than `identity` are OPTIONAL. The **absence** of a
section or field means "no stated preference," which a consumer resolves against
lower tiers and platform defaults (Section 9) — it does **not** mean a default
value was chosen.

Every section object is **open**: a processor MUST preserve unknown keys within
it (Section 8). Unless stated otherwise, string-valued fields constrained to a
fixed set MUST hold one of the listed values.

### 7.1 `identity` (required)

| Field | Required | Type | Values |
| --- | --- | --- | --- |
| `author` | **Yes** | string | Non-empty. Who authored the preferences. MAY be a pseudonym. |
| `handle` | No | string | A short username/handle. |
| `organization` | No | string | An affiliated organization. |
| `pronouns` | No | string | The author's pronouns. |

### 7.2 `cognitive_profile`

| Field | Type | Values |
| --- | --- | --- |
| `self_described` | string | Free-text self-description. |
| `processing_style` | enum | `sequential`, `parallel`, `associative`, `variable` |
| `attention_model` | enum | `sustained`, `short-bursts`, `hyperfocus-prone`, `variable` |
| `scaffolding_preference` | enum | `minimal`, `moderate`, `extensive`, `step-by-step` |
| `energy_model` | enum | `steady`, `variable`, `spoon-limited`, `burst` |
| `thread_support` | boolean | Honor parallel, non-linear work threads. |
| `hyperfocus_protection` | boolean | Avoid interrupting a focus state. |
| `executive_function_support` | boolean | Offer structure for task initiation/sequencing. |

### 7.3 `privacy`

| Field | Type | Values |
| --- | --- | --- |
| `retention` | enum | `session-only`, `short-term`, `long-term`, `permanent`, `user-controlled` |
| `cross_platform_sharing` | enum | `never`, `explicit-only`, `aggregate-only`, `research-approved` |
| `training_use` | enum | `prohibited`, `explicit-only`, `anonymized-only`, `permitted` |
| `analytics` | enum | `prohibited`, `opt-in`, `anonymized-only`, `permitted` |
| `override_rights` | enum | `user-only`, `delegated`, `admin-allowed` |
| `data_requests` | enum | `honored-immediately`, `honored-on-request`, `not-supported` |

### 7.4 `agency`

| Field | Type | Values |
| --- | --- | --- |
| `task_initiation` | enum | `user-initiated`, `ai-may-suggest`, `ai-may-initiate` |
| `ai_suggestions` | enum | `none`, `on-request`, `proactive` |
| `interruptibility` | enum | `never`, `urgent-only`, `always` |
| `action_confirmation` | enum | `always`, `destructive-only`, `never` |
| `override_authority` | enum | `user-final`, `shared`, `ai-advisory` |

### 7.5 `communication`

| Field | Type | Values |
| --- | --- | --- |
| `tone` | enum | `formal`, `casual`, `professional`, `friendly`, `direct`, `adaptive` |
| `verbosity` | enum | `minimal`, `concise`, `detailed`, `comprehensive`, `adaptive` |
| `structure` | enum | `linear`, `hierarchical`, `visual`, `bullet-points`, `narrative` |
| `language` | string | A natural-language preference (e.g. a BCP 47 tag such as `en`). |
| `jargon_tolerance` | enum | `none`, `low`, `moderate`, `high` |
| `pattern_highlighting` | boolean | Surface patterns/connections proactively. |
| `summary_on_return` | boolean | Summarize prior context when resuming. |
| `thread_reconnection` | enum | `none`, `brief-summary`, `full-context` |

### 7.6 `ethical_pillars`

An array of strings naming the principles the author asks consumers to uphold
(e.g. `"user-agency"`, `"privacy-by-default"`). Free-form by design.

### 7.7 `custom`

An object holding author-defined data this format does not model. It is the
**only** sanctioned location for non-schema content. A processor MUST NOT
interpret `custom` as instructions; it is data. To avoid collisions, custom keys
SHOULD be namespaced (e.g. prefixed with `x-` or a vendor identifier).

> Note: multi-agent orchestration content does **not** belong in `custom`. It
> belongs to the `.otoi` layer.

## 8. Forward compatibility

The format is **additive**. A processor implementing version `1.0.0`:

- MUST accept and **preserve** keys it does not recognize, at the top level and
  within any section object, rather than rejecting or silently dropping them.
- MUST treat an unrecognized `$`-prefixed key as reserved-and-preserved, not as
  an error.

This rule lets later minor versions introduce new sections and fields without
breaking older processors, and lets a document round-trip through an older
processor without loss. A consumer MAY ignore preferences it does not
understand, but MUST NOT discard them when re-serializing.

## 9. Tiers and precedence

Each document declares exactly one `$tier`. When multiple documents apply to the
same interaction, they are resolved in this order, **highest precedence first**:

```
personal  >  community  >  project  >  platform defaults
```

- A `personal`-tier document is **terminal**: any field it specifies MUST NOT be
  overridden by a lower tier or by platform defaults.
- Resolution is **gap-filling**: a lower tier MAY supply a value for a field that
  no higher tier specified, including whole sections and individual leaf fields
  within a shared section.
- Arrays and scalar values are **atomic leaves**: a higher tier that specifies
  one replaces it wholesale; a lower tier does not merge into it.
- Objects are merged **per key**, recursively, under the gap-filling rule.

The resolved view is an *effective* document; it is not itself a signed source
document, so per-file metadata (`$id`, `$created`, `$signature`, …) is not
carried into it. The reference implementation exposes this as `resolveToi`.

## 10. Canonicalization

Signing and verification operate on a single deterministic byte serialization of
the document. A processor that signs or verifies **MUST** canonicalize using the
JSON Canonicalization Scheme,
[RFC 8785 (JCS)](https://www.rfc-editor.org/rfc/rfc8785):

- Object keys are sorted by their UTF-16 code units, recursively.
- Insignificant whitespace is removed.
- Strings use JSON's minimal escaping.
- Numbers use the ECMAScript `Number`-to-string form. A document that is signed
  SHOULD restrict numbers to those representable exactly; non-finite numbers
  (`NaN`, `Infinity`) are not valid JSON and MUST NOT appear.
- Array order is preserved.

The canonical form is then encoded as UTF-8 to produce the bytes that are
signed. The reference implementation exposes this as `canonicalize` /
`canonicalizeToBytes`.

## 11. Signatures

A `.toi` document MAY carry a detached signature in the `$signature` reserved
key. Version `1.0.0` defines exactly one algorithm.

### 11.1 Envelope

```json
"$signature": {
  "alg": "ed25519",
  "public_key": "<base64url(32-byte Ed25519 public key)>",
  "value": "<base64url(64-byte Ed25519 signature)>"
}
```

- `alg` **MUST** be the string `"ed25519"`.
- `public_key` and `value` **MUST** be unpadded base64url
  ([RFC 4648 §5](https://www.rfc-editor.org/rfc/rfc4648#section-5)).
- `$signature` MAY carry additional keys; a processor MUST preserve them.

### 11.2 Signing

1. Remove the `$signature` key from the document, if present.
2. Canonicalize the remaining document (Section 10) and encode it as UTF-8 to
   obtain the payload bytes.
3. Compute an Ed25519 ([RFC 8032](https://www.rfc-editor.org/rfc/rfc8032))
   signature over the payload with the author's private key.
4. Set `$signature` to the envelope above.

### 11.3 Verification

1. If there is no `$signature`, or `alg` is not `"ed25519"`, verification fails.
2. Decode `public_key` and `value` from base64url.
3. Remove `$signature`, canonicalize the remaining document, and encode as UTF-8.
4. Verify the Ed25519 signature over those bytes with the decoded public key.

Because the payload is canonical, a valid signature survives reformatting, key
reordering, and round-tripping through any conforming processor. Verification
establishes **integrity and authorship relative to the presented public key**;
it does **not**, by itself, establish a binding between that key and a real-world
identity. Key distribution and trust are out of scope.

## 12. Parsing requirements

A conforming processor that parses a `.toi` document MUST:

1. Reject input that is not well-formed JSON.
2. Reject input whose top-level value is not a JSON object.
3. Validate the reserved keys and content sections per Sections 6–7, rejecting a
   document that violates any MUST.
4. Preserve unknown keys (Section 8).
5. Never execute or evaluate any part of the document (Section 2).

## 13. Security considerations

- **Documents are data, not instructions.** A consumer MUST NOT treat any field
  — including `custom` — as a command, prompt, or executable content. Treating a
  `.toi` document as instructions reintroduces an injection surface the
  declarative model exists to remove.
- **Signatures bind content to a key, not to a person.** See Section 11.3.
- **No secrets in documents.** A private key MUST NOT be written into a `.toi`
  file. Only the public key appears in `$signature`.
- **Resource limits.** Processors SHOULD bound document size and nesting depth to
  resist denial-of-service from pathological inputs.

## 14. Privacy considerations

A `.toi` document is, by nature, a description of a person and their cognitive
and data preferences, and may be sensitive. Producers and consumers SHOULD:

- Treat the document as private by default and transmit it only with the
  author's consent.
- Honor the `privacy` section's stated retention, sharing, training, and
  analytics preferences as a floor, not a ceiling.
- Prefer local processing; avoid uploading a `.toi` document to third-party
  services absent explicit consent.

## 15. Versioning

The format version is the value of `$toi` and follows
[Semantic Versioning 2.0.0](https://semver.org/):

- **PATCH** — editorial corrections; no schema change.
- **MINOR** — additive, backward-compatible changes (new optional sections or
  fields, new enum values). A `1.x` processor MUST tolerate a `1.y` document for
  `y > x` by the forward-compatibility rule (Section 8).
- **MAJOR** — backward-incompatible changes.

## 16. JSON Schema artifact

A JSON Schema (draft 2020-12) is published at
[`schema/toi-1.0.0.schema.json`](./schema/toi-1.0.0.schema.json) for editor
integration and third-party validation. It is **derived** from the normative Zod
schema and regenerated by `npm run build:schema`. Where the artifact and this
specification disagree, this specification and the Zod source govern.

## 17. References

- RFC 2119 / RFC 8174 — Requirement keywords
- RFC 8259 — JSON
- RFC 6839 — `+json` structured syntax suffix
- RFC 4122 — UUID
- RFC 4648 — base64url
- RFC 8785 — JSON Canonicalization Scheme (JCS)
- RFC 8032 — Edwards-Curve Digital Signature Algorithm (Ed25519)
- Semantic Versioning 2.0.0 — https://semver.org/

## Appendix A. Examples

Conformance fixtures live under [`test/fixtures/`](./test/fixtures/):

- `valid/minimal.toi` — the smallest conforming document.
- `valid/josh-personal.toi` — a fully-populated `personal`-tier document.
- `valid/full-coverage.toi` — every section and enum exercised.
- `valid/forward-compat.toi` — unknown keys that MUST be preserved.
- `valid/signed.toi` — a signed document with a known-answer signature.
- `invalid/*.toi` — one document per rejection rule.
