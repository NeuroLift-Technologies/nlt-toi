/**
 * Natural-language extraction for `.toi` documents.
 *
 * Turns freeform user terms — e.g. an agent's custom instructions or an in-chat
 * declaration like "here's my Terms of Interaction" — into a schema-valid
 * `.toi` document by mapping confident phrase matches onto the SPEC §7 fields.
 *
 * Design rules:
 *
 * 1. **Deterministic.** Pure regex/phrase matching. No LLM calls, no provider,
 *    no network — a `.toi` document stays data, never instructions (SPEC §2, §13).
 * 2. **Confident-only.** A field is set only when a strong phrase match exists.
 *    Absence means "no stated preference" (SPEC §7), resolved later against
 *    lower tiers and platform defaults. Weak or unmatched text is never forced
 *    onto a field.
 * 3. **Lossless.** The original text is preserved under `custom.freeform_terms`
 *    and extraction metadata under `custom.x-extract`, the only sanctioned
 *    location for non-schema content (SPEC §7.7).
 *
 * The produced document is passed through `safeParseToi`, so the result is
 * guaranteed to be a conforming document that can be serialized or signed with
 * the rest of this library.
 */
import { randomUUID } from "node:crypto";
import { safeParseToi, type SafeParseResult } from "./parse.js";
import { TOI_FORMAT_VERSION, type ToiTier } from "./constants.js";

/** Options controlling how a `.toi` document is extracted from text. */
export interface ExtractOptions {
  /** Tier for the produced document. Defaults to `personal`. */
  tier?: ToiTier;
  /** Author used when no name can be extracted. Defaults to `anonymous`. */
  fallbackAuthor?: string;
  /** Include `$created`, `$updated`, and `$id` metadata. Defaults to `true`. */
  metadata?: boolean;
}

/** A single phrase→value rule for an enum field. */
type Rule<T> = { pattern: RegExp; value: T };

function matchRules<T>(text: string, rules: readonly Rule<T>[]): T | undefined {
  for (const { pattern, value } of rules) {
    if (pattern.test(text)) return value;
  }
  return undefined;
}

/** Negation tokens that flip a stated preference into its opposite. */
const NEGATION = /\b(?:don'?t|do not|never|without|avoid)\b/i;

/**
 * True only when `pattern` matches AND no negation token precedes the match
 * (within a short window). Keeps boolean fields from being set by negated
 * statements like "don't use multiple threads".
 */
function positive(text: string, pattern: RegExp): boolean {
  const match = pattern.exec(text);
  if (!match) return false;
  const before = text.slice(Math.max(0, match.index - 40), match.index);
  return !NEGATION.test(before);
}

function capture(text: string, pattern: RegExp): string | undefined {
  const match = text.match(pattern);
  return match?.[1]?.trim();
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function newId(): string {
  return randomUUID();
}

// ---------------------------------------------------------------------------
// identity (§7.1)
// ---------------------------------------------------------------------------

const AUTHOR_PATTERNS: ReadonlyArray<RegExp> = [
  /\bmy name is ([A-Z][A-Za-z .'-]+?)(?:\s+(?:and|with|from|who)\s+|[,.;]|\r?\n|$)/i,
  /\bmy identifier\s*(?:is\s+)?:?\s*([A-Z][A-Za-z .'-]+?)(?:[,.;]|\r?\n|$)/i,
  /\bcall me ([A-Z][A-Za-z]+(?:\s[A-Z][A-Za-z]+){0,2})(?:[,.;]|\s+(?:and|please|with|from|who)\b|$)/i,
];

function extractAuthor(text: string): string | undefined {
  for (const pattern of AUTHOR_PATTERNS) {
    const match = text.match(pattern);
    if (match?.[1]) return match[1].replace(/[.,;]+$/, "").trim();
  }
  return undefined;
}

function extractHandle(text: string): string | undefined {
  return (
    capture(text, /\bmy (?:handle|username) is @?([A-Za-z0-9_.-]{2,40})\b/i) ??
    capture(text, /\b(?:handle|username)[: ]@?([A-Za-z0-9_.-]{2,40})\b/i)
  );
}

function extractOrganization(text: string): string | undefined {
  return capture(text, /\b(?:i work (?:at|for)|my organization is|my company is) ([A-Za-z][A-Za-z .'&-]{2,60})/i)?.replace(
    /[.,;]+$/,
    "",
  );
}

function extractPronouns(text: string): string | undefined {
  return capture(text, /\b(?:my )?pronouns? (?:are|[:]) ([a-z]+(?:\/[a-z]+){0,2})\b/i);
}

// ---------------------------------------------------------------------------
// cognitive_profile (§7.2)
// ---------------------------------------------------------------------------

const PROCESSING_STYLE_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\b(?:several|multiple|many) things (?:at once|at the same time)\b|\bparallel (?:thinking|processing|threads?)\b|\bmultitask\b/i, value: "parallel" },
  { pattern: /\bone thing at a time\b|\bsequential\b/i, value: "sequential" },
  { pattern: /\bassociative\b|\bconnect(?:ing)? (?:ideas|concepts|dots)\b/i, value: "associative" },
  { pattern: /\b(?:processing|thinking) (?:style )?varies\b|\bvariable\b/i, value: "variable" },
];

const ATTENTION_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bhyperfocus\b|\bdeep focus\b/i, value: "hyperfocus-prone" },
  { pattern: /\bshort bursts\b|\bquick bursts\b/i, value: "short-bursts" },
  { pattern: /\bsustained (?:attention|focus)\b|\blong stretches\b|\bfocused sessions?\b|\bmaintain(?:ing)? attention\b/i, value: "sustained" },
  { pattern: /\battention (?:span )?varies\b/i, value: "variable" },
];

const SCAFFOLDING_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bstep[- ]by[- ]step\b|\bwalk me through\b/i, value: "step-by-step" },
  { pattern: /\bminimal (?:hand[- ]?holding|scaffolding|structure)\b/i, value: "minimal" },
  { pattern: /\bextensive (?:scaffolding|structure|guidance)\b|\b(?:lots|a lot) of structure\b/i, value: "extensive" },
  { pattern: /\bmoderate (?:scaffolding|structure|guidance)\b|\bsome structure\b/i, value: "moderate" },
];

const ENERGY_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bspoon(?:s)? (?:limited|based|theory)\b|\b(?:limited|low) spoons?\b|\blimited energy\b/i, value: "spoon-limited" },
  { pattern: /\bbursts? of energy\b|\benergy bursts\b/i, value: "burst" },
  { pattern: /\bsteady (?:energy|pace)\b|\benergy (?:is|stays|remains) steady\b/i, value: "steady" },
  { pattern: /\benergy varies\b|\bdepends on (?:my )?energy(?: level)?\b/i, value: "variable" },
];

// ---------------------------------------------------------------------------
// privacy (§7.3)
// ---------------------------------------------------------------------------

const RETENTION_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bsession[- ]only\b|\b(?:don'?t|do not) (?:remember|retain)\b|\bforget (?:it|everything) (?:after|when)\b/i, value: "session-only" },
  { pattern: /\bshort[- ]term\b|\bdelete (?:it|data) (?:soon|after a while)\b/i, value: "short-term" },
  { pattern: /\blong[- ]term\b|\bremember (?:it|data) (?:long[- ]term|over time)\b/i, value: "long-term" },
  { pattern: /\b(?:keep|store|retain).{0,15}permanent(?:ly)?\b|\byou can keep it\b|\bremember everything forever\b|\bnever delete\b/i, value: "permanent" },
  { pattern: /\buser[- ]controlled\b|\byou decide\b|\bask me\b|\blet me control\b/i, value: "user-controlled" },
];

const SHARING_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bnever share\b|\bdon'?t share\b|\bno sharing\b/i, value: "never" },
  { pattern: /\b(?:only share|share (?:only|if)) .*explicit/i, value: "explicit-only" },
  { pattern: /\baggregate[- ]only\b|\banonymized aggregate\b|\banonymous research\b|\banonymize(?:d)? (?:my )?data\b/i, value: "aggregate-only" },
  { pattern: /\bresearch[- ]approved\b|\bshare (?:for|in) research\b|\bapprove research\b|\bresearch uses case[- ]by[- ]case\b/i, value: "research-approved" },
];

const TRAINING_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bnever train\b|\bdon'?t train\b|\bno training\b/i, value: "prohibited" },
  { pattern: /\bask (?:me|first) before (?:training|you train)\b|\bexplicit[- ]only\b/i, value: "explicit-only" },
  { pattern: /\banonymized[- ]only\b|\b(?:train|training) (?:on )?anonymized\b/i, value: "anonymized-only" },
  { pattern: /\b(?:can|may) train\b|\btraining (?:is )?permitted\b/i, value: "permitted" },
];

const ANALYTICS_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bno analytics\b|\bnever track\b|\banalytics (?:is )?prohibited\b/i, value: "prohibited" },
  { pattern: /\banalytics opt[- ]in\b|\bopt[- ]in to analytics\b|\bopt[- ]in analytics\b/i, value: "opt-in" },
  { pattern: /\banonymized analytics\b/i, value: "anonymized-only" },
  { pattern: /\banalytics (?:are|is)? ?(?:ok|allowed|permitted)\b|\bcan track\b/i, value: "permitted" },
];

const OVERRIDE_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\b(?:only )?(?:i|the user) (?:can|may) override\b|\buser[- ]only\b/i, value: "user-only" },
  { pattern: /\bdelegated\b/i, value: "delegated" },
  { pattern: /\badmin(?:istrator)? can override\b|\badmin[- ]allowed\b/i, value: "admin-allowed" },
];

const DATA_REQUEST_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bdelete (?:my data )?(?:immediately|right away|right now)\b|\bhonor(?:ed)? (?:deletion|requests?|data requests?) immediately\b|\bhonor(?:ed)? immediately\b/i, value: "honored-immediately" },
  { pattern: /\bhonor(?:ed)? on request\b|\b(?:delete|remove) (?:it|data) on request\b/i, value: "honored-on-request" },
  { pattern: /\bnot[- ]supported\b|\bcannot? (?:honor|fulfill)\b/i, value: "not-supported" },
];

// ---------------------------------------------------------------------------
// agency (§7.4)
// ---------------------------------------------------------------------------

const TASK_INITIATION_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bdon'?t (?:start|begin) (?:things|anything|tasks)?\s*(?:on your own|without asking)\b|\buser[- ]initiated\b|\bonly i (?:can )?(?:start|initiate|begin)\b/i, value: "user-initiated" },
  { pattern: /\b(?:you|ai) can (?:start|begin|initiate)\b|\bai[- ]may[- ]initiate\b/i, value: "ai-may-initiate" },
  { pattern: /\b(?:you|ai) (?:can|may) suggest\b|\bai[- ]may[- ]suggest\b|\bsuggest (?:next steps|options|things)\b/i, value: "ai-may-suggest" },
];

const SUGGESTION_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bno suggestions\b|\bdon'?t suggest\b/i, value: "none" },
  { pattern: /\b(?:only )?(?:when|if) i ask\b|\bon request\b|\bon[- ]request\b/i, value: "on-request" },
  { pattern: /\bproactive(?:ly)?\b|\bsuggest proactively\b/i, value: "proactive" },
];

const INTERRUPT_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bnever interrupt\b|\bdon'?t interrupt\b|\bno interruptions\b/i, value: "never" },
  { pattern: /\binterrupt.*\burgent\b|\burgent.*\binterrupt\b|\burgent[- ]only\b/i, value: "urgent-only" },
  { pattern: /\binterrupt (?:me )?anytime\b|\banytime.*\binterrupt\b/i, value: "always" },
];

const CONFIRMATION_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bconfirm (?:everything|every (?:action|step))\b|\bask before (?:doing|every|any)\b/i, value: "always" },
  { pattern: /\bdestructive[- ]only\b|\b(?:only )?(?:for )?(?:destructive|irreversible)\b|\bconfirm.*(?:destructive|irreversible)\b/i, value: "destructive-only" },
  { pattern: /\bnever ask\b|\bdon'?t ask (?:me )?(?:for )?confirmation\b/i, value: "never" },
];

const OVERRIDE_AUTHORITY_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bmy word is final\b|\buser[- ]final\b|\b(?:i|the user) (?:have|has) (?:the )?final say\b|\bi decide what to do\b/i, value: "user-final" },
  { pattern: /\bshared (?:authority|decision|control)\b/i, value: "shared" },
  { pattern: /\byou decide\b|\bai[- ]advisory\b|\byour call\b/i, value: "ai-advisory" },
];

// ---------------------------------------------------------------------------
// communication (§7.5)
// ---------------------------------------------------------------------------

const TONE_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bformal\b/i, value: "formal" },
  { pattern: /\bcasual\b/i, value: "casual" },
  { pattern: /\bprofessional\b/i, value: "professional" },
  { pattern: /\bfriendly\b/i, value: "friendly" },
  { pattern: /\bvery direct\b|\bbe direct\b|\bstraight to the point\b/i, value: "direct" },
  { pattern: /\badaptive\b|\bcontext[- ]sensitive\b|\badapt(?:ing)? based on\b/i, value: "adaptive" },
];

const VERBOSITY_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bminimal\b|\bkeep it to a minimum\b/i, value: "minimal" },
  { pattern: /\bconcise\b|\bkeep it brief\b|\bbe brief\b|\bkeep it short\b|\bshort answers\b|\bbriefly\b|\bdon'?t be verbose\b/i, value: "concise" },
  { pattern: /\bdetailed\b|\bgo into detail\b|\bexplain (?:it|things|your reasoning)\b|\bthorough explanations?\b/i, value: "detailed" },
  { pattern: /\bcomprehensive\b|\bcover everything\b/i, value: "comprehensive" },
  { pattern: /\badaptive\b/i, value: "adaptive" },
];

const STRUCTURE_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bhierarchical\b|\buse headings\b|\boutline\b/i, value: "hierarchical" },
  { pattern: /\bvisual\b|\bdiagrams?\b|\btables?\b/i, value: "visual" },
  { pattern: /\bbullet(?:ed)? points?\b|\buse bullets\b|\bmarkdown lists\b/i, value: "bullet-points" },
  { pattern: /\bnarrative\b|\btell it like a story\b/i, value: "narrative" },
  { pattern: /\blinear\b/i, value: "linear" },
];

const LANGUAGE_MAP: Readonly<Record<string, string>> = {
  english: "en",
  spanish: "es",
  french: "fr",
  german: "de",
  japanese: "ja",
  chinese: "zh",
  "mandarin": "zh",
  portuguese: "pt",
  italian: "it",
  dutch: "nl",
  russian: "ru",
  arabic: "ar",
  hindi: "hi",
  korean: "ko",
};

function extractLanguage(text: string): string | undefined {
  const match = capture(text, /\b(?:speak|language|in|prefer)\s+(?:in\s+)?([a-z]+)\b/i);
  if (!match) return undefined;
  return LANGUAGE_MAP[match.toLowerCase()];
}

const JARGON_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bno jargon\b|\b(?:don'?t use|avoid) jargon\b/i, value: "none" },
  { pattern: /\blow jargon\b|\blittle jargon\b|\bminimal jargon\b/i, value: "low" },
  { pattern: /\bmoderate jargon\b|\bsome jargon\b|\bjargon ok\b/i, value: "moderate" },
  { pattern: /\bjargon[- ]?fine\b|\bhigh jargon\b|\btechnical terms? (?:ok|fine|welcome)\b|\bjargon (?:is )?fine\b/i, value: "high" },
];

const THREAD_RECONNECTION_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\bfull[- ]?context\b|\brestore everything\b/i, value: "full-context" },
  { pattern: /\bbrief summary\b|\bremind me briefly\b|\bquick recap\b/i, value: "brief-summary" },
  { pattern: /\bno recap\b|\bdon'?t recap\b/i, value: "none" },
];

// ---------------------------------------------------------------------------
// ethical_pillars (§7.6)
// ---------------------------------------------------------------------------

const PILLAR_RULES: ReadonlyArray<Rule<string>> = [
  { pattern: /\buser[- ]?agency\b|\brespect my agency\b/i, value: "user-agency" },
  { pattern: /\bdata dignity\b|\bdata[- ]?dignity\b/i, value: "data-dignity" },
  { pattern: /\btransparency\b|\bbe transparent\b/i, value: "transparency" },
  { pattern: /\bcognitive integrity\b|\bcognitive[- ]?integrity\b/i, value: "cognitive-integrity" },
  { pattern: /\bnon[- ]?discrimination\b/i, value: "non-discrimination" },
  { pattern: /\bprivacy[- ]by[- ]default\b|\bprivacy by default\b/i, value: "privacy-by-default" },
];

// ---------------------------------------------------------------------------
// document assembly
// ---------------------------------------------------------------------------

function collectCognitiveProfile(text: string, raw: string, matches: string[]): Record<string, unknown> {
  const profile: Record<string, unknown> = {};
  const selfDescribed = capture(raw, /\b(i (?:am|'m) .{0,120}?(?:neurodivergent|adhd|autistic|add|dyslexic|autism|dyslexia)).{0,60}?(?:[.!]|$)/i);
  if (selfDescribed) {
    profile.self_described = selfDescribed.trim();
    matches.push("cognitive_profile.self_described");
  }
  const set = (field: string, value: unknown) => {
    if (value !== undefined) {
      profile[field] = value;
      matches.push(`cognitive_profile.${field}`);
    }
  };
  set("processing_style", matchRules(text, PROCESSING_STYLE_RULES));
  set("attention_model", matchRules(text, ATTENTION_RULES));
  set("scaffolding_preference", matchRules(text, SCAFFOLDING_RULES));
  set("energy_model", matchRules(text, ENERGY_RULES));
  set(
    "thread_support",
    positive(text, /\b(?:several|multiple|many) threads?\b|\bparallel threads?\b|\bjuggle (?:multiple|several)\b/i)
      ? true
      : undefined,
  );
  set(
    "hyperfocus_protection",
    /\b(?:don'?t|do not|never) (?:interrupt|break) (?:me|my focus|my flow|a flow state)\b|\bprotect (?:my )?flow\b|\bhyperfocus protection\b/i.test(text)
      ? true
      : undefined,
  );
  set(
    "executive_function_support",
    positive(text, /\b(?:help me|help) (?:get started|start tasks|stay on task|plan)\b|\bexecutive function support\b/i)
      ? true
      : undefined,
  );
  return profile;
}

function collectPrivacy(text: string, matches: string[]): Record<string, unknown> {
  const privacy: Record<string, unknown> = {};
  const set = (field: string, value: unknown) => {
    if (value !== undefined) {
      privacy[field] = value;
      matches.push(`privacy.${field}`);
    }
  };
  set("retention", matchRules(text, RETENTION_RULES));
  set("cross_platform_sharing", matchRules(text, SHARING_RULES));
  set("training_use", matchRules(text, TRAINING_RULES));
  set("analytics", matchRules(text, ANALYTICS_RULES));
  set("override_rights", matchRules(text, OVERRIDE_RULES));
  set("data_requests", matchRules(text, DATA_REQUEST_RULES));
  return privacy;
}

function collectAgency(text: string, matches: string[]): Record<string, unknown> {
  const agency: Record<string, unknown> = {};
  const set = (field: string, value: unknown) => {
    if (value !== undefined) {
      agency[field] = value;
      matches.push(`agency.${field}`);
    }
  };
  set("task_initiation", matchRules(text, TASK_INITIATION_RULES));
  set("ai_suggestions", matchRules(text, SUGGESTION_RULES));
  set("interruptibility", matchRules(text, INTERRUPT_RULES));
  set("action_confirmation", matchRules(text, CONFIRMATION_RULES));
  set("override_authority", matchRules(text, OVERRIDE_AUTHORITY_RULES));
  return agency;
}

function collectCommunication(text: string, matches: string[]): Record<string, unknown> {
  const communication: Record<string, unknown> = {};
  const set = (field: string, value: unknown) => {
    if (value !== undefined) {
      communication[field] = value;
      matches.push(`communication.${field}`);
    }
  };
  set("tone", matchRules(text, TONE_RULES));
  set("verbosity", matchRules(text, VERBOSITY_RULES));
  set("structure", matchRules(text, STRUCTURE_RULES));
  const language = extractLanguage(text);
  set("language", language);
  set("jargon_tolerance", matchRules(text, JARGON_RULES));
  set(
    "pattern_highlighting",
    positive(text, /\b(?:point out|surface|highlight) (?:patterns|connections|links)\b|\bpattern highlighting\b/i)
      ? true
      : undefined,
  );
  set(
    "summary_on_return",
    positive(
      text,
      /\b(?:summarize|summary) (?:when|whenever) (?:i (?:come|return)|i'?m back)\b|\bsummary on return\b|\b(?:remind me|recap) where we were\b|\bsummary (?:at the end|when we'?re done)\b|\bsummarize at the end\b/i,
    )
      ? true
      : undefined,
  );
  set("thread_reconnection", matchRules(text, THREAD_RECONNECTION_RULES));
  return communication;
}

function collectPillars(text: string, matches: string[]): string[] | undefined {
  const found: string[] = [];
  for (const { pattern, value } of PILLAR_RULES) {
    if (pattern.test(text)) {
      if (!found.includes(value)) found.push(value);
    }
  }
  if (found.length) {
    matches.push("ethical_pillars");
    return found;
  }
  return undefined;
}

/**
 * Extract a schema-valid `.toi` document from freeform natural-language terms.
 *
 * @param input The user's declared terms (e.g. an agent's custom instructions).
 * @param options See {@link ExtractOptions}.
 */
export function extractToi(input: string, options: ExtractOptions = {}): SafeParseResult {
  const text = input.trim();
  const lower = text.toLowerCase();
  const matches: string[] = [];

  const author = extractAuthor(text) ?? (options.fallbackAuthor?.trim() || "anonymous");
  const identity: Record<string, string> = { author };
  const handle = extractHandle(text);
  if (handle) {
    identity.handle = handle;
    matches.push("identity.handle");
  }
  const organization = extractOrganization(text);
  if (organization) {
    identity.organization = organization;
    matches.push("identity.organization");
  }
  const pronouns = extractPronouns(text);
  if (pronouns) {
    identity.pronouns = pronouns;
    matches.push("identity.pronouns");
  }

  const cognitive_profile = collectCognitiveProfile(lower, text, matches);
  const privacy = collectPrivacy(lower, matches);
  const agency = collectAgency(lower, matches);
  const communication = collectCommunication(lower, matches);
  const ethical_pillars = collectPillars(lower, matches);

  const doc: Record<string, unknown> = {
    $toi: TOI_FORMAT_VERSION,
    $tier: options.tier ?? "personal",
    identity,
  };

  if (options.metadata !== false) {
    const stamp = todayIso();
    doc["$created"] = stamp;
    doc["$updated"] = stamp;
    doc["$id"] = newId();
  }

  if (Object.keys(cognitive_profile).length) doc.cognitive_profile = cognitive_profile;
  if (Object.keys(privacy).length) doc.privacy = privacy;
  if (Object.keys(agency).length) doc.agency = agency;
  if (Object.keys(communication).length) doc.communication = communication;
  if (ethical_pillars) doc.ethical_pillars = ethical_pillars;

  doc.custom = {
    freeform_terms: text,
    "x-extract": {
      source: "nlt-toi/extract",
      matched_fields: matches,
    },
  };

  return safeParseToi(doc);
}
