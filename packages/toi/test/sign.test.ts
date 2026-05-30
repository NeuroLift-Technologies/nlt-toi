/** Ed25519 sign / verify behavior, including a committed known-answer fixture. */
import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  parseToi,
  signToi,
  verifyToi,
  generateKeyPair,
  isSigned,
  signingPayload,
  canonicalize,
} from "../src/index.js";

const validDir = fileURLToPath(new URL("./fixtures/valid/", import.meta.url));
const loadValid = (name: string) => parseToi(readFileSync(join(validDir, name), "utf8"));

describe("ed25519 signing", () => {
  it("round-trips sign -> verify", () => {
    const { privateKey } = generateKeyPair();
    const signed = signToi(loadValid("josh-personal.toi"), privateKey);
    expect(isSigned(signed)).toBe(true);
    expect(signed.$signature?.alg).toBe("ed25519");
    expect(verifyToi(signed)).toBe(true);
  });

  it("detects tampering with signed content", () => {
    const { privateKey } = generateKeyPair();
    const signed = signToi(loadValid("minimal.toi"), privateKey);
    const tampered = structuredClone(signed) as Record<string, any>;
    tampered.identity.author = "someone else";
    expect(verifyToi(tampered as never)).toBe(false);
  });

  it("is stable across reformatting and key reordering", () => {
    const { privateKey } = generateKeyPair();
    const signed = signToi(loadValid("full-coverage.toi"), privateKey);
    const shuffled = JSON.parse(
      JSON.stringify({
        identity: signed.identity,
        $signature: signed.$signature,
        communication: signed.communication,
        $tier: signed.$tier,
        $toi: signed.$toi,
        custom: signed.custom,
        privacy: signed.privacy,
        agency: signed.agency,
        cognitive_profile: signed.cognitive_profile,
        ethical_pillars: signed.ethical_pillars,
        $created: signed.$created,
        $updated: signed.$updated,
        $id: signed.$id,
        $license: signed.$license,
      }),
    );
    expect(verifyToi(shuffled)).toBe(true);
  });

  it("signs over the canonical form with $signature removed", () => {
    const { privateKey } = generateKeyPair();
    const doc = loadValid("minimal.toi");
    const signed = signToi(doc, privateKey);
    expect(new TextDecoder().decode(signingPayload(signed))).toBe(canonicalize(doc));
  });

  it("verifies the committed known-answer fixture", () => {
    const signed = loadValid("signed.toi");
    expect(verifyToi(signed)).toBe(true);
    expect(signed.$signature?.public_key).toBe("ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmQ");
  });

  it("treats unsigned documents as unverified, not errors", () => {
    const doc = loadValid("minimal.toi");
    expect(isSigned(doc)).toBe(false);
    expect(verifyToi(doc)).toBe(false);
  });

  it("rejects a wrong public key", () => {
    const { privateKey } = generateKeyPair();
    const signed = signToi(loadValid("minimal.toi"), privateKey);
    const other = generateKeyPair();
    const swapped = { ...signed, $signature: { ...signed.$signature!, public_key: other.publicKeyBase64Url } };
    expect(verifyToi(swapped)).toBe(false);
  });

  it("returns false (never throws) for malformed base64url in the envelope", () => {
    const { privateKey } = generateKeyPair();
    const signed = signToi(loadValid("minimal.toi"), privateKey);
    const malformed = { ...signed, $signature: { ...signed.$signature!, value: "@@@" } };
    expect(() => verifyToi(malformed)).not.toThrow();
    expect(verifyToi(malformed)).toBe(false);
  });
});
