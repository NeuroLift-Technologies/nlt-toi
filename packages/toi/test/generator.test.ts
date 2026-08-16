/** Document generation behavior: defaults, partial preferences, error taxonomy. */
import { describe, it, expect } from "vitest";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import {
  TOIDocumentGenerator,
  isToi,
  parseToi,
  ToiValidationError,
} from "../src/index.js";

describe("TOIDocumentGenerator", () => {
  it("fromDefaults fills identity and reserved keys", () => {
    const gen = TOIDocumentGenerator.fromDefaults("alice");
    expect(gen.document.identity.author).toBe("alice");
    expect(gen.document.$tier).toBe("personal");
    expect(gen.document.$toi).toBe("1.0.0");
    expect(gen.document.$id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    expect(isToi(gen.document)).toBe(true);
  });

  it("fromDefaults honors handle/organization/tier", () => {
    const gen = TOIDocumentGenerator.fromDefaults("bob", {
      handle: "@bob",
      organization: "NeuroLift",
      tier: "community",
    });
    expect(gen.document.identity.handle).toBe("@bob");
    expect(gen.document.identity.organization).toBe("NeuroLift");
    expect(gen.document.$tier).toBe("community");
  });

  it("fromDefaults rejects an unknown tier", () => {
    expect(() =>
      TOIDocumentGenerator.fromDefaults("x", { tier: "galaxy" as never }),
    ).toThrow(ToiValidationError);
  });

  it("fromDict merges partial preferences over defaults", () => {
    const gen = TOIDocumentGenerator.fromDict(
      {
        communication: { tone: "friendly" },
        privacy: { retention: "long-term" },
      },
      { author: "bob" },
    );
    expect(gen.document.communication?.tone).toBe("friendly");
    expect(gen.document.privacy?.retention).toBe("long-term");
    // Untouched defaults survive the merge.
    expect(gen.document.privacy?.cross_platform_sharing).toBe("never");
    expect(gen.document.identity.author).toBe("bob");
    expect(isToi(gen.document)).toBe(true);
  });

  it("fromDict falls back to anonymous author", () => {
    const gen = TOIDocumentGenerator.fromDict({ communication: { tone: "friendly" } });
    expect(gen.document.identity.author).toBe("anonymous");
    expect(isToi(gen.document)).toBe(true);
  });

  it("fromDict preserves input tier unless overridden", () => {
    const base = { $toi: "1.0.0", $tier: "community", identity: { author: "alice" } };
    expect(TOIDocumentGenerator.fromDict(base).document.$tier).toBe("community");
    const over = TOIDocumentGenerator.fromDict(base, { tier: "project" });
    expect(over.document.$tier).toBe("project");
  });

  it("fromDict raises a ToiValidationError on an invalid value", () => {
    expect(() =>
      TOIDocumentGenerator.fromDict({ communication: { tone: "gibberish" } }),
    ).toThrow(ToiValidationError);
  });

  it("toJson / parse round-trips", () => {
    const gen = TOIDocumentGenerator.fromDefaults("carol");
    const json = gen.toJson();
    expect(parseToi(json).identity.author).toBe("carol");
  });

  it("toMarkdown includes the author and tier", () => {
    const md = TOIDocumentGenerator.fromDefaults("dave", { tier: "project" }).toMarkdown();
    expect(md).toContain("dave");
    expect(md).toContain("project");
  });

  it("write produces a readable .toi file", () => {
    const dir = mkdtempSync(join(tmpdir(), "toi-gen-"));
    try {
      const path = join(dir, "me.toi");
      TOIDocumentGenerator.fromDefaults("eve").write(path);
      expect(parseToi(readFileSync(path, "utf8")).identity.author).toBe("eve");
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});