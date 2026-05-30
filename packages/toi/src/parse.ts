/**
 * Parsing, validation, and serialization for `.toi` documents.
 *
 * `parseToi` is the throwing front door; `safeParseToi` is the Result-returning
 * variant for control-flow without exceptions. Both accept either a JSON string
 * (the on-disk form) or an already-parsed value.
 */
import type { z } from "zod";
import { toiSchema } from "./schema.js";
import type { ToiDocument } from "./types.js";
import { ToiError, ToiParseError, ToiValidationError, type ToiIssue } from "./errors.js";

/** Options controlling how a document is serialized to its on-disk form. */
export interface SerializeOptions {
  /** Pretty-print with 2-space indentation and a trailing newline. Default `true`. */
  pretty?: boolean;
  /** Validate against the canonical schema before serializing. Default `true`. */
  validate?: boolean;
}

/** A non-throwing parse outcome. */
export type SafeParseResult =
  | { success: true; data: ToiDocument }
  | { success: false; error: ToiError };

/**
 * Parse and validate a `.toi` document.
 *
 * @param input A JSON string or an already-parsed value.
 * @throws {ToiParseError} if `input` is not valid JSON or its root is not an object.
 * @throws {ToiValidationError} if the document violates the canonical schema.
 */
export function parseToi(input: unknown): ToiDocument {
  const json = typeof input === "string" ? parseJson(input) : input;
  assertJsonObject(json);
  const result = toiSchema.safeParse(json);
  if (!result.success) {
    throw toValidationError(result.error);
  }
  return result.data;
}

/** Parse and validate without throwing, returning a discriminated result. */
export function safeParseToi(input: unknown): SafeParseResult {
  let json: unknown;
  if (typeof input === "string") {
    try {
      json = JSON.parse(input);
    } catch (err) {
      return { success: false, error: new ToiParseError("Input is not valid JSON", { cause: err }) };
    }
  } else {
    json = input;
  }
  if (json === null || typeof json !== "object" || Array.isArray(json)) {
    return { success: false, error: new ToiParseError("A .toi document must be a JSON object") };
  }
  const result = toiSchema.safeParse(json);
  if (!result.success) {
    return { success: false, error: toValidationError(result.error) };
  }
  return { success: true, data: result.data };
}

/** Type guard: `true` when `input` is a valid `.toi` document. */
export function isToi(input: unknown): boolean {
  return safeParseToi(input).success;
}

/**
 * Serialize a document to its canonical on-disk JSON form. By default the
 * document is validated first and pretty-printed for human editing.
 *
 * Note: this is NOT the signing form — signatures are computed over the RFC 8785
 * canonical bytes (see `canonicalize`), independent of on-disk formatting.
 */
export function serializeToi(doc: unknown, options: SerializeOptions = {}): string {
  const { pretty = true, validate = true } = options;
  const data: unknown = validate ? parseToi(doc) : doc;
  const json = JSON.stringify(data, null, pretty ? 2 : 0);
  return pretty ? `${json}\n` : json;
}

function parseJson(input: string): unknown {
  try {
    return JSON.parse(input);
  } catch (err) {
    throw new ToiParseError("Input is not valid JSON", { cause: err });
  }
}

function assertJsonObject(value: unknown): void {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new ToiParseError("A .toi document must be a JSON object");
  }
}

function toValidationError(error: z.ZodError): ToiValidationError {
  const issues: ToiIssue[] = error.issues.map((issue) => ({
    path: issue.path.join("."),
    message: issue.message,
  }));
  const summary = issues
    .map((i) => (i.path ? `${i.path}: ${i.message}` : i.message))
    .join("; ");
  return new ToiValidationError(`Invalid .toi document — ${summary}`, issues);
}
