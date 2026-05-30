/**
 * Error taxonomy for the `.toi` reference library.
 *
 * Every error thrown by a public API is a `ToiError`, so callers can catch the
 * whole family with one `instanceof` check while still discriminating on `code`
 * for programmatic handling.
 */

export type ToiErrorCode =
  | "PARSE"
  | "VALIDATION"
  | "CANONICALIZATION"
  | "SIGNATURE"
  | "TIER";

/** A single schema violation, flattened to a dotted path and a message. */
export interface ToiIssue {
  readonly path: string;
  readonly message: string;
}

/** Base class for every error raised by this library. */
export class ToiError extends Error {
  readonly code: ToiErrorCode;
  constructor(code: ToiErrorCode, message: string, options?: { cause?: unknown }) {
    super(message, options);
    this.name = new.target.name;
    this.code = code;
    // Restore the prototype chain across the ES target's class transform.
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

/** Input was not well-formed JSON, or its root was not a JSON object. */
export class ToiParseError extends ToiError {
  constructor(message: string, options?: { cause?: unknown }) {
    super("PARSE", message, options);
  }
}

/** A document violated the canonical `.toi` schema. */
export class ToiValidationError extends ToiError {
  readonly issues: readonly ToiIssue[];
  constructor(message: string, issues: readonly ToiIssue[], options?: { cause?: unknown }) {
    super("VALIDATION", message, options);
    this.issues = issues;
  }
}

/** A value could not be canonicalized per RFC 8785 (e.g. a non-finite number). */
export class ToiCanonicalizationError extends ToiError {
  constructor(message: string, options?: { cause?: unknown }) {
    super("CANONICALIZATION", message, options);
  }
}

/** Signing or verification could not be performed (distinct from "signature did not match"). */
export class ToiSignatureError extends ToiError {
  constructor(message: string, options?: { cause?: unknown }) {
    super("SIGNATURE", message, options);
  }
}

/** Tier resolution encountered an inconsistency (e.g. no documents to resolve). */
export class ToiTierError extends ToiError {
  constructor(message: string, options?: { cause?: unknown }) {
    super("TIER", message, options);
  }
}
