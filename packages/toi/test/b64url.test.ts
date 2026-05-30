/** base64url codec: round-trip plus malformed-input rejection. */
import { describe, it, expect } from "vitest";
import { bytesToBase64Url, base64UrlToBytes } from "../src/b64url.js";

describe("base64url codec", () => {
  it("round-trips arbitrary bytes", () => {
    const bytes = Uint8Array.from({ length: 64 }, (_, i) => (i * 37) & 0xff);
    expect(base64UrlToBytes(bytesToBase64Url(bytes))).toEqual(bytes);
  });

  it("emits unpadded, URL-safe output", () => {
    const s = bytesToBase64Url(Uint8Array.from([251, 255, 191]));
    expect(s).not.toMatch(/[+/=]/);
  });

  it("tolerates surrounding whitespace", () => {
    const s = bytesToBase64Url(Uint8Array.from([1, 2, 3]));
    expect(base64UrlToBytes(`  ${s}\n`)).toEqual(Uint8Array.from([1, 2, 3]));
  });

  it("rejects invalid characters", () => {
    expect(() => base64UrlToBytes("@@@")).toThrow();
  });

  it("rejects a dangling character (length mod 4 === 1)", () => {
    expect(() => base64UrlToBytes("A")).toThrow();
    expect(() => base64UrlToBytes("AAAAA")).toThrow();
  });

  it("rejects non-zero trailing padding bits", () => {
    // [0] canonically encodes to "AA"; "AB" carries non-zero padding bits.
    expect(base64UrlToBytes("AA")).toEqual(Uint8Array.from([0]));
    expect(() => base64UrlToBytes("AB")).toThrow();
  });
});
