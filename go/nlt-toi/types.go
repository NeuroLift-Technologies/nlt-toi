package nlt_toi

import (
	"crypto/sha256"
	"encoding/hex"
)

// TOI format constants mirroring crates/nlt-toi and packages/toi.
const (
	TOIFormatVersion  = "1.0.0"
	TOIFileExtension  = ".toi"
	TOIMediaType      = "application/toi+json"
	TOIReservedPrefix = "$"
)

// TOIReservedKeys lists reserved keys in TOI documents.
var TOIReservedKeys = []string{"$schema", "$version", "$signature"}

// TOITiers lists TOI tiers in precedence order (lowest to highest).
var TOITiers = []string{"personal", "community", "project"}

// TierPrecedence lists tiers in ascending precedence order (higher = stronger).
var TierPrecedence = []string{"personal", "community", "project"}

// TierRank returns the 1-based rank of tier in TierPrecedence (higher number =
// higher precedence), or 0 if the tier is unknown.
func TierRank(tier string) uint8 {
	for i, t := range TierPrecedence {
		if t == tier {
			return uint8(i + 1)
		}
	}
	return 0
}

// ToiTier mirrors ToiTier in crates/nlt-toi.
type ToiTier string

const (
	ToiTierPersonal  ToiTier = "personal"
	ToiTierCommunity ToiTier = "community"
	ToiTierProject   ToiTier = "project"
)

// ToiSignature is the TOI signature envelope.
type ToiSignature struct {
	Alg       string `json:"alg"`
	PublicKey string `json:"public_key"`
	Signature string `json:"signature"`
	SignedAt  string `json:"signed_at"`
}

// ToiDocument mirrors ToiDocument in crates/nlt-toi.
type ToiDocument struct {
	Schema    string                 `json:"$schema,omitempty"`
	Version   string                 `json:"$version,omitempty"`
	Tier      string                 `json:"tier"`
	Author    string                 `json:"author"`
	Custom    map[string]interface{} `json:"custom"`
	Signature *ToiSignature          `json:"$signature,omitempty"`
}

// CanonicalizeToBytes returns the RFC 8785 canonical form of value as bytes
// (for signing).
func CanonicalizeToBytes(value interface{}) ([]byte, error) {
	s, err := CanonicalizeJCS(value)
	if err != nil {
		return nil, err
	}
	return []byte(s), nil
}

// ContentHash returns the SHA-256 hex digest of the canonical form (for OTOI
// receipt fingerprints).
func ContentHash(value interface{}) (string, error) {
	canonical, err := CanonicalizeJCS(value)
	if err != nil {
		return "", err
	}
	sum := sha256.Sum256([]byte(canonical))
	return hex.EncodeToString(sum[:]), nil
}
