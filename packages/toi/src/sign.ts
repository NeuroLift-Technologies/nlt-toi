/**
 * Ed25519 signing and verification over the RFC 8785 canonical form.
 *
 * The signed payload is always `canonicalize(document without $signature)`
 * encoded as UTF-8. Because canonicalization is order- and formatting-
 * independent, a signature survives reformatting, key reordering, and
 * round-tripping through any conformant parser.
 *
 * Crypto is provided by `@noble/ed25519` (audited, dependency-light). Its
 * synchronous API needs a SHA-512 implementation wired in once at module load.
 */
import * as ed from "@noble/ed25519";
import { sha512 } from "@noble/hashes/sha512";
import { canonicalizeToBytes } from "./canonicalize.js";
import { bytesToBase64Url, base64UrlToBytes } from "./b64url.js";
import { parseToi } from "./parse.js";
import { ToiSignatureError } from "./errors.js";
import type { ToiDocument, ToiSignature } from "./types.js";

// Wire the synchronous SHA-512 that @noble/ed25519 v2 needs for sync sign/verify.
ed.etc.sha512Sync = (...messages: Uint8Array[]): Uint8Array =>
  sha512(ed.etc.concatBytes(...messages));

/** An Ed25519 key pair. Keys are raw 32-byte seeds / public points. */
export interface ToiKeyPair {
  /** 32-byte Ed25519 private seed. Keep secret; never write it into a `.toi` file. */
  privateKey: Uint8Array;
  /** 32-byte Ed25519 public key. */
  publicKey: Uint8Array;
  /** The public key as base64url — the form stored in `$signature.public_key`. */
  publicKeyBase64Url: string;
}

/** Generate a fresh Ed25519 key pair. */
export function generateKeyPair(): ToiKeyPair {
  const privateKey = ed.utils.randomPrivateKey();
  const publicKey = ed.getPublicKey(privateKey);
  return { privateKey, publicKey, publicKeyBase64Url: bytesToBase64Url(publicKey) };
}

/** The exact bytes that get signed: the canonical form with `$signature` removed. */
export function signingPayload(doc: ToiDocument): Uint8Array {
  return canonicalizeToBytes(withoutSignature(doc));
}

/** `true` when `doc` carries a `$signature` envelope (not a validity claim). */
export function isSigned(doc: unknown): boolean {
  return isPlainObject(doc) && isPlainObject((doc as Record<string, unknown>)["$signature"]);
}

/**
 * Sign a document, returning a copy with a populated `$signature` field. The
 * input is validated first, so signing a malformed document throws.
 *
 * @throws {ToiValidationError} if `doc` is not a valid `.toi` document.
 * @throws {ToiSignatureError} if the cryptographic operation fails.
 */
export function signToi(doc: ToiDocument, privateKey: Uint8Array): ToiDocument {
  const validated = parseToi(doc);
  const unsigned = withoutSignature(validated);
  const payload = canonicalizeToBytes(unsigned);
  let publicKey: Uint8Array;
  let signature: Uint8Array;
  try {
    publicKey = ed.getPublicKey(privateKey);
    signature = ed.sign(payload, privateKey);
  } catch (err) {
    throw new ToiSignatureError("Failed to sign .toi document", { cause: err });
  }
  const $signature: ToiSignature = {
    alg: "ed25519",
    public_key: bytesToBase64Url(publicKey),
    value: bytesToBase64Url(signature),
  };
  return { ...unsigned, $signature } as ToiDocument;
}

/**
 * Verify a document's embedded `$signature` against its canonical payload.
 * Returns `false` for a missing, malformed, or non-matching signature.
 *
 * @throws {ToiSignatureError} only if the verification cannot be attempted
 *   (e.g. the encoded public key / value are not valid base64url).
 */
export function verifyToi(doc: ToiDocument): boolean {
  const raw = (doc as Record<string, unknown>)["$signature"];
  if (!isPlainObject(raw)) return false;
  if (raw["alg"] !== "ed25519") return false;
  const publicKeyB64 = raw["public_key"];
  const valueB64 = raw["value"];
  if (typeof publicKeyB64 !== "string" || typeof valueB64 !== "string") return false;

  let publicKey: Uint8Array;
  let signature: Uint8Array;
  try {
    publicKey = base64UrlToBytes(publicKeyB64);
    signature = base64UrlToBytes(valueB64);
  } catch (err) {
    throw new ToiSignatureError("Malformed signature encoding", { cause: err });
  }

  const payload = canonicalizeToBytes(withoutSignature(doc));
  try {
    return ed.verify(signature, payload, publicKey);
  } catch {
    // Wrong-length key/signature bytes are simply not verifiable.
    return false;
  }
}

function withoutSignature(doc: ToiDocument): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  const source = doc as Record<string, unknown>;
  for (const key of Object.keys(source)) {
    if (key !== "$signature") out[key] = source[key];
  }
  return out;
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
