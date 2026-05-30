/**
 * Canonical constants for the `.toi` standard file type.
 *
 * These values are normative. Downstream consumers (e.g. the `.otoi` honoring
 * layer in `nlt-otoi`) should import them rather than re-declaring literals.
 */

/** Format version of the `.toi` specification this library implements. */
export const TOI_FORMAT_VERSION = "1.0.0";

/** Canonical file extension for Terms of Interaction documents. */
export const TOI_FILE_EXTENSION = ".toi";

/**
 * Registered media (MIME) type for `.toi` documents. Structured-syntax suffix
 * form per RFC 6839 — a `.toi` file is always a JSON document.
 */
export const TOI_MEDIA_TYPE = "application/toi+json";

/** Prefix marking the reserved namespace. Every `$`-prefixed key is reserved. */
export const TOI_RESERVED_PREFIX = "$";

/**
 * The set of reserved top-level keys defined by v1.0.0. Keys outside this set
 * that still begin with `$` are reserved for future use and SHOULD NOT be
 * authored by users (user-defined data belongs under `custom`).
 */
export const TOI_RESERVED_KEYS = [
  "$toi",
  "$tier",
  "$created",
  "$updated",
  "$id",
  "$license",
  "$signature",
] as const;

/** The three interaction tiers, in descending order of precedence. */
export const TOI_TIERS = ["personal", "community", "project"] as const;

export type ToiTier = (typeof TOI_TIERS)[number];

/**
 * Tier precedence, highest first. A `personal`-tier file is terminal: any field
 * it specifies cannot be overridden by a lower tier or by platform defaults.
 *
 * Resolution order: personal > community > project > platform defaults.
 */
export const TIER_PRECEDENCE: readonly ToiTier[] = TOI_TIERS;

/** Numeric rank for each tier — lower number means higher precedence. */
export const TIER_RANK: Readonly<Record<ToiTier, number>> = {
  personal: 0,
  community: 1,
  project: 2,
};
