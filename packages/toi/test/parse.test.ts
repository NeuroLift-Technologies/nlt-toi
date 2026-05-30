/** Parse / serialize / guard behavior and error taxonomy. */
import { describe, it, expect } from "vitest";
import {
  parseToi,
  safeParseToi,
  serializeToi,
  isToi,
  ToiParseError,
  ToiValidationError,
} from "../src/index.js";

const minimal = { $toi: "1.0.0", $tier: "personal", identity: { author: "x" } };

describe("parse / serialize", () => {
  it("accepts both objects and JSON strings", () => {
    expect(parseToi(minimal).$tier).toBe("personal");
    expect(parseToi(JSON.stringify(minimal)).$tier).toBe("personal");
  });

  it("preserves unknown keys (forward compatibility)", () => {
    const doc = parseToi({ ...minimal, $futureReserved: 1, extra: { a: true } }) as Record<string, unknown>;
    expect(doc["$futureReserved"]).toBe(1);
    expect(doc["extra"]).toEqual({ a: true });
  });

  it("safeParse surfaces a parse error for bad JSON", () => {
    const r = safeParseToi("not json{");
    expect(r.success).toBe(false);
    if (!r.success) expect(r.error).toBeInstanceOf(ToiParseError);
  });

  it("safeParse surfaces a validation error with issues", () => {
    const r = safeParseToi({ $toi: "1.0.0", $tier: "nope", identity: { author: "x" } });
    expect(r.success).toBe(false);
    if (!r.success) {
      expect(r.error).toBeInstanceOf(ToiValidationError);
      expect((r.error as ToiValidationError).issues.length).toBeGreaterThan(0);
    }
  });

  it("rejects non-object JSON roots as parse errors", () => {
    expect(() => parseToi("[]")).toThrow(ToiParseError);
    expect(() => parseToi("42")).toThrow(ToiParseError);
    expect(() => parseToi("null")).toThrow(ToiParseError);
  });

  it("isToi guards values", () => {
    expect(isToi(minimal)).toBe(true);
    expect(isToi({})).toBe(false);
    expect(isToi("nope")).toBe(false);
  });

  it("pretty serialization round-trips and ends with a newline", () => {
    const s = serializeToi(minimal);
    expect(s.endsWith("\n")).toBe(true);
    expect(parseToi(s)).toEqual(parseToi(minimal));
  });

  it("compact serialization has no whitespace newline", () => {
    const s = serializeToi(minimal, { pretty: false });
    expect(s.includes("\n")).toBe(false);
  });

  it("reports the offending path in validation issues", () => {
    const r = safeParseToi({ ...minimal, communication: { tone: "bad" } });
    expect(r.success).toBe(false);
    if (!r.success && r.error instanceof ToiValidationError) {
      expect(r.error.issues.some((i) => i.path.includes("communication"))).toBe(true);
    }
  });

  it("rejects malformed signature encodings (SPEC §11.1)", () => {
    const r = safeParseToi({ ...minimal, $signature: { alg: "ed25519", public_key: "@@@", value: "@@@" } });
    expect(r.success).toBe(false);
    if (!r.success) expect(r.error).toBeInstanceOf(ToiValidationError);
  });
});
