/**
 * Regenerate the signed conformance fixture (`test/fixtures/valid/signed.toi`).
 *
 * Ed25519 (RFC 8032) is deterministic, so signing a fixed document with a fixed
 * seed always yields byte-identical output. The seed below is a NON-SECRET test
 * key (bytes 0x01..0x20) — it exists only so the fixture is reproducible and so
 * other implementations have a known-answer signature to verify against.
 *
 * Run with: npx tsx scripts/make-signed-fixture.ts
 */
import { writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { signToi, verifyToi, serializeToi } from "../src/index.js";
import type { ToiDocument } from "../src/index.js";

const TEST_SEED = Uint8Array.from({ length: 32 }, (_v, i) => i + 1);

const doc: ToiDocument = {
  $toi: "1.0.0",
  $tier: "personal",
  $created: "2026-05-29",
  $id: "6ba7b810-9dad-41d1-80b4-00c04fd430c8",
  $license: "Apache-2.0",
  identity: {
    author: "signed conformance fixture",
  },
  communication: {
    tone: "direct",
    verbosity: "concise",
  },
};

const signed = signToi(doc, TEST_SEED);
if (!verifyToi(signed)) {
  throw new Error("Generated fixture failed self-verification");
}

const here = dirname(fileURLToPath(import.meta.url));
const outPath = resolve(here, "..", "test", "fixtures", "valid", "signed.toi");
writeFileSync(outPath, serializeToi(signed), "utf8");
console.log(`Wrote ${outPath}`);
console.log(`public_key = ${signed.$signature?.public_key}`);
