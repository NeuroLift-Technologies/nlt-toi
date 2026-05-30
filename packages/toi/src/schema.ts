/**
 * Canonical `.toi` v1.0.0 schema — the single source of truth.
 *
 * This Zod schema defines the normative shape of a Terms of Interaction
 * document. The TypeScript types (`types.ts`) and the published JSON Schema
 * artifact (`scripts/build-schema.ts`) are both derived from it, so the three
 * never drift.
 *
 * Forward compatibility is structural: every object is a `looseObject`, so a
 * v1.0.0 parser preserves (never rejects) keys it does not recognize. This is
 * how the standard stays additive across minor versions.
 *
 * Sectioning rationale:
 *   - Reserved `$`-prefixed keys carry document metadata and the signature.
 *   - `identity` is the only required content section (it must name an author).
 *   - The remaining sections are optional; absence means "no stated preference,"
 *     which a consumer resolves against lower tiers and platform defaults.
 *
 * Note: multi-agent orchestration content does NOT live here — it belongs to
 * the `.otoi` honoring layer. The one place free-form data is permitted is
 * `custom`.
 */
import { z } from "zod";
import { TOI_TIERS } from "./constants.js";

/** Semantic version, e.g. `1.0.0`, `1.2.0-rc.1`, `1.0.0+build.5`. */
const semver = z
  .string()
  .regex(
    /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/,
    "must be a semantic version (MAJOR.MINOR.PATCH)",
  );

/** ISO 8601 calendar date or date-time (offset optional). */
const isoDateTime = z
  .string()
  .regex(
    /^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})?)?$/,
    "must be an ISO 8601 date or date-time",
  );

/** RFC 4122 version-4 UUID. */
const uuidV4 = z
  .string()
  .regex(
    /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
    "must be a version-4 UUID",
  );

/**
 * Detached Ed25519 signature envelope. The signed payload is the RFC 8785
 * canonical form of the document with this `$signature` field removed.
 */
export const toiSignatureSchema = z.looseObject({
  alg: z.literal("ed25519"),
  public_key: z.string().min(1),
  value: z.string().min(1),
});

/** Who authored the preferences. The author field is mandatory. */
const identitySchema = z.looseObject({
  author: z.string().min(1),
  handle: z.string().optional(),
  organization: z.string().optional(),
  pronouns: z.string().optional(),
});

/** How the person thinks and sustains attention. */
const cognitiveProfileSchema = z.looseObject({
  self_described: z.string().optional(),
  processing_style: z.enum(["sequential", "parallel", "associative", "variable"]).optional(),
  attention_model: z.enum(["sustained", "short-bursts", "hyperfocus-prone", "variable"]).optional(),
  scaffolding_preference: z.enum(["minimal", "moderate", "extensive", "step-by-step"]).optional(),
  energy_model: z.enum(["steady", "variable", "spoon-limited", "burst"]).optional(),
  thread_support: z.boolean().optional(),
  hyperfocus_protection: z.boolean().optional(),
  executive_function_support: z.boolean().optional(),
});

/** Data-sovereignty preferences. */
const privacySchema = z.looseObject({
  retention: z.enum(["session-only", "short-term", "long-term", "permanent", "user-controlled"]).optional(),
  cross_platform_sharing: z.enum(["never", "explicit-only", "aggregate-only", "research-approved"]).optional(),
  training_use: z.enum(["prohibited", "explicit-only", "anonymized-only", "permitted"]).optional(),
  analytics: z.enum(["prohibited", "opt-in", "anonymized-only", "permitted"]).optional(),
  override_rights: z.enum(["user-only", "delegated", "admin-allowed"]).optional(),
  data_requests: z.enum(["honored-immediately", "honored-on-request", "not-supported"]).optional(),
});

/** Who may initiate action, and where final authority rests. */
const agencySchema = z.looseObject({
  task_initiation: z.enum(["user-initiated", "ai-may-suggest", "ai-may-initiate"]).optional(),
  ai_suggestions: z.enum(["none", "on-request", "proactive"]).optional(),
  interruptibility: z.enum(["never", "urgent-only", "always"]).optional(),
  action_confirmation: z.enum(["always", "destructive-only", "never"]).optional(),
  override_authority: z.enum(["user-final", "shared", "ai-advisory"]).optional(),
});

/** How responses should be shaped. */
const communicationSchema = z.looseObject({
  tone: z.enum(["formal", "casual", "professional", "friendly", "direct", "adaptive"]).optional(),
  verbosity: z.enum(["minimal", "concise", "detailed", "comprehensive", "adaptive"]).optional(),
  structure: z.enum(["linear", "hierarchical", "visual", "bullet-points", "narrative"]).optional(),
  language: z.string().optional(),
  jargon_tolerance: z.enum(["none", "low", "moderate", "high"]).optional(),
  pattern_highlighting: z.boolean().optional(),
  summary_on_return: z.boolean().optional(),
  thread_reconnection: z.enum(["none", "brief-summary", "full-context"]).optional(),
});

/**
 * The canonical `.toi` document schema. `looseObject` at the top level keeps
 * unknown reserved/forward-compatible keys instead of stripping them.
 */
export const toiSchema = z.looseObject({
  // Reserved namespace.
  $toi: semver,
  $tier: z.enum(TOI_TIERS),
  $created: isoDateTime.optional(),
  $updated: isoDateTime.optional(),
  $id: uuidV4.optional(),
  $license: z.string().optional(),
  $signature: toiSignatureSchema.optional(),

  // Content sections.
  identity: identitySchema,
  cognitive_profile: cognitiveProfileSchema.optional(),
  privacy: privacySchema.optional(),
  agency: agencySchema.optional(),
  communication: communicationSchema.optional(),
  ethical_pillars: z.array(z.string()).optional(),

  // The only sanctioned home for free-form, non-schema data.
  custom: z.record(z.string(), z.unknown()).optional(),
});
