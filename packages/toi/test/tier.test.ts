/** Tier precedence resolution (§5). */
import { describe, it, expect } from "vitest";
import { resolveToi, sortByPrecedence, compareTier } from "../src/index.js";
import type { ToiDocument } from "../src/index.js";

const personal: ToiDocument = {
  $toi: "1.0.0",
  $tier: "personal",
  identity: { author: "Josh" },
  communication: { tone: "direct" },
  privacy: { retention: "user-controlled" },
};
const community: ToiDocument = {
  $toi: "1.0.0",
  $tier: "community",
  identity: { author: "Group" },
  communication: { tone: "friendly", verbosity: "detailed" },
};
const project: ToiDocument = {
  $toi: "1.0.0",
  $tier: "project",
  identity: { author: "Repo" },
  communication: { tone: "professional", verbosity: "concise", structure: "linear" },
  agency: { action_confirmation: "always" },
};

describe("tier precedence (§5)", () => {
  it("orders highest precedence first", () => {
    expect(sortByPrecedence([project, personal, community]).map((d) => d.$tier)).toEqual([
      "personal",
      "community",
      "project",
    ]);
  });

  it("ranks personal above project", () => {
    expect(compareTier("personal", "project")).toBeLessThan(0);
    expect(compareTier("project", "personal")).toBeGreaterThan(0);
  });

  it("makes personal terminal while lower tiers fill gaps", () => {
    const eff = resolveToi([project, community, personal]);
    expect(eff.$tier).toBe("personal");
    expect(eff.communication?.tone).toBe("direct"); // personal wins
    expect(eff.communication?.verbosity).toBe("detailed"); // community fills
    expect(eff.communication?.structure).toBe("linear"); // project fills
    expect(eff.agency?.action_confirmation).toBe("always"); // project adds a section
    expect(eff.privacy?.retention).toBe("user-controlled");
  });

  it("does not mutate inputs", () => {
    resolveToi([project, personal]);
    expect(project.communication?.tone).toBe("professional");
    expect(personal.communication?.tone).toBe("direct");
  });

  it("applies platform defaults at lowest precedence", () => {
    const eff = resolveToi([personal], {
      platformDefaults: {
        communication: { tone: "adaptive", verbosity: "concise" },
        agency: { override_authority: "user-final" },
      },
    });
    expect(eff.communication?.tone).toBe("direct"); // personal beats default
    expect(eff.communication?.verbosity).toBe("concise"); // default fills
    expect(eff.agency?.override_authority).toBe("user-final"); // default adds
  });

  it("throws on empty input", () => {
    expect(() => resolveToi([])).toThrow();
  });

  it("drops unknown reserved ($-prefixed) keys from the effective view", () => {
    const eff = resolveToi([{ ...personal, $futureReserved: "leak" } as ToiDocument]) as Record<string, unknown>;
    expect(eff["$futureReserved"]).toBeUndefined();
    expect(eff.$tier).toBe("personal");
    expect(eff.$toi).toBe("1.0.0");
  });
});
