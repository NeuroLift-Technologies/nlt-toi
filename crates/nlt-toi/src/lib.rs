//! nlt-toi — Rust port of @neurolift-technologies/toi
//!
//! Reference implementation of the .toi (Terms of Interaction) standard file type.
//! Ported from @neurolift-technologies/toi (TypeScript) and nlt_toi (Python).
//!
//! IMPORTANT: RFC 8785 JCS canonicalization with exact ECMA-262 Number::toString
//! behavior for number serialization. This implementation uses the ryu crate
//! for exact float-to-string conversion matching ECMAScript Number::toString
//! and UTF-16BE code unit ordering for key sorting per RFC 8785 §3.2.3.

use ed25519_dalek::{Signature, Signer, SigningKey, Verifier, VerifyingKey};
use rand_core::RngCore;
use serde::{Deserialize, Serialize};
use serde_json::Value;

/// TOI format version
pub const TOI_FORMAT_VERSION: &str = "1.0.0";
/// TOI file extension
pub const TOI_FILE_EXTENSION: &str = ".toi";
/// TOI media type
pub const TOI_MEDIA_TYPE: &str = "application/toi+json";
/// Reserved prefix for TOI keys
pub const TOI_RESERVED_PREFIX: &str = "$";
/// Reserved keys in TOI documents
pub const TOI_RESERVED_KEYS: &[&str] = &["$schema", "$version", "$signature"];
/// TOI tiers in precedence order (lowest to highest)
pub const TOI_TIERS: &[&str] = &["personal", "community", "project"];

/// Tier precedence order (higher = stronger)
pub const TIER_PRECEDENCE: &[&str] = &["personal", "community", "project"];
/// Tier rank mapping (higher number = higher precedence)
pub fn tier_rank(tier: &str) -> Option<u8> {
    TIER_PRECEDENCE.iter().position(|&t| t == tier).map(|p| p as u8 + 1)
}

/// TOI document structure
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ToiDocument {
    #[serde(rename = "$schema")]
    pub schema: Option<String>,
    #[serde(rename = "$version")]
    pub version: Option<String>,
    pub tier: String,
    pub author: String,
    pub custom: serde_json::Map<String, Value>,
    #[serde(rename = "$signature")]
    pub signature: Option<ToiSignature>,
}

/// TOI signature envelope (SPEC §11) — a detached Ed25519 signature over the
/// RFC 8785 canonical form of the document with `$signature` removed. Fields
/// match `packages/toi/src/schema.ts` (`toiSignatureSchema`): unpadded base64url
/// for both the raw 32-byte public point and the 64-byte signature.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ToiSignature {
    pub alg: String,
    pub public_key: String,
    pub value: String,
}

/// TOI tier type
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ToiTier {
    Personal,
    Community,
    Project,
}

/// RFC 8785 JCS canonicalization error
#[derive(Debug, thiserror::Error)]
pub enum ToiError {
    #[error("JCS canonicalization failed: {0}")]
    Canonicalization(String),
    #[error("JSON serialization failed: {0}")]
    Serialization(#[from] serde_json::Error),
    #[error("Invalid tier: {0}")]
    InvalidTier(String),
    #[error("Invalid .toi document: {0}")]
    InvalidDocument(String),
    #[error("Invalid signature: {0}")]
    InvalidSignature(String),
    #[error("Base64url decoding failed: {0}")]
    Base64Url(String),
    #[error("Invalid Ed25519 key: {0}")]
    InvalidKey(String),
}

/// ECMA-262 §6.1.6.1.20 Number::toString via ryu's shortest digits.
///
/// RFC 8785 §3.2.2.3 mandates this exact serialization so signatures stay
/// byte-for-byte identical with the TypeScript and Python reference ports.
/// ryu alone is not enough (it renders `42.0`, `1e-6`, `1e7`); this implements
/// the ECMAScript decimal/exponent selection rules on top of ryu's shortest
/// round-tripping digits.
pub fn format_number(n: f64) -> String {
    if n.is_nan() {
        return "NaN".to_string();
    }
    if n.is_infinite() {
        return if n.is_sign_positive() { "Infinity" } else { "-Infinity" }.to_string();
    }
    if n == 0.0 {
        return "0".to_string();
    }
    let sign = if n.is_sign_negative() { "-" } else { "" };
    let mut buf = ryu::Buffer::new();
    let raw = buf.format(n.abs());

    // Decompose ryu's output into significant digits + decimal exponent.
    let (mut digits, mut exponent): (String, i32) = if let Some(pos) =
        raw.find('e').or_else(|| raw.find('E'))
    {
        let mantissa = &raw[..pos];
        let exp_e: i32 = raw[pos + 1..].parse().expect("ryu exponent");
        let dp = mantissa
            .split_once('.')
            .map(|(_, f)| f.len() as i32)
            .unwrap_or(0);
        (mantissa.chars().filter(|c| *c != '.').collect(), exp_e - dp)
    } else {
        let (i, f) = raw.split_once('.').unwrap_or((raw, ""));
        let mut d = String::with_capacity(i.len() + f.len());
        d.push_str(i);
        d.push_str(f);
        (d, -(f.len() as i32))
    };

    // Trailing zeros are never significant in ryu output; stripping them keeps
    // n = exponent + k constant while normalizing k to the significant count.
    while digits.ends_with('0') {
        digits.pop();
        exponent += 1;
    }

    let k = digits.len() as i32;
    let n = exponent + k; // position of the decimal point (ECMA-262)
    if k <= n && n <= 21 {
        return format!("{}{}{}", sign, digits, "0".repeat((n - k) as usize));
    }
    if (1..=21).contains(&n) {
        return format!("{}{}.{}", sign, &digits[..n as usize], &digits[n as usize..]);
    }
    if (-5..=0).contains(&n) {
        return format!("{}0.{}{}", sign, "0".repeat((-n) as usize), digits);
    }
    // Exponential form.
    let exp = n - 1;
    let exp_sign = if exp >= 0 { "+" } else { "-" };
    let mantissa = if k == 1 {
        digits
    } else {
        format!("{}.{}", &digits[..1], &digits[1..])
    };
    format!("{}{}e{}{}", sign, mantissa, exp_sign, exp.abs())
}

/// Compare two strings by their UTF-16BE code unit sequences per RFC 8785 §3.2.3
fn utf16be_compare(a: &str, b: &str) -> std::cmp::Ordering {
    let a_units: Vec<u16> = a.encode_utf16().collect();
    let b_units: Vec<u16> = b.encode_utf16().collect();
    a_units.cmp(&b_units)
}

/// Sort object keys by UTF-16BE code unit sequence per RFC 8785 §3.2.3
fn sort_keys_jcs(value: &Value) -> Result<Value, ToiError> {
    match value {
        Value::Object(map) => {
            let mut entries: Vec<(&String, &Value)> = map.iter().collect();
            entries.sort_by(|a, b| utf16be_compare(a.0, b.0));
            let mut out = serde_json::Map::new();
            for (k, v) in entries {
                out.insert(k.clone(), sort_keys_jcs(v)?);
            }
            Ok(Value::Object(out))
        }
        Value::Array(arr) => {
            let mut out = Vec::new();
            for v in arr {
                out.push(sort_keys_jcs(v)?);
            }
            Ok(Value::Array(out))
        }
        other => Ok(other.clone()),
    }
}

/// RFC 8785 JCS canonicalization with exact ECMA-262 number formatting
/// and UTF-16BE key sorting per RFC 8785 §3.2.3
pub fn canonicalize_jcs(value: &Value) -> Result<String, ToiError> {
    let sorted = sort_keys_jcs(value)?;
    let json = serde_json::to_string(&sorted)?;
    // Post-process to fix number formatting using ryu
    Ok(post_process_numbers(&json))
}

/// Post-process a serde_json-serialized string to ECMA-262 number form.
///
/// serde_json emits floats via ryu (`42.0`, `1e-6`) which is not the RFC 8785
/// form. Integer tokens (no `.`/`e`) are already canonical and pass through
/// verbatim so u64/i64 values beyond 2^53 keep exact precision.
fn post_process_numbers(json_str: &str) -> String {
    let mut result = String::new();
    let mut chars = json_str.chars().peekable();
    let mut in_string = false;
    let mut escape_next = false;

    while let Some(c) = chars.next() {
        if in_string {
            result.push(c);
            if escape_next {
                escape_next = false;
            } else if c == '\\' {
                escape_next = true;
            } else if c == '"' {
                in_string = false;
            }
        } else if c.is_ascii_digit() || c == '-' {
            let mut number_buffer = String::new();
            number_buffer.push(c);
            while let Some(&next_c) = chars.peek() {
                if next_c.is_ascii_digit()
                    || next_c == '.'
                    || next_c == 'e'
                    || next_c == 'E'
                    || next_c == '+'
                    || next_c == '-'
                {
                    number_buffer.push(chars.next().unwrap());
                } else {
                    break;
                }
            }
            if number_buffer.contains('.') || number_buffer.contains('e') || number_buffer.contains('E')
            {
                if let Ok(n) = number_buffer.parse::<f64>() {
                    result.push_str(&format_number(n));
                } else {
                    result.push_str(&number_buffer);
                }
            } else {
                result.push_str(&number_buffer);
            }
        } else {
            result.push(c);
            if c == '"' {
                in_string = true;
            }
        }
    }
    result
}

/// Canonicalize to bytes (for signing)
pub fn canonicalize_to_bytes(value: &Value) -> Result<Vec<u8>, ToiError> {
    Ok(canonicalize_jcs(value)?.into_bytes())
}

/// Compute SHA-256 hash of canonical form (for receipt fingerprints)
pub fn content_hash(value: &Value) -> Result<String, ToiError> {
    use sha2::{Digest, Sha256};
    let canonical = canonicalize_jcs(value)?;
    let mut hasher = Sha256::new();
    hasher.update(canonical.as_bytes());
    Ok(format!("{:x}", hasher.finalize()))
}

// ---------------------------------------------------------------------------
// Ed25519 signing (SPEC §11) — mirrors packages/toi/src/sign.ts and
// src/nlt_toi/sign.py exactly. The signed payload is always
// `canonicalize(document without $signature)` as UTF-8.
// ---------------------------------------------------------------------------

const B64URL_ALPHABET: &[u8; 64] =
    b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";

/// An Ed25519 key pair. Keys are raw 32-byte seeds / public points.
#[derive(Clone, PartialEq, Eq)]
pub struct ToiKeyPair {
    /// 32-byte Ed25519 private seed. Keep secret; never write it into a `.toi` file.
    pub private_key: [u8; 32],
    /// 32-byte Ed25519 public key.
    pub public_key: [u8; 32],
    /// The public key as base64url — the form stored in `$signature.public_key`.
    pub public_key_base64url: String,
}

impl std::fmt::Debug for ToiKeyPair {
    /// Redacts the private seed so accidental `{:?}` of a key pair never leaks it.
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("ToiKeyPair")
            .field("private_key", &"[redacted]")
            .field("public_key", &self.public_key)
            .field("public_key_base64url", &self.public_key_base64url)
            .finish()
    }
}

/// Encode bytes as unpadded base64url (RFC 4648 §5) — no `=` padding.
pub fn base64url_encode(bytes: &[u8]) -> String {
    let mut out = String::with_capacity(bytes.len() / 3 * 4 + 4);
    for chunk in bytes.chunks(3) {
        let b0 = chunk[0] as u32;
        let b1 = chunk.get(1).copied().unwrap_or(0) as u32;
        let b2 = chunk.get(2).copied().unwrap_or(0) as u32;
        let n = (b0 << 16) | (b1 << 8) | b2;
        out.push(B64URL_ALPHABET[((n >> 18) & 63) as usize] as char);
        out.push(B64URL_ALPHABET[((n >> 12) & 63) as usize] as char);
        if chunk.len() > 1 {
            out.push(B64URL_ALPHABET[((n >> 6) & 63) as usize] as char);
        }
        if chunk.len() > 2 {
            out.push(B64URL_ALPHABET[(n & 63) as usize] as char);
        }
    }
    out
}

/// Decode unpadded base64url. Rejects non-alphabet characters, a dangling
/// trailing character (length ≡ 1 mod 4), and non-zero trailing padding bits —
/// i.e. only canonical encodings decode, matching the reference `b64url`.
pub fn base64url_decode(s: &str) -> Result<Vec<u8>, ToiError> {
    let mut out = Vec::with_capacity(s.len() * 3 / 4);
    let mut acc: u32 = 0;
    let mut bits: u32 = 0;
    for b in s.bytes() {
        let six = match b {
            b'A'..=b'Z' => b - b'A',
            b'a'..=b'z' => b - b'a' + 26,
            b'0'..=b'9' => b - b'0' + 52,
            b'-' => 62,
            b'_' => 63,
            _ => return Err(ToiError::Base64Url(format!("invalid character in {s:?}"))),
        };
        acc = (acc << 6) | six as u32;
        bits += 6;
        if bits >= 8 {
            bits -= 8;
            out.push(((acc >> bits) & 0xff) as u8);
            acc &= (1u32 << bits) - 1;
        }
    }
    if bits >= 6 {
        return Err(ToiError::Base64Url("dangling base64url character".into()));
    }
    if bits > 0 && (acc & ((1u32 << bits) - 1)) != 0 {
        return Err(ToiError::Base64Url("non-zero trailing padding bits".into()));
    }
    Ok(out)
}

/// Generate a fresh Ed25519 key pair.
pub fn generate_key_pair() -> ToiKeyPair {
    let mut seed = [0u8; 32];
    rand_core::OsRng.fill_bytes(&mut seed);
    let signing = SigningKey::from_bytes(&seed);
    let public_key = signing.verifying_key().to_bytes();
    ToiKeyPair {
        private_key: seed,
        public_key,
        public_key_base64url: base64url_encode(&public_key),
    }
}

/// A copy of `value` with the top-level `$signature` key removed.
fn without_signature(value: &Value) -> Value {
    match value {
        Value::Object(map) => {
            let mut out = serde_json::Map::new();
            for (k, v) in map {
                if k != "$signature" {
                    out.insert(k.clone(), v.clone());
                }
            }
            Value::Object(out)
        }
        other => other.clone(),
    }
}

/// The exact bytes that get signed: the canonical form with `$signature` removed.
pub fn signing_payload(value: &Value) -> Result<Vec<u8>, ToiError> {
    canonicalize_to_bytes(&without_signature(value))
}

/// Sign a document, returning a copy with a populated `$signature` field.
///
/// The signature is computed over the RFC 8785 canonical form of the document
/// with `$signature` removed, so it survives reformatting and key reordering.
pub fn sign_toi(value: &Value, private_key: &[u8]) -> Result<Value, ToiError> {
    let seed: [u8; 32] = private_key
        .try_into()
        .map_err(|_| ToiError::InvalidKey("Ed25519 private key must be exactly 32 bytes".into()))?;
    let unsigned = without_signature(value);
    if !unsigned.is_object() {
        return Err(ToiError::InvalidDocument(
            "a .toi document must be a JSON object".into(),
        ));
    }
    let signing = SigningKey::from_bytes(&seed);
    let payload = canonicalize_to_bytes(&unsigned)?;
    let signature = signing.sign(&payload);
    let public_key = signing.verifying_key().to_bytes();
    let envelope = serde_json::json!({
        "alg": "ed25519",
        "public_key": base64url_encode(&public_key),
        "value": base64url_encode(&signature.to_bytes()),
    });
    let mut out = unsigned;
    if let Value::Object(map) = &mut out {
        map.insert("$signature".to_string(), envelope);
    }
    Ok(out)
}

/// `true` when `value` carries a `$signature` envelope (not a validity claim).
pub fn is_signed(value: &Value) -> bool {
    matches!(value.get("$signature"), Some(Value::Object(_)))
}

/// SPEC §11.1: signature fields are unpadded base64url — no `=` padding, no whitespace.
fn is_unpadded_base64url(s: &str) -> bool {
    !s.is_empty() && s.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_')
}

/// Verify a document's embedded `$signature` against its canonical payload.
///
/// Fully defensive: returns `false` for a missing, malformed, undecodable, or
/// non-matching signature, and never throws.
pub fn verify_toi(value: &Value) -> bool {
    let raw = match value.get("$signature") {
        Some(Value::Object(m)) => m,
        _ => return false,
    };
    if raw.get("alg").and_then(Value::as_str) != Some("ed25519") {
        return false;
    }
    let public_key_b64 = match raw.get("public_key").and_then(Value::as_str) {
        Some(s) => s,
        None => return false,
    };
    let value_b64 = match raw.get("value").and_then(Value::as_str) {
        Some(s) => s,
        None => return false,
    };
    // SPEC §11.1: reject padded / whitespaced encodings instead of silently
    // normalizing them, so non-conforming envelopes do not verify.
    if !is_unpadded_base64url(public_key_b64) || !is_unpadded_base64url(value_b64) {
        return false;
    }
    let public_key_bytes = match base64url_decode(public_key_b64) {
        Ok(b) => b,
        Err(_) => return false,
    };
    let signature_bytes = match base64url_decode(value_b64) {
        Ok(b) => b,
        Err(_) => return false,
    };
    let Ok(public_key) = <[u8; 32]>::try_from(public_key_bytes.as_slice()) else {
        return false;
    };
    let Ok(signature_bytes) = <[u8; 64]>::try_from(signature_bytes.as_slice()) else {
        return false;
    };
    let payload = match signing_payload(value) {
        Ok(p) => p,
        Err(_) => return false,
    };
    let Ok(verifying_key) = VerifyingKey::from_bytes(&public_key) else {
        return false;
    };
    let signature = Signature::from_bytes(&signature_bytes);
    verifying_key.verify(&payload, &signature).is_ok()
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_format_number_integers() {
        assert_eq!(format_number(42.0), "42");
        assert_eq!(format_number(-42.0), "-42");
        assert_eq!(format_number(0.0), "0");
        assert_eq!(format_number(-0.0), "0");
    }

    #[test]
    fn test_format_number_floats() {
        assert_eq!(format_number(0.1), "0.1");
        assert_eq!(format_number(0.5), "0.5");
        assert_eq!(format_number(1.5), "1.5");
        assert_eq!(format_number(0.000001), "0.000001");
    }

    #[test]
    fn test_format_number_scientific() {
        assert_eq!(format_number(1e-7), "1e-7");
        assert_eq!(format_number(1e7), "10000000");
        assert_eq!(format_number(1e21), "1e+21");
    }

    #[test]
    fn test_format_number_special() {
        assert_eq!(format_number(f64::NAN), "NaN");
        assert_eq!(format_number(f64::INFINITY), "Infinity");
        assert_eq!(format_number(f64::NEG_INFINITY), "-Infinity");
    }

    #[test]
    fn test_jcs_key_sorting_utf16() {
        let value = json!({"b": 1, "a": {"z": 2, "y": 3}});
        let canonical = canonicalize_jcs(&value).unwrap();
        assert_eq!(canonical, r#"{"a":{"y":3,"z":2},"b":1}"#);
    }

    #[test]
    fn test_jcs_unicode_key_sorting() {
        let value = json!({"🎉": 1, "a": 2});
        let canonical = canonicalize_jcs(&value).unwrap();
        assert_eq!(canonical, r#"{"a":2,"🎉":1}"#);
    }

    #[test]
    fn test_number_formatting_preserved() {
        let value = json!({"small": 0.000001, "large": 1000000.0, "int": 42.0});
        let canonical = canonicalize_jcs(&value).unwrap();
        assert!(canonical.contains("0.000001"));
        assert!(canonical.contains("1000000"));
        assert!(canonical.contains("42"));
    }

    #[test]
    fn test_canonicalize_to_bytes() {
        let value = json!({"a": 1, "b": 2});
        let bytes = canonicalize_to_bytes(&value).unwrap();
        let canonical = String::from_utf8(bytes).unwrap();
        assert_eq!(canonical, r#"{"a":1,"b":2}"#);
    }

    #[test]
    fn test_content_hash() {
        let value = json!({"test": "data"});
        let hash = content_hash(&value).unwrap();
        assert_eq!(hash.len(), 64);
    }

    /// Cross-runtime parity vectors — byte-for-byte identical to the assertions
    /// in packages/toi/test/canonicalize.test.ts and tests/test_canonicalize.py.
    /// Green here means the Rust port signs/verifies identically to the TS and
    /// Python references (the Phase 0 conformance gate).
    mod cross_runtime_parity {
        use super::*;
        use serde_json::json;

        fn canon(v: &Value) -> String {
            canonicalize_jcs(v).unwrap()
        }

        #[test]
        fn recursive_utf16_key_sorting() {
            let value = json!({"b": 1, "a": [{"d": true, "c": null}, "x"], "ä": 2, "A": 3});
            assert_eq!(
                canon(&value),
                r#"{"A":3,"a":[{"c":null,"d":true},"x"],"b":1,"ä":2}"#
            );
        }

        #[test]
        fn array_element_order_preserved() {
            assert_eq!(canon(&json!([3, 1, 2])), "[3,1,2]");
        }

        #[test]
        fn json_literals() {
            let value = json!({"t": true, "f": false, "n": null});
            assert_eq!(canon(&value), r#"{"f":false,"n":null,"t":true}"#);
        }

        #[test]
        fn null_array_elements() {
            assert_eq!(canon(&json!([1, null, 3])), "[1,null,3]");
        }

        #[test]
        fn ecmascript_number_serialization() {
            assert_eq!(canon(&json!(1.5)), "1.5");
            assert_eq!(canon(&json!(-0.0)), "0");
            assert_eq!(canon(&json!(1e21)), "1e+21");
            assert_eq!(canon(&json!(100.0)), "100");
            assert_eq!(canon(&json!(0.000001)), "0.000001");
            assert_eq!(canon(&json!(1e-7)), "1e-7");
            assert_eq!(canon(&json!(1e-6)), "0.000001");
            assert_eq!(canon(&json!(123.456)), "123.456");
            assert_eq!(canon(&json!(1e20)), "100000000000000000000");
            assert_eq!(canon(&json!(-1.5e-8)), "-1.5e-8");
        }

        #[test]
        fn number_in_custom_object() {
            let value = json!({"custom": {"threshold": 0.000001}});
            assert_eq!(canon(&value), r#"{"custom":{"threshold":0.000001}}"#);
        }

        #[test]
        fn string_escaping_per_json() {
            let value = json!("a\"b\\c");
            assert_eq!(canon(&value), r#""a\"b\\c""#);
        }

        #[test]
        fn utf8_bytes_match_text() {
            let text = "{\"ä\":1}";
            let bytes = canonicalize_to_bytes(&json!({"ä": 1})).unwrap();
            assert_eq!(String::from_utf8(bytes.clone()).unwrap(), text);
            // "ä" is one UTF-16 unit but two UTF-8 bytes (7 units -> 8 bytes).
            assert_eq!(bytes.len(), text.len());
        }
    }

    /// Phase 1: Ed25519 sign / verify — mirrors packages/toi/test/sign.test.ts
    /// and tests/test_sign.py, including the committed known-answer fixture.
    mod signing {
        use super::*;
        use serde_json::json;

        fn minimal() -> Value {
            json!({
                "$toi": "1.0.0",
                "$tier": "personal",
                "identity": { "author": "anonymous" }
            })
        }

        /// The committed known-answer fixture (packages/toi/test/fixtures/valid/signed.toi).
        /// Produced by the TypeScript reference — verifying it here is the
        /// cross-implementation proof that a JS-signed document verifies in Rust
        /// byte-for-byte (the Phase 1 gate).
        fn signed_fixture() -> Value {
            json!({
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
            })
        }

        /// Deterministic Ed25519 vector — seed bytes 1..=32. Shared with the Go
        /// port (go/nlt-toi/sign_test.go); byte-parity across Rust and Go for
        /// the same payload + seed proves the two new ports interoperate and
        /// match the TS/Python references.
        const FIXED_SEED: [u8; 32] = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
            25, 26, 27, 28, 29, 30, 31, 32,
        ];
        const EXPECTED_PUBLIC_KEY_B64: &str = "ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmQ";
        const EXPECTED_SIGNATURE_B64: &str =
            "ubQpn9BdJH6yVrX_XWUA2KhoSi3_hBzfD_5z_xISH6PV_UfKvvNfjuq8icQww79NUPlkNVaSGnQKbs6z04QHBg";
        /// Canonical form of the full signed document for the deterministic vector.
        const EXPECTED_SIGNED_CANONICAL: &str = "{\"$signature\":{\"alg\":\"ed25519\",\"public_key\":\"ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmQ\",\"value\":\"ubQpn9BdJH6yVrX_XWUA2KhoSi3_hBzfD_5z_xISH6PV_UfKvvNfjuq8icQww79NUPlkNVaSGnQKbs6z04QHBg\"},\"$tier\":\"personal\",\"$toi\":\"1.0.0\",\"identity\":{\"author\":\"anonymous\"}}";

        #[test]
        fn round_trips_sign_then_verify() {
            let keys = generate_key_pair();
            let signed = sign_toi(&minimal(), &keys.private_key).unwrap();
            assert!(is_signed(&signed));
            assert_eq!(signed["$signature"]["alg"], "ed25519");
            assert!(verify_toi(&signed));
        }

        #[test]
        fn detects_tampering_with_signed_content() {
            let keys = generate_key_pair();
            let mut signed = sign_toi(&minimal(), &keys.private_key).unwrap();
            signed["identity"]["author"] = json!("someone else");
            assert!(!verify_toi(&signed));
        }

        #[test]
        fn is_stable_across_reformatting_and_key_reordering() {
            let keys = generate_key_pair();
            let signed = sign_toi(&minimal(), &keys.private_key).unwrap();
            // Round-trip through the canonical string: reformatting + key
            // reordering cannot change the payload the signature is over.
            let reparsed: Value = serde_json::from_str(&canonicalize_jcs(&signed).unwrap()).unwrap();
            assert!(verify_toi(&reparsed));
        }

        #[test]
        fn signs_over_canonical_form_with_signature_removed() {
            let keys = generate_key_pair();
            let doc = minimal();
            let signed = sign_toi(&doc, &keys.private_key).unwrap();
            assert_eq!(
                String::from_utf8(signing_payload(&signed).unwrap()).unwrap(),
                canonicalize_jcs(&doc).unwrap()
            );
        }

        #[test]
        fn verifies_committed_known_answer_fixture() {
            let signed = signed_fixture();
            assert!(verify_toi(&signed));
            assert_eq!(
                signed["$signature"]["public_key"],
                "ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmQ"
            );
        }

        #[test]
        fn treats_unsigned_documents_as_unverified_not_errors() {
            let doc = minimal();
            assert!(!is_signed(&doc));
            assert!(!verify_toi(&doc));
        }

        #[test]
        fn rejects_a_wrong_public_key() {
            let keys = generate_key_pair();
            let mut signed = sign_toi(&minimal(), &keys.private_key).unwrap();
            let other = generate_key_pair();
            signed["$signature"]["public_key"] = json!(other.public_key_base64url);
            assert!(!verify_toi(&signed));
        }

        #[test]
        fn returns_false_never_throws_for_malformed_base64url() {
            let keys = generate_key_pair();
            let mut signed = sign_toi(&minimal(), &keys.private_key).unwrap();
            signed["$signature"]["value"] = json!("@@@");
            assert!(!verify_toi(&signed));
        }

        #[test]
        fn rejects_padded_or_whitespaced_base64url() {
            let keys = generate_key_pair();
            let signed = sign_toi(&minimal(), &keys.private_key).unwrap();
            let mut padded = signed.clone();
            padded["$signature"]["value"] =
                json!(format!("{}=", signed["$signature"]["value"].as_str().unwrap()));
            let mut spaced = signed.clone();
            spaced["$signature"]["public_key"] = json!(format!(
                " {}",
                signed["$signature"]["public_key"].as_str().unwrap()
            ));
            assert!(!verify_toi(&padded));
            assert!(!verify_toi(&spaced));
        }

        #[test]
        fn rejects_wrong_length_signature_bytes() {
            // A valid base64url string that decodes to the wrong byte count
            // (32 bytes instead of 64) must not verify.
            let keys = generate_key_pair();
            let mut signed = sign_toi(&minimal(), &keys.private_key).unwrap();
            signed["$signature"]["value"] =
                json!(keys.public_key_base64url.clone());
            assert!(!verify_toi(&signed));
        }

        #[test]
        fn rejects_non_canonical_base64url_trailing_bits() {
            // The ...ElmR variant decodes to the same 32 bytes as the canonical
            // ...ElmQ public key but carries non-zero trailing padding bits.
            // SPEC §11.1 requires canonical encodings, so it must NOT verify
            // (matches TS/Python/Go).
            assert!(base64url_decode("ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmR").is_err());
            let keys = generate_key_pair();
            let mut signed = sign_toi(&minimal(), &keys.private_key).unwrap();
            signed["$signature"]["public_key"] =
                json!("ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmR");
            assert!(!verify_toi(&signed));
        }

        #[test]
        fn debug_redacts_private_key() {
            let keys = generate_key_pair();
            let debug = format!("{keys:?}");
            assert!(debug.contains("[redacted]"));
            assert!(!debug.contains(&keys.private_key.iter().map(|b| format!("{b:02x}")).collect::<String>()));
        }

        #[test]
        fn deterministic_vector_matches_reference_bytes() {
            let signed = sign_toi(&minimal(), &FIXED_SEED).unwrap();
            assert_eq!(signed["$signature"]["public_key"], EXPECTED_PUBLIC_KEY_B64);
            assert_eq!(signed["$signature"]["value"], EXPECTED_SIGNATURE_B64);
            assert_eq!(canonicalize_jcs(&signed).unwrap(), EXPECTED_SIGNED_CANONICAL);
            assert!(verify_toi(&signed));
        }
    }
}