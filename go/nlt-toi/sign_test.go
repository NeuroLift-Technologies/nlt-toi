// Ed25519 sign / verify behavior — mirrors packages/toi/test/sign.test.ts and
// tests/test_sign.py, including the committed known-answer fixture. The
// fixture was produced by the TypeScript reference, so verifying it here is the
// cross-implementation proof that a JS-signed document verifies in Go
// byte-for-byte (the Phase 1 gate).
package nlt_toi

import (
	"math"
	"testing"
)

const minimalDoc = `{"$toi":"1.0.0","$tier":"personal","identity":{"author":"anonymous"}}`

// The committed known-answer fixture (packages/toi/test/fixtures/valid/signed.toi).
const signedFixture = `{
  "$toi": "1.0.0",
  "$tier": "personal",
  "$created": "2026-05-29",
  "$id": "6ba7b810-9dad-41d1-80b4-00c04fd430c8",
  "$license": "Apache-2.0",
  "$signature": {
    "alg": "ed25519",
    "public_key": "ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmQ",
    "value": "9_YgHkljt8dPLYBmuvHjcRHlSaxS0DK06qvJDu2NM3s7tsiqL8zAQjtN-yiwlN5PN7nAFkr_Iz1kMUtrubBAAA"
  },
  "identity": { "author": "signed conformance fixture" },
  "communication": { "tone": "direct", "verbosity": "concise" }
}`

// Deterministic Ed25519 vector — seed bytes 1..=32. Shared with the Rust port
// (crates/nlt-toi/src/lib.rs signing module); byte-parity across Rust and Go
// for the same payload + seed proves the two new ports interoperate and match
// the TS/Python references.
var fixedSeed = []byte{
	1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
	25, 26, 27, 28, 29, 30, 31, 32,
}

const (
	expectedPublicKeyB64    = "ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmQ"
	expectedSignatureB64    = "ubQpn9BdJH6yVrX_XWUA2KhoSi3_hBzfD_5z_xISH6PV_UfKvvNfjuq8icQww79NUPlkNVaSGnQKbs6z04QHBg"
	expectedSignedCanonical = `{"$signature":{"alg":"ed25519","public_key":"ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmQ","value":"ubQpn9BdJH6yVrX_XWUA2KhoSi3_hBzfD_5z_xISH6PV_UfKvvNfjuq8icQww79NUPlkNVaSGnQKbs6z04QHBg"},"$tier":"personal","$toi":"1.0.0","identity":{"author":"anonymous"}}`
)

func TestRoundTripsSignThenVerify(t *testing.T) {
	keys, err := GenerateKeyPair()
	if err != nil {
		t.Fatalf("generate key pair: %v", err)
	}
	signed, err := SignToi(mustParse(t, minimalDoc), keys.PrivateKey)
	if err != nil {
		t.Fatalf("sign: %v", err)
	}
	if !IsSigned(signed) {
		t.Fatal("expected isSigned == true")
	}
	env := signed.(map[string]interface{})["$signature"].(map[string]interface{})
	if env["alg"] != "ed25519" {
		t.Fatalf("alg = %v, want ed25519", env["alg"])
	}
	if !VerifyToi(signed) {
		t.Fatal("expected verifyToi == true")
	}
}

func TestDetectsTamperingWithSignedContent(t *testing.T) {
	keys, err := GenerateKeyPair()
	if err != nil {
		t.Fatalf("generate key pair: %v", err)
	}
	signed, err := SignToi(mustParse(t, minimalDoc), keys.PrivateKey)
	if err != nil {
		t.Fatalf("sign: %v", err)
	}
	tampered := signed.(map[string]interface{})
	tampered["identity"].(map[string]interface{})["author"] = "someone else"
	if VerifyToi(tampered) {
		t.Fatal("expected verifyToi == false after tampering")
	}
}

func TestIsStableAcrossReformattingAndKeyReordering(t *testing.T) {
	keys, err := GenerateKeyPair()
	if err != nil {
		t.Fatalf("generate key pair: %v", err)
	}
	signed, err := SignToi(mustParse(t, minimalDoc), keys.PrivateKey)
	if err != nil {
		t.Fatalf("sign: %v", err)
	}
	canonical, err := CanonicalizeJCS(signed)
	if err != nil {
		t.Fatalf("canonicalize: %v", err)
	}
	reparsed := mustParse(t, canonical)
	if !VerifyToi(reparsed) {
		t.Fatal("expected verifyToi == true after round-trip through canonical form")
	}
}

func TestSignsOverCanonicalFormWithSignatureRemoved(t *testing.T) {
	keys, err := GenerateKeyPair()
	if err != nil {
		t.Fatalf("generate key pair: %v", err)
	}
	doc := mustParse(t, minimalDoc)
	signed, err := SignToi(doc, keys.PrivateKey)
	if err != nil {
		t.Fatalf("sign: %v", err)
	}
	payload, err := SigningPayload(signed)
	if err != nil {
		t.Fatalf("signing payload: %v", err)
	}
	canonical, err := CanonicalizeJCS(doc)
	if err != nil {
		t.Fatalf("canonicalize: %v", err)
	}
	if string(payload) != canonical {
		t.Fatalf("payload %q != canonical %q", string(payload), canonical)
	}
}

func TestVerifiesCommittedKnownAnswerFixture(t *testing.T) {
	signed := mustParse(t, signedFixture)
	if !VerifyToi(signed) {
		t.Fatal("expected the JS-produced known-answer fixture to verify")
	}
	env := signed.(map[string]interface{})["$signature"].(map[string]interface{})
	if env["public_key"] != "ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmQ" {
		t.Fatalf("public_key = %v", env["public_key"])
	}
}

func TestTreatsUnsignedDocumentsAsUnverifiedNotErrors(t *testing.T) {
	doc := mustParse(t, minimalDoc)
	if IsSigned(doc) {
		t.Fatal("expected isSigned == false")
	}
	if VerifyToi(doc) {
		t.Fatal("expected verifyToi == false")
	}
}

func TestRejectsAWrongPublicKey(t *testing.T) {
	keys, err := GenerateKeyPair()
	if err != nil {
		t.Fatalf("generate key pair: %v", err)
	}
	signed, err := SignToi(mustParse(t, minimalDoc), keys.PrivateKey)
	if err != nil {
		t.Fatalf("sign: %v", err)
	}
	other, err := GenerateKeyPair()
	if err != nil {
		t.Fatalf("generate key pair: %v", err)
	}
	env := signed.(map[string]interface{})["$signature"].(map[string]interface{})
	env["public_key"] = other.PublicKeyBase64Url
	if VerifyToi(signed) {
		t.Fatal("expected verifyToi == false with a wrong public key")
	}
}

func TestReturnsFalseNeverThrowsForMalformedBase64Url(t *testing.T) {
	keys, err := GenerateKeyPair()
	if err != nil {
		t.Fatalf("generate key pair: %v", err)
	}
	signed, err := SignToi(mustParse(t, minimalDoc), keys.PrivateKey)
	if err != nil {
		t.Fatalf("sign: %v", err)
	}
	env := signed.(map[string]interface{})["$signature"].(map[string]interface{})
	env["value"] = "@@@"
	if VerifyToi(signed) {
		t.Fatal("expected verifyToi == false with malformed base64url")
	}
}

func TestRejectsPaddedOrWhitespacedBase64Url(t *testing.T) {
	keys, err := GenerateKeyPair()
	if err != nil {
		t.Fatalf("generate key pair: %v", err)
	}
	signed, err := SignToi(mustParse(t, minimalDoc), keys.PrivateKey)
	if err != nil {
		t.Fatalf("sign: %v", err)
	}
	env := signed.(map[string]interface{})["$signature"].(map[string]interface{})

	padded := mustParse(t, canonJSON(t, signed))
	paddedEnv := padded.(map[string]interface{})["$signature"].(map[string]interface{})
	paddedEnv["value"] = env["value"].(string) + "="
	if VerifyToi(padded) {
		t.Fatal("expected verifyToi == false with '=' padding")
	}

	spaced := mustParse(t, canonJSON(t, signed))
	spacedEnv := spaced.(map[string]interface{})["$signature"].(map[string]interface{})
	spacedEnv["public_key"] = " " + env["public_key"].(string)
	if VerifyToi(spaced) {
		t.Fatal("expected verifyToi == false with whitespace in the envelope")
	}
}

func TestReturnsFalseWhenDocumentCannotBeCanonicalized(t *testing.T) {
	keys, err := GenerateKeyPair()
	if err != nil {
		t.Fatalf("generate key pair: %v", err)
	}
	signed, err := SignToi(mustParse(t, minimalDoc), keys.PrivateKey)
	if err != nil {
		t.Fatalf("sign: %v", err)
	}
	broken := signed.(map[string]interface{})
	broken["custom"] = map[string]interface{}{"bad": math.Inf(1)}
	if VerifyToi(broken) {
		t.Fatal("expected verifyToi == false when the document cannot be canonicalized")
	}
}

func TestRejectsNonCanonicalBase64UrlTrailingBits(t *testing.T) {
	keys, err := GenerateKeyPair()
	if err != nil {
		t.Fatalf("generate key pair: %v", err)
	}
	signed, err := SignToi(mustParse(t, minimalDoc), keys.PrivateKey)
	if err != nil {
		t.Fatalf("sign: %v", err)
	}
	// The ...ElmR variant decodes to the same 32 bytes as the canonical ...ElmQ
	// public key but carries non-zero trailing padding bits. SPEC §11.1 requires
	// canonical encodings, so it must NOT verify (matches TS/Python/Rust).
	env := signed.(map[string]interface{})["$signature"].(map[string]interface{})
	env["public_key"] = "ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmR"
	if VerifyToi(signed) {
		t.Fatal("expected verifyToi == false for non-canonical base64url trailing bits")
	}
}

func TestDeterministicVectorMatchesReferenceBytes(t *testing.T) {
	signed, err := SignToi(mustParse(t, minimalDoc), fixedSeed)
	if err != nil {
		t.Fatalf("sign: %v", err)
	}
	env := signed.(map[string]interface{})["$signature"].(map[string]interface{})
	if env["public_key"] != expectedPublicKeyB64 {
		t.Fatalf("public_key = %v, want %s", env["public_key"], expectedPublicKeyB64)
	}
	if env["value"] != expectedSignatureB64 {
		t.Fatalf("value = %v, want %s", env["value"], expectedSignatureB64)
	}
	canonical, err := CanonicalizeJCS(signed)
	if err != nil {
		t.Fatalf("canonicalize: %v", err)
	}
	if canonical != expectedSignedCanonical {
		t.Fatalf("canonical = %s\nwant         %s", canonical, expectedSignedCanonical)
	}
	if !VerifyToi(signed) {
		t.Fatal("expected verifyToi == true for the deterministic vector")
	}
}

func canonJSON(t *testing.T, value interface{}) string {
	t.Helper()
	s, err := CanonicalizeJCS(value)
	if err != nil {
		t.Fatalf("canonicalize: %v", err)
	}
	return s
}
