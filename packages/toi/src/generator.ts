/**
 * High-level `.toi` document generation.
 *
 * `TOIDocumentGenerator` is a small authoring helper that produces conforming
 * `.toi` v1.0.0 documents from defaults or from a partial preferences object.
 * It fills the required reserved keys (`$toi`, `$tier`, `identity`), applies
 * privacy-first defaults, validates the result through the canonical schema, and
 * can render a human-readable Markdown summary for review.
 *
 * The generated document is plain data — nothing here evaluates preferences as
 * instructions (SPEC §2). Use {@link parseToi} / `signToi` for downstream
 * parsing and signing.
 */
import { randomUUID } from "node:crypto";
import { writeFileSync } from "node:fs";
import { TOI_FORMAT_VERSION, TOI_TIERS, type ToiTier } from "./constants.js";
import { ToiValidationError } from "./errors.js";
import { parseToi, serializeToi, type SerializeOptions } from "./parse.js";
import type { ToiDocument } from "./types.js";

/**
 * Privacy-first default preferences (CLAUDE.md: default to the most
 * privacy-preserving options; user agency first). Used as the merge base for
 * both {@link TOIDocumentGenerator.fromDefaults} and
 * {@link TOIDocumentGenerator.fromDict}; `identity.author` is filled in by the
 * generator so a bare merge never produces a conforming document.
 */
export const DEFAULT_DOCUMENT: ToiDocument = {
  $toi: TOI_FORMAT_VERSION,
  $tier: "personal",
  identity: { author: "" },
  cognitive_profile: {
    scaffolding_preference: "moderate",
    attention_model: "variable",
    energy_model: "variable",
    thread_support: true,
  },
  privacy: {
    retention: "session-only",
    cross_platform_sharing: "never",
    training_use: "prohibited",
    analytics: "prohibited",
    override_rights: "user-only",
    data_requests: "honored-immediately",
  },
  agency: {
    task_initiation: "user-initiated",
    ai_suggestions: "on-request",
    interruptibility: "urgent-only",
    action_confirmation: "destructive-only",
    override_authority: "user-final",
  },
  communication: {
    tone: "direct",
    verbosity: "concise",
    structure: "bullet-points",
    language: "en",
    jargon_tolerance: "moderate",
    pattern_highlighting: false,
    summary_on_return: true,
    thread_reconnection: "brief-summary",
  },
  ethical_pillars: ["user-agency", "privacy-by-default"],
};

/** Options accepted by {@link TOIDocumentGenerator.fromDefaults}. */
export interface FromDefaultsOptions {
  /** Interaction tier; defaults to `personal`. */
  tier?: ToiTier;
  /** Optional identity handle. */
  handle?: string;
  /** Optional identity organization. */
  organization?: string;
}

/** Options accepted by {@link TOIDocumentGenerator.fromDict}. */
export interface FromDictOptions {
  /** Override `identity.author`; falls back to `anonymous` when absent everywhere. */
  author?: string;
  /** Override `$tier`; preserves an input document's tier when absent. */
  tier?: ToiTier;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function deepMerge(
  base: Record<string, unknown>,
  overlay: Record<string, unknown>,
): Record<string, unknown> {
  const result: Record<string, unknown> = structuredClone(base);
  for (const [key, value] of Object.entries(overlay)) {
    const baseValue = result[key];
    if (isRecord(value) && isRecord(baseValue)) {
      result[key] = deepMerge(baseValue, value);
    } else {
      result[key] = structuredClone(value);
    }
  }
  return result;
}

function assertTier(tier: ToiTier): void {
  if (!TOI_TIERS.includes(tier)) {
    throw new ToiValidationError(
      `tier must be one of ${TOI_TIERS.join(", ")}; got ${String(tier)}`,
      [],
    );
  }
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

/**
 * Author and validate a single `.toi` document.
 *
 * @example
 * ```ts
 * import { TOIDocumentGenerator } from "@neurolift-technologies/toi";
 *
 * const gen = TOIDocumentGenerator.fromDefaults("alice");
 * console.log(gen.toJson());
 *
 * const fromPrefs = TOIDocumentGenerator.fromDict({
 *   communication: { tone: "friendly" },
 * });
 * console.log(fromPrefs.document.identity.author); // "anonymous"
 * ```
 */
export class TOIDocumentGenerator {
  /** The current, validated document. */
  document: ToiDocument;

  /** Wrap an already-validated document without re-authoring defaults. */
  constructor(document: ToiDocument) {
    this.document = document;
  }

  /** Build a privacy-first personal TOI for `author`. */
  static fromDefaults(author: string, options: FromDefaultsOptions = {}): TOIDocumentGenerator {
    const tier = options.tier ?? "personal";
    assertTier(tier);
    const doc = deepMerge(DEFAULT_DOCUMENT as unknown as Record<string, unknown>, { $tier: tier });
    doc.identity = deepMerge(doc.identity as Record<string, unknown>, { author });
    const identity = doc.identity as Record<string, unknown>;
    if (options.handle) identity.handle = options.handle;
    if (options.organization) identity.organization = options.organization;
    doc.$created = todayIso();
    doc.$id = randomUUID();
    delete doc.$signature;
    return new TOIDocumentGenerator(parseToi(doc)).validate();
  }

  /**
   * Build a TOI from a (possibly partial) preferences object.
   *
   * `preferences` may be a full `.toi` document or a partial set of content
   * sections; missing fields fall back to the privacy-first defaults.
   * `author`/`tier` override the document values so callers do not have to build
   * the reserved keys by hand. When no author is supplied anywhere,
   * `identity.author` falls back to `"anonymous"`.
   *
   * A `$signature` present on the input is always stripped: the merged result
   * changes the signed payload, so the returned document must not look signed.
   * Callers that need a signature must re-sign the generated document.
   */
  static fromDict(
    preferences: Record<string, unknown>,
    options: FromDictOptions = {},
  ): TOIDocumentGenerator {
    const doc = deepMerge(DEFAULT_DOCUMENT as unknown as Record<string, unknown>, preferences ?? {});
    const identity = isRecord(doc.identity) ? doc.identity : {};
    doc.identity = identity;
    if (options.author !== undefined) identity.author = options.author;
    if (!identity.author) identity.author = "anonymous";
    if (options.tier !== undefined) {
      assertTier(options.tier);
      doc.$tier = options.tier;
    }
    delete doc.$signature;
    return new TOIDocumentGenerator(parseToi(doc)).validate();
  }

  /** Validate the document against the canonical schema; throws on failure. */
  validate(): this {
    this.document = parseToi(this.document);
    return this;
  }

  /** Return a fresh copy of the document. */
  toDict(): ToiDocument {
    return structuredClone(this.document);
  }

  /** Serialize the document to its on-disk JSON form. */
  toJson(options?: SerializeOptions): string {
    return serializeToi(this.document, options);
  }

  /**
   * Render a human-readable Markdown summary of the document. This is a review
   * aid, not a machine format — the canonical form is `toJson()`/the on-disk
   * `.toi` file.
   */
  toMarkdown(): string {
    const doc = this.document;
    const identity = (doc.identity ?? {}) as Record<string, unknown>;
    const title = String(identity.author ?? doc.$tier ?? "personal");
    const lines: string[] = [`# Terms of Interaction — ${title}`, ""];
    lines.push(`- **Version**: ${doc.$toi} (${doc.$tier} tier)`);
    if (doc.$created) lines.push(`- **Created**: ${doc.$created}`);
    if (identity.handle) lines.push(`- **Handle**: ${String(identity.handle)}`);
    if (identity.organization) lines.push(`- **Organization**: ${String(identity.organization)}`);

    const sections: Array<[string, string]> = [
      ["identity", "Identity"],
      ["cognitive_profile", "Cognitive profile"],
      ["privacy", "Privacy and data"],
      ["agency", "Agency"],
      ["communication", "Communication"],
      ["ethical_pillars", "Ethical pillars"],
    ];
    for (const [key, label] of sections) {
      const value = (doc as Record<string, unknown>)[key];
      if (value === undefined) continue;
      lines.push("", `## ${label}`, "");
      if (Array.isArray(value)) {
        for (const item of value) lines.push(`- ${String(item)}`);
      } else if (isRecord(value)) {
        for (const [field, fieldValue] of Object.entries(value)) {
          if (field === "$schema") continue;
          const rendered =
            typeof fieldValue === "string"
              ? fieldValue.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
              : String(fieldValue);
          lines.push(
            `- **${field.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}**: ${rendered}`,
          );
        }
      } else {
        lines.push(`- ${String(value)}`);
      }
    }

    const custom = (doc as Record<string, unknown>).custom;
    if (isRecord(custom)) {
      lines.push("", "## Custom", "", "```json", JSON.stringify(custom, null, 2), "```");
    }

    lines.push(
      "",
      "---",
      "",
      "_Machine-readable form: JSON following the `.toi` v1.0.0 spec (see `@neurolift-technologies/toi` schema)._",
    );
    return lines.join("\n") + "\n";
  }

  /** Write the JSON form of the document to `path` (`.toi` or `.json`). */
  write(path: string, options?: SerializeOptions): void {
    writeFileSync(path, this.toJson(options), "utf8");
  }
}