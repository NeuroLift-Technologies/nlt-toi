/**
 * Public TypeScript types, inferred from the canonical schema so they can never
 * drift from validation. Import {@link ToiDocument} as the shape of any parsed
 * `.toi` file.
 */
import type { z } from "zod";
import type { toiSchema, toiSignatureSchema } from "./schema.js";

/** A fully-parsed, schema-valid `.toi` document. */
export type ToiDocument = z.infer<typeof toiSchema>;

/** The detached Ed25519 signature envelope carried in `$signature`. */
export type ToiSignature = z.infer<typeof toiSignatureSchema>;
