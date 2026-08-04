/** Natural-language extraction behavior — confident-only, lossless, deterministic. */
import { describe, it, expect } from "vitest";
import { extractToi } from "../src/index.js";

function docOf(input: string, options?: Parameters<typeof extractToi>[1]) {
  const result = extractToi(input, options);
  if (!result.success) throw result.error;
  return result.data as Record<string, any>;
}

describe("extractToi", () => {
  it("returns a schema-valid document for a rich declaration", () => {
    const result = extractToi(
      "My name is Sam Smith and my handle is @sams. I work at Acme, my pronouns are they/them. " +
        "I hyperfocus and like step-by-step instructions. Never share my data, don't train on it. " +
        "Only I can start tasks and my word is final. Keep responses concise, use bullet points, no jargon. " +
        "I am neurodivergent.",
    );
    expect(result.success).toBe(true);
    if (!result.success) return;
    const doc = result.data as Record<string, any>;
    expect(doc["$toi"]).toBe("1.0.0");
    expect(doc["$tier"]).toBe("personal");
    expect(doc.identity).toMatchObject({
      author: "Sam Smith",
      handle: "sams",
      organization: "Acme",
      pronouns: "they/them",
    });
    expect(doc.cognitive_profile.attention_model).toBe("hyperfocus-prone");
    expect(doc.cognitive_profile.scaffolding_preference).toBe("step-by-step");
    expect(doc.cognitive_profile.self_described).toMatch(/neurodivergent/);
    expect(doc.privacy).toMatchObject({
      cross_platform_sharing: "never",
      training_use: "prohibited",
    });
    expect(doc.agency).toMatchObject({
      task_initiation: "user-initiated",
      override_authority: "user-final",
    });
    expect(doc.communication).toMatchObject({
      verbosity: "concise",
      structure: "bullet-points",
      jargon_tolerance: "none",
    });
  });

  it("writes an anonymous author with no content sections when nothing matches", () => {
    const doc = docOf("I like coffee and long walks on the beach.");
    expect(doc.identity.author).toBe("anonymous");
    expect(doc.cognitive_profile).toBeUndefined();
    expect(doc.privacy).toBeUndefined();
    expect(doc.agency).toBeUndefined();
    expect(doc.communication).toBeUndefined();
    expect(doc.ethical_pillars).toBeUndefined();
  });

  it("does not treat adjectives after 'I am' as a name (confident-only)", () => {
    expect(docOf("I am happy today.").identity.author).toBe("anonymous");
  });

  it("extracts a name from 'call me'", () => {
    expect(docOf("Call me Rio, please.").identity.author).toBe("Rio");
  });

  it("stops a name capture at a clause boundary", () => {
    expect(docOf("My name is Ada Lovelace and I work at Acme.").identity.author).toBe("Ada Lovelace");
    expect(docOf("My name is Grace Hopper. I am a programmer.").identity.author).toBe("Grace Hopper");
  });

  it("preserves the full original text under custom.freeform_terms", () => {
    const text = "  My name is Sam, keep it concise.  ";
    const doc = docOf(text);
    expect(doc.custom.freeform_terms).toBe("My name is Sam, keep it concise.");
  });

  it("records matched fields under custom.x-extract", () => {
    const doc = docOf("My name is Sam. Never share my data.");
    expect(doc.custom["x-extract"].source).toBe("nlt-toi/extract");
    expect(doc.custom["x-extract"].matched_fields).toContain("privacy.cross_platform_sharing");
  });

  it("sets booleans only when a positive pattern matches", () => {
    const gated = docOf("My name is Sam.");
    expect(gated.cognitive_profile?.thread_support).toBeUndefined();
    expect(gated.cognitive_profile?.hyperfocus_protection).toBeUndefined();
    expect(gated.cognitive_profile?.executive_function_support).toBeUndefined();
    expect(gated.communication?.pattern_highlighting).toBeUndefined();
    expect(gated.communication?.summary_on_return).toBeUndefined();

    const set = docOf(
      "I juggle multiple threads, protect my flow, help me get started, point out patterns, and summarize when I return.",
    );
    expect(set.cognitive_profile.thread_support).toBe(true);
    expect(set.cognitive_profile.hyperfocus_protection).toBe(true);
    expect(set.cognitive_profile.executive_function_support).toBe(true);
    expect(set.communication.pattern_highlighting).toBe(true);
    expect(set.communication.summary_on_return).toBe(true);
  });

  it("supports tier, fallbackAuthor, and metadata options", () => {
    const doc = docOf("Keep it brief.", { tier: "project", fallbackAuthor: "   Rio   ", metadata: false });
    expect(doc["$tier"]).toBe("project");
    expect(doc.identity.author).toBe("Rio");
    expect(doc["$created"]).toBeUndefined();
    expect(doc["$updated"]).toBeUndefined();
    expect(doc["$id"]).toBeUndefined();
  });

  it("adds created/updated/id metadata by default", () => {
    const doc = docOf("My name is Sam.");
    expect(doc["$created"]).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(doc["$updated"]).toBe(doc["$created"]);
    expect(doc["$id"]).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
  });

  it("maps a sample of enum fields", () => {
    const doc = docOf(
      "My name is Sam. I do several things at once. Attention span varies. Energy is steady. " +
        "Session-only retention, aggregate-only sharing, explicit-only training, opt-in analytics. " +
        "User-only overrides, honor deletion immediately. Don't start tasks on your own, no suggestions, " +
        "interrupt only for urgent things, ask before destructive actions. Formal tone, detailed responses, " +
        "hierarchical structure, high jargon tolerance, full-context reconnection. " +
        "Respect my agency and be transparent.",
    );
    expect(doc.cognitive_profile).toMatchObject({
      processing_style: "parallel",
      attention_model: "variable",
      energy_model: "steady",
    });
    expect(doc.privacy).toMatchObject({
      retention: "session-only",
      cross_platform_sharing: "aggregate-only",
      training_use: "explicit-only",
      analytics: "opt-in",
      override_rights: "user-only",
      data_requests: "honored-immediately",
    });
    expect(doc.agency).toMatchObject({
      task_initiation: "user-initiated",
      ai_suggestions: "none",
      interruptibility: "urgent-only",
      action_confirmation: "destructive-only",
    });
    expect(doc.communication).toMatchObject({
      tone: "formal",
      verbosity: "detailed",
      structure: "hierarchical",
      jargon_tolerance: "high",
      thread_reconnection: "full-context",
    });
    expect(doc.ethical_pillars).toContain("user-agency");
    expect(doc.ethical_pillars).toContain("transparency");
  });

  it("keeps the tier within the canonical set", () => {
    for (const tier of ["personal", "community", "project"] as const) {
      expect(extractToi("My name is Sam.", { tier }).success).toBe(true);
    }
  });

  function findField(doc: ReturnType<typeof docOf>, field: string): unknown {
    for (const section of ["identity", "cognitive_profile", "privacy", "agency", "communication"] as const) {
      if (doc[section] && field in doc[section]) return doc[section][field];
    }
    return undefined;
  }

  it.each([
    ["I am context-sensitive.", "tone", "adaptive"],
    ["Very direct, please.", "tone", "direct"],
    ["Keep it to a minimum.", "verbosity", "minimal"],
    ["Give me thorough explanations.", "verbosity", "detailed"],
    ["Focused sessions work best.", "attention_model", "sustained"],
    ["I maintain attention well.", "attention_model", "sustained"],
    ["My energy depends on my energy level.", "energy_model", "variable"],
    ["Let me control when to delete.", "retention", "user-controlled"],
    ["Please anonymize my data.", "cross_platform_sharing", "aggregate-only"],
    ["I approve research uses case-by-case.", "cross_platform_sharing", "research-approved"],
    ["I decide what to do.", "override_authority", "user-final"],
    ["Give me a summary at the end.", "summary_on_return", true],
    ["My identifier is Rio.", "author", "Rio"],
  ] as const)("maps the template phrasing %j", (phrase, field, expected) => {
    expect(findField(docOf(phrase), field)).toBe(expected);
  });

  it("extracts a filled-out personal template", () => {
    const filled = `My TOI Version: 1.0.0
My Identifier: Sam Smith

## Communication Preferences

**Communication Style:** Formal (professional, proper grammar)
**Level of Explanation I Want:** Detailed (thorough explanations)
**How I Like Information Structured:** Bullet Points (lists and organized points)

## How I Process Information

**My Cognitive Load:** Variable (depends on my energy level)
**My Attention Patterns:** Short Bursts (brief, focused interactions)

## Privacy and Data

**Keep My Data For:** This session only (delete when we're done)
**Sharing My Information:** Never share with anyone
**Other Privacy Preferences:** Please anonymize my data

## Working with Others

**When AIs Disagree:** I decide what to do
`;
    const doc = docOf(filled);
    expect(doc.identity.author).toBe("Sam Smith");
    expect(doc.cognitive_profile).toMatchObject({
      attention_model: "short-bursts",
      energy_model: "variable",
    });
    expect(doc.privacy).toMatchObject({
      retention: "session-only",
      cross_platform_sharing: "never",
    });
    expect(doc.agency.override_authority).toBe("user-final");
    expect(doc.communication).toMatchObject({
      tone: "formal",
      verbosity: "detailed",
      structure: "bullet-points",
    });
    expect(doc.custom.freeform_terms).toContain("My Identifier: Sam Smith");
  });

  it("does not capture a clause after 'call me'", () => {
    expect(docOf("Call me Rio and keep it brief.").identity.author).toBe("Rio");
  });

  it("does not set override_authority from bare 'shared'", () => {
    expect(docOf("I shared my screen with you.").agency?.override_authority).toBeUndefined();
  });

  it("does not set energy_model from eating with a spoon", () => {
    expect(docOf("I eat with a spoon.").cognitive_profile?.energy_model).toBeUndefined();
  });

  it("does not set retention from 'delete my data permanently'", () => {
    expect(docOf("Delete my data permanently.").privacy?.retention).toBeUndefined();
  });

  it("does not set tone from 'please direct me to the file'", () => {
    expect(docOf("Please direct me to the file.").communication?.tone).toBeUndefined();
  });

  it("does not set training_use from bare 'permitted'", () => {
    expect(docOf("I am permitted to enter the building.").privacy?.training_use).toBeUndefined();
  });

  it("does not set booleans from negated statements", () => {
    const doc = docOf("Don't use multiple threads, don't summarize when I return.");
    expect(doc.cognitive_profile?.thread_support).toBeUndefined();
    expect(doc.communication?.summary_on_return).toBeUndefined();
  });

  it("preserves original casing in self_described", () => {
    expect(docOf("I am Autistic and I need structure.").cognitive_profile?.self_described).toBe("I am Autistic");
  });
});
