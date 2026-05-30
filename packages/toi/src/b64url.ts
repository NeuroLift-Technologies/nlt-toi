/**
 * Dependency-free base64url (RFC 4648 §5) codec for binary data.
 *
 * Used to serialize Ed25519 public keys and signatures into the `$signature`
 * envelope. base64url is URL- and filename-safe and emits no padding, keeping
 * `.toi` documents clean and copy-pasteable.
 *
 * Implemented with a bit accumulator and without `Buffer`, `atob`, or `btoa`,
 * so the library is portable across Node, browsers, Deno, and edge runtimes.
 */

const ALPHABET =
  "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";

/** Reverse lookup: ASCII code point -> 6-bit value, or -1 if not in alphabet. */
const LOOKUP: Int8Array = (() => {
  const table = new Int8Array(128).fill(-1);
  for (let i = 0; i < ALPHABET.length; i++) {
    table[ALPHABET.charCodeAt(i)] = i;
  }
  return table;
})();

/** Encode bytes as an unpadded base64url string. */
export function bytesToBase64Url(bytes: Uint8Array): string {
  let out = "";
  let value = 0;
  let bits = 0;
  for (let i = 0; i < bytes.length; i++) {
    value = (value << 8) | bytes[i]!;
    bits += 8;
    while (bits >= 6) {
      bits -= 6;
      out += ALPHABET.charAt((value >>> bits) & 63);
    }
  }
  if (bits > 0) {
    out += ALPHABET.charAt((value << (6 - bits)) & 63);
  }
  return out;
}

/** Decode a base64url string (padding and surrounding whitespace tolerated). */
export function base64UrlToBytes(input: string): Uint8Array {
  const out: number[] = [];
  let value = 0;
  let bits = 0;
  for (let i = 0; i < input.length; i++) {
    const code = input.charCodeAt(i);
    // Skip ASCII whitespace and '=' padding.
    if (code === 0x20 || code === 0x09 || code === 0x0a || code === 0x0d || code === 0x3d) {
      continue;
    }
    const six = code < 128 ? LOOKUP[code]! : -1;
    if (six < 0) {
      throw new Error(`Invalid base64url character at index ${i}`);
    }
    value = (value << 6) | six;
    bits += 6;
    if (bits >= 8) {
      bits -= 8;
      out.push((value >>> bits) & 0xff);
    }
  }
  return Uint8Array.from(out);
}
