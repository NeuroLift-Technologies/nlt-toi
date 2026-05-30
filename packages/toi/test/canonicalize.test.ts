/** RFC 8785 (JCS) known-answer tests. */
import { describe, it, expect } from "vitest";
import { canonicalize, canonicalizeToBytes, ToiCanonicalizationError } from "../src/index.js";

describe("RFC 8785 canonicalization", () => {
  it("sorts object keys by UTF-16 code unit, recursively", () => {
    expect(canonicalize({ b: 1, a: [{ d: true, c: null }, "x"], "ä": 2, A: 3 })).toBe(
      '{"A":3,"a":[{"c":null,"d":true},"x"],"b":1,"ä":2}',
    );
  });

  it("preserves array element order", () => {
    expect(canonicalize([3, 1, 2])).toBe("[3,1,2]");
  });

  it("serializes JSON literals", () => {
    expect(canonicalize({ t: true, f: false, n: null })).toBe('{"f":false,"n":null,"t":true}');
  });

  it("drops undefined-valued object properties", () => {
    expect(canonicalize({ a: 1, b: undefined })).toBe('{"a":1}');
  });

  it("encodes array holes / undefined elements as null", () => {
    expect(canonicalize([1, undefined, 3])).toBe("[1,null,3]");
  });

  it("rejects non-finite numbers", () => {
    expect(() => canonicalize({ x: Infinity })).toThrow(ToiCanonicalizationError);
    expect(() => canonicalize(-Infinity)).toThrow(ToiCanonicalizationError);
    expect(() => canonicalize(NaN)).toThrow(ToiCanonicalizationError);
  });

  it("matches ECMAScript number serialization", () => {
    expect(canonicalize(1.5)).toBe("1.5");
    expect(canonicalize(-0)).toBe("0");
    expect(canonicalize(1e21)).toBe("1e+21");
    expect(canonicalize(100)).toBe("100");
  });

  it("emits UTF-8 bytes", () => {
    const text = '{"ä":1}';
    const bytes = canonicalizeToBytes({ "ä": 1 });
    expect(new TextDecoder().decode(bytes)).toBe(text);
    // "ä" is one UTF-16 unit but two UTF-8 bytes.
    expect(bytes.length).toBe(text.length + 1);
  });

  it("escapes strings per JSON", () => {
    expect(canonicalize('a"b\\c')).toBe('"a\\"b\\\\c"');
  });

  it("honors toJSON like JSON.stringify (e.g. Date)", () => {
    const iso = "2026-05-29T00:00:00.000Z";
    expect(canonicalize(new Date(iso))).toBe(JSON.stringify(iso));
    expect(canonicalize({ when: new Date(iso) })).toBe(`{"when":${JSON.stringify(iso)}}`);
  });

  it("rejects non-plain objects (Map, class instances)", () => {
    expect(() => canonicalize(new Map([["a", 1]]))).toThrow(ToiCanonicalizationError);
    class Tagged {
      kind = "x";
    }
    expect(() => canonicalize({ nested: new Tagged() })).toThrow(ToiCanonicalizationError);
  });

  it("rejects a top-level undefined value", () => {
    expect(() => canonicalize(undefined)).toThrow(ToiCanonicalizationError);
  });
});
