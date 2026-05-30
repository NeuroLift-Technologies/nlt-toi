/**
 * Fixture-driven conformance: every file under `fixtures/valid` MUST parse and
 * validate; every file under `fixtures/invalid` MUST be rejected. Valid docs
 * also round-trip (serialize -> parse -> identical canonical form), and any
 * signed valid fixture must verify.
 */
import { describe, it, expect } from "vitest";
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  parseToi,
  safeParseToi,
  serializeToi,
  canonicalize,
  verifyToi,
  isSigned,
  ToiError,
} from "../src/index.js";

const validDir = fileURLToPath(new URL("./fixtures/valid/", import.meta.url));
const invalidDir = fileURLToPath(new URL("./fixtures/invalid/", import.meta.url));

const validFiles = readdirSync(validDir).filter((f) => f.endsWith(".toi"));
const invalidFiles = readdirSync(invalidDir).filter((f) => f.endsWith(".toi"));

const readValid = (file: string) => readFileSync(join(validDir, file), "utf8");

describe("conformance: valid fixtures", () => {
  it("has fixtures to test", () => {
    expect(validFiles.length).toBeGreaterThan(0);
  });

  it.each(validFiles)("accepts %s", (file) => {
    const raw = readValid(file);
    const doc = parseToi(raw);
    expect(doc.$toi).toBe("1.0.0");
    expect(safeParseToi(raw).success).toBe(true);

    // Serialization is canonically idempotent.
    const canon = canonicalize(doc);
    expect(canonicalize(parseToi(serializeToi(doc)))).toBe(canon);
  });

  it("verifies signed valid fixtures", () => {
    const signed = validFiles.filter((f) => isSigned(parseToi(readValid(f))));
    expect(signed.length).toBeGreaterThan(0);
    for (const file of signed) {
      expect(verifyToi(parseToi(readValid(file)))).toBe(true);
    }
  });
});

describe("conformance: invalid fixtures", () => {
  it("has fixtures to test", () => {
    expect(invalidFiles.length).toBeGreaterThan(0);
  });

  it.each(invalidFiles)("rejects %s", (file) => {
    const raw = readFileSync(join(invalidDir, file), "utf8");
    expect(() => parseToi(raw)).toThrow(ToiError);
    expect(safeParseToi(raw).success).toBe(false);
  });
});
