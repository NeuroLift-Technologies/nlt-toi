//! nlt-toi — Rust port of @neurolift-technologies/toi
//!
//! Reference implementation of the .toi (Terms of Interaction) standard file type.
//! Ported from @neurolift-technologies/toi (TypeScript) and nlt_toi (Python).
//!
//! IMPORTANT: RFC 8785 JCS canonicalization with exact ECMA-262 Number::toString
//! behavior for number serialization. This implementation uses the ryu crate
//! for exact float-to-string conversion matching ECMAScript Number::toString
//! and UTF-16BE code unit ordering for key sorting per RFC 8785 §3.2.3.

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

/// TOI signature envelope
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ToiSignature {
    pub alg: String,
    pub public_key: String,
    pub signature: String,
    pub signed_at: String,
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
    #[error("Invalid signature: {0}")]
    InvalidSignature(String),
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
}