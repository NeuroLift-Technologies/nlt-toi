/**
 * RFC 8785 JSON Canonicalization Scheme (JCS).
 *
 * Produces the single deterministic serialization of a JSON value that the
 * `.toi` standard signs over. Two semantically equal documents always yield
 * byte-identical output, which is what makes Ed25519 signatures stable across
 * platforms and re-serializations.
 *
 * Rules implemented:
 *   - Object keys sorted by UTF-16 code unit (the ordering RFC 8785 mandates;
 *     JavaScript's `<` on strings already compares by UTF-16 code unit).
 *   - `undefined`-valued object properties dropped (not representable in JSON).
 *   - Strings serialized via `JSON.stringify` — its escaping matches RFC 8785.
 *   - Finite numbers serialized via `JSON.stringify`; ECMAScript
 *     `Number::toString` is exactly the numeric form RFC 8785 prescribes.
 *   - NaN / Infinity / -Infinity rejected (not valid JSON).
 *   - Arrays preserve element order; `undefined`/holes encoded as `null`.
 *   - Values exposing `toJSON()` (e.g. Date) are replaced by its result first,
 *     matching `JSON.stringify`.
 */
import { ToiCanonicalizationError } from "./errors.js";

/** A JSON value accepted by the canonicalizer. */
export type JsonValue =
  | null
  | boolean
  | number
  | string
  | JsonValue[]
  | { [key: string]: JsonValue | undefined };

/** Serialize `value` to its RFC 8785 canonical JSON string. */
export function canonicalize(value: unknown): string {
  const out: string[] = [];
  writeValue(value, out);
  return out.join("");
}

/** Canonical JSON encoded as UTF-8 bytes — the exact input to sign / verify. */
export function canonicalizeToBytes(value: unknown): Uint8Array {
  return new TextEncoder().encode(canonicalize(value));
}

function writeValue(value: unknown, out: string[]): void {
  if (value === null) {
    out.push("null");
    return;
  }

  // Replace values exposing a custom JSON representation (e.g. Date) with that
  // representation first, exactly as JSON.stringify does.
  if (typeof (value as { toJSON?: unknown }).toJSON === "function") {
    writeValue((value as { toJSON: () => unknown }).toJSON(), out);
    return;
  }

  switch (typeof value) {
    case "boolean":
      out.push(value ? "true" : "false");
      return;
    case "number":
      if (!Number.isFinite(value)) {
        throw new ToiCanonicalizationError(
          `Cannot canonicalize non-finite number: ${String(value)}`,
        );
      }
      out.push(JSON.stringify(value));
      return;
    case "string":
      out.push(JSON.stringify(value));
      return;
    case "bigint":
      throw new ToiCanonicalizationError("Cannot canonicalize a bigint value");
    case "function":
    case "symbol":
    case "undefined":
      throw new ToiCanonicalizationError(
        `Cannot canonicalize a value of type ${typeof value}`,
      );
  }

  if (Array.isArray(value)) {
    out.push("[");
    for (let i = 0; i < value.length; i++) {
      if (i > 0) out.push(",");
      const element = value[i];
      if (element === undefined) {
        out.push("null");
      } else {
        writeValue(element, out);
      }
    }
    out.push("]");
    return;
  }

  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).filter((k) => obj[k] !== undefined);
  keys.sort(compareCodeUnits);
  out.push("{");
  for (let i = 0; i < keys.length; i++) {
    if (i > 0) out.push(",");
    const key = keys[i]!;
    out.push(JSON.stringify(key));
    out.push(":");
    writeValue(obj[key], out);
  }
  out.push("}");
}

/** Compare two strings by UTF-16 code unit, per RFC 8785 §3.2.3. */
function compareCodeUnits(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0;
}
