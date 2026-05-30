/**
 * Tier precedence and resolution (§5 of the spec).
 *
 * Resolution order, highest first: personal > community > project > platform
 * defaults. A `personal`-tier file is terminal — any field it specifies cannot
 * be overridden by a lower tier or by platform defaults.
 *
 * `resolveToi` is the precedence *primitive*: it folds several single-tier
 * documents into one effective view. Full multi-agent orchestration (how an
 * agent mesh honors that view) is out of scope here — that is the `.otoi`
 * layer's job.
 */
import { TIER_RANK, type ToiTier } from "./constants.js";
import { ToiTierError } from "./errors.js";
import type { ToiDocument } from "./types.js";

/** Compare two tiers by precedence. Negative means `a` outranks `b`. */
export function compareTier(a: ToiTier, b: ToiTier): number {
  return TIER_RANK[a] - TIER_RANK[b];
}

/** Return a copy of `documents` ordered highest-precedence first. */
export function sortByPrecedence<T extends { $tier: ToiTier }>(documents: readonly T[]): T[] {
  return [...documents].sort((a, b) => compareTier(a.$tier, b.$tier));
}

/** Options for {@link resolveToi}. */
export interface ResolveOptions {
  /** Lowest-precedence fallback values, applied only where nothing else set a field. */
  platformDefaults?: Record<string, unknown>;
}

const RESERVED_KEYS = new Set([
  "$toi",
  "$tier",
  "$created",
  "$updated",
  "$id",
  "$license",
  "$signature",
]);

/**
 * Fold one or more single-tier documents into one effective document.
 *
 * Merge semantics implement terminal precedence: documents are processed
 * highest-tier first, and a field already set by a higher tier is never
 * overwritten. Nested objects are deep-filled (a lower tier may supply leaves a
 * higher tier left unspecified); arrays and scalars are atomic leaves.
 *
 * The result carries the highest tier's `$toi` and `$tier`; per-file metadata
 * (`$id`, `$created`, `$signature`, ...) is intentionally not merged, because a
 * synthesized view is not itself a signed source document.
 */
export function resolveToi(documents: readonly ToiDocument[], options: ResolveOptions = {}): ToiDocument {
  if (documents.length === 0) {
    throw new ToiTierError("resolveToi requires at least one document");
  }
  const ordered = sortByPrecedence(documents);
  const top = ordered[0]!;

  const result: Record<string, unknown> = {
    $toi: top.$toi,
    $tier: top.$tier,
  };

  for (const doc of ordered) {
    fillInto(result, stripReserved(doc as Record<string, unknown>));
  }
  if (options.platformDefaults) {
    fillInto(result, options.platformDefaults);
  }

  return result as ToiDocument;
}

function stripReserved(doc: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const key of Object.keys(doc)) {
    if (!RESERVED_KEYS.has(key)) out[key] = doc[key];
  }
  return out;
}

/** Copy keys from `source` into `target` without overwriting set leaves. */
function fillInto(target: Record<string, unknown>, source: Record<string, unknown>): void {
  for (const key of Object.keys(source)) {
    const sourceValue = source[key];
    if (sourceValue === undefined) continue;
    const targetValue = target[key];
    if (isPlainObject(targetValue) && isPlainObject(sourceValue)) {
      fillInto(targetValue, sourceValue);
    } else if (!(key in target) || target[key] === undefined) {
      target[key] = clone(sourceValue);
    }
  }
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function clone<T>(value: T): T {
  return typeof structuredClone === "function"
    ? structuredClone(value)
    : (JSON.parse(JSON.stringify(value)) as T);
}
