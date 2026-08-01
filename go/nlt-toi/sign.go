// Ed25519 signing and verification over the RFC 8785 canonical form — mirrors
// packages/toi/src/sign.ts and src/nlt_toi/sign.py exactly.
//
// The signed payload is always `canonicalize(document without $signature)`
// encoded as UTF-8. Because canonicalization is order- and formatting-
// independent, a signature survives reformatting, key reordering, and
// round-tripping through any conformant parser.
package nlt_toi

import (
	"crypto/ed25519"
	"crypto/rand"
	"encoding/base64"
	"fmt"
	"regexp"
)

// ToiKeyPair is an Ed25519 key pair. Keys are raw 32-byte seeds / public points.
type ToiKeyPair struct {
	// PrivateKey is the 32-byte Ed25519 private seed. Keep secret; never write
	// it into a .toi file.
	PrivateKey []byte
	// PublicKey is the 32-byte Ed25519 public key.
	PublicKey []byte
	// PublicKeyBase64Url is the public key as base64url — the form stored in
	// $signature.public_key.
	PublicKeyBase64Url string
}

// SPEC §11.1: signature fields are unpadded base64url — no `=` padding, no
// whitespace.
var unpaddedBase64Url = regexp.MustCompile(`^[A-Za-z0-9_-]+$`)

// GenerateKeyPair generates a fresh Ed25519 key pair.
func GenerateKeyPair() (ToiKeyPair, error) {
	seed := make([]byte, ed25519.SeedSize)
	if _, err := rand.Read(seed); err != nil {
		return ToiKeyPair{}, fmt.Errorf("nlt-toi: generate key pair: %w", err)
	}
	return keyPairFromSeed(seed), nil
}

func keyPairFromSeed(seed []byte) ToiKeyPair {
	priv := ed25519.NewKeyFromSeed(seed)
	pub := priv.Public().(ed25519.PublicKey)
	return ToiKeyPair{
		PrivateKey:         append([]byte(nil), seed...),
		PublicKey:          append([]byte(nil), pub...),
		PublicKeyBase64Url: base64.RawURLEncoding.EncodeToString(pub),
	}
}

// withoutSignature returns a copy of value with the top-level $signature key
// removed.
func withoutSignature(value interface{}) interface{} {
	m, ok := value.(map[string]interface{})
	if !ok {
		return value
	}
	out := make(map[string]interface{}, len(m))
	for k, v := range m {
		if k != "$signature" {
			out[k] = v
		}
	}
	return out
}

// SigningPayload returns the exact bytes that get signed: the canonical form
// with $signature removed.
func SigningPayload(value interface{}) ([]byte, error) {
	return CanonicalizeToBytes(withoutSignature(value))
}

// SignToi signs a document, returning a copy with a populated $signature field.
//
// The input must be a JSON object (a parsed .toi document). The signature is
// computed over the RFC 8785 canonical form of the document with $signature
// removed, so it survives reformatting and key reordering.
func SignToi(value interface{}, privateKey []byte) (interface{}, error) {
	if len(privateKey) != ed25519.SeedSize {
		return nil, fmt.Errorf("nlt-toi: Ed25519 private key must be exactly %d bytes", ed25519.SeedSize)
	}
	out, ok := withoutSignature(value).(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("nlt-toi: a .toi document must be a JSON object")
	}
	payload, err := CanonicalizeToBytes(out)
	if err != nil {
		return nil, err
	}
	priv := ed25519.NewKeyFromSeed(privateKey)
	sig := ed25519.Sign(priv, payload)
	pub := priv.Public().(ed25519.PublicKey)
	out["$signature"] = map[string]interface{}{
		"alg":        "ed25519",
		"public_key": base64.RawURLEncoding.EncodeToString(pub),
		"value":      base64.RawURLEncoding.EncodeToString(sig),
	}
	return out, nil
}

// IsSigned reports whether value carries a $signature envelope (not a validity
// claim).
func IsSigned(value interface{}) bool {
	m, ok := value.(map[string]interface{})
	if !ok {
		return false
	}
	_, ok = m["$signature"].(map[string]interface{})
	return ok
}

// VerifyToi verifies a document's embedded $signature against its canonical
// payload. Fully defensive: returns false for a missing, malformed,
// undecodable, or non-matching signature, and never panics.
func VerifyToi(value interface{}) bool {
	m, ok := value.(map[string]interface{})
	if !ok {
		return false
	}
	raw, ok := m["$signature"].(map[string]interface{})
	if !ok {
		return false
	}
	if raw["alg"] != "ed25519" {
		return false
	}
	publicKeyB64, ok := raw["public_key"].(string)
	if !ok {
		return false
	}
	signatureB64, ok := raw["value"].(string)
	if !ok {
		return false
	}
	// SPEC §11.1: reject padded / whitespaced encodings instead of silently
	// normalizing them, so non-conforming envelopes do not verify.
	if !unpaddedBase64Url.MatchString(publicKeyB64) || !unpaddedBase64Url.MatchString(signatureB64) {
		return false
	}
	publicKey, err := base64.RawURLEncoding.DecodeString(publicKeyB64)
	if err != nil {
		return false
	}
	signature, err := base64.RawURLEncoding.DecodeString(signatureB64)
	if err != nil {
		return false
	}
	// base64.RawURLEncoding tolerates non-zero trailing padding bits (golang/go#18446);
	// the TS/Python/Rust references reject them. Require the canonical re-encoding
	// so only canonical encodings verify (SPEC §11.1).
	if base64.RawURLEncoding.EncodeToString(publicKey) != publicKeyB64 ||
		base64.RawURLEncoding.EncodeToString(signature) != signatureB64 {
		return false
	}
	if len(publicKey) != ed25519.PublicKeySize || len(signature) != ed25519.SignatureSize {
		return false
	}
	payload, err := SigningPayload(value)
	if err != nil {
		return false
	}
	return ed25519.Verify(ed25519.PublicKey(publicKey), payload, signature)
}
