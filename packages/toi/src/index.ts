/**
 * `@neurolift/toi` — reference implementation of the `.toi` (Terms of
 * Interaction) standard file type.
 *
 * This module is the stable public API. Everything re-exported here is covered
 * by semver; anything reached by deep-importing internal files is not.
 *
 * @example
 * ```ts
 * import { parseToi, signToi, verifyToi, generateKeyPair } from "@neurolift/toi";
 *
 * const doc = parseToi(await readFile("me.toi", "utf8"));
 * const { privateKey } = generateKeyPair();
 * const signed = signToi(doc, privateKey);
 * verifyToi(signed); // => true
 * ```
 */

// Constants and tier model.
export {
  TOI_FORMAT_VERSION,
  TOI_FILE_EXTENSION,
  TOI_MEDIA_TYPE,
  TOI_RESERVED_PREFIX,
  TOI_RESERVED_KEYS,
  TOI_TIERS,
  TIER_PRECEDENCE,
  TIER_RANK,
  type ToiTier,
} from "./constants.js";

// Schema (single source of truth) and inferred types.
export { toiSchema, toiSignatureSchema } from "./schema.js";
export type { ToiDocument, ToiSignature } from "./types.js";

// Parse / validate / serialize.
export {
  parseToi,
  safeParseToi,
  isToi,
  serializeToi,
  type SerializeOptions,
  type SafeParseResult,
} from "./parse.js";

// RFC 8785 canonicalization.
export { canonicalize, canonicalizeToBytes, type JsonValue } from "./canonicalize.js";

// Ed25519 signing / verification.
export {
  generateKeyPair,
  signToi,
  verifyToi,
  isSigned,
  signingPayload,
  type ToiKeyPair,
} from "./sign.js";

// Tier precedence resolution (§5).
export {
  resolveToi,
  sortByPrecedence,
  compareTier,
  type ResolveOptions,
} from "./tier.js";

// Error taxonomy.
export {
  ToiError,
  ToiParseError,
  ToiValidationError,
  ToiCanonicalizationError,
  ToiSignatureError,
  ToiTierError,
  type ToiErrorCode,
  type ToiIssue,
} from "./errors.js";
