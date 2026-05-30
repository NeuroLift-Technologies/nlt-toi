/**
 * Generate the published JSON Schema artifact from the canonical Zod schema.
 *
 * Run with `npm run build:schema`. The output is a *derived* artifact for
 * editor/tooling integration — the Zod schema in `src/schema.ts` remains the
 * normative source of truth.
 */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { z } from "zod";
import { toiSchema } from "../src/schema.js";
import { TOI_FORMAT_VERSION, TOI_MEDIA_TYPE } from "../src/constants.js";

const here = dirname(fileURLToPath(import.meta.url));
const outPath = resolve(here, "..", "schema", `toi-${TOI_FORMAT_VERSION}.schema.json`);

const generated = z.toJSONSchema(toiSchema, { target: "draft-2020-12" });

const artifact = {
  $schema: "https://json-schema.org/draft/2020-12/schema",
  $id: `https://neurolift.tech/schemas/toi-${TOI_FORMAT_VERSION}.schema.json`,
  title: `Terms of Interaction (.toi) v${TOI_FORMAT_VERSION}`,
  description: `Canonical JSON Schema for the .toi standard file type (media type ${TOI_MEDIA_TYPE}). Derived from the @neurolift/toi Zod schema; do not edit by hand.`,
  ...generated,
};

mkdirSync(dirname(outPath), { recursive: true });
writeFileSync(outPath, `${JSON.stringify(artifact, null, 2)}\n`, "utf8");
console.log(`Wrote ${outPath}`);
