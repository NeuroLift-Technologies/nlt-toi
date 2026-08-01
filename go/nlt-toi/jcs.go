// Package nlt_toi is the Go port of @neurolift-technologies/toi.
//
// RFC 8785 JCS canonicalization with exact ECMA-262 Number::toString behavior
// for number serialization, matching the TypeScript (packages/toi), Python
// (nlt_toi), and Rust (crates/nlt-toi) ports byte-for-byte so TOI/OTOI
// signatures stay interoperable across all runtimes.
package nlt_toi

import (
	"bytes"
	"encoding/json"
	"fmt"
	"math"
	"sort"
	"strconv"
	"strings"
	"unicode/utf16"
)

// FormatNumber implements ECMA-262 §6.1.6.1.20 Number::toString on top of Go's
// shortest round-tripping digits.
//
// RFC 8785 §3.2.2.3 mandates this exact serialization so signatures stay
// byte-for-byte identical with the TypeScript and Python reference ports.
// Go's strconv 'g' format is not sufficient (it renders 1e-06, 1e+07, etc.);
// this implements the ECMAScript decimal/exponent selection rules on top of
// strconv's shortest digits.
func FormatNumber(n float64) string {
	if math.IsNaN(n) {
		return "NaN"
	}
	if math.IsInf(n, 1) {
		return "Infinity"
	}
	if math.IsInf(n, -1) {
		return "-Infinity"
	}
	if n == 0 {
		return "0"
	}
	sign := ""
	if math.Signbit(n) {
		sign = "-"
	}
	s := strconv.FormatFloat(math.Abs(n), 'e', -1, 64)
	e := strings.IndexByte(s, 'e')
	mantissa := s[:e]
	exp, err := strconv.Atoi(s[e+1:])
	if err != nil {
		panic("nlt-toi: strconv produced an invalid exponent")
	}

	// Decompose strconv's shortest mantissa into significant digits + decimal
	// exponent (value = digits * 10^(exp - f), with k = len(digits)).
	digits := strings.ReplaceAll(mantissa, ".", "")
	k := len(digits)
	f := 0
	if dot := strings.IndexByte(mantissa, '.'); dot >= 0 {
		f = len(mantissa) - dot - 1
	}
	npos := exp + k - f // position of the decimal point (ECMA-262)

	switch {
	case k <= npos && npos <= 21:
		return sign + digits + strings.Repeat("0", npos-k)
	case npos >= 1 && npos <= 21:
		return sign + digits[:npos] + "." + digits[npos:]
	case npos >= -5 && npos <= 0:
		return sign + "0." + strings.Repeat("0", -npos) + digits
	default:
		expOut := npos - 1
		expSign := "+"
		if expOut < 0 {
			expSign = "-"
			expOut = -expOut
		}
		mant := digits
		if k > 1 {
			mant = digits[:1] + "." + digits[1:]
		}
		return sign + mant + "e" + expSign + strconv.Itoa(expOut)
	}
}

// utf16be returns the UTF-16BE code unit sequence of s per RFC 8785 §3.2.3.
func utf16be(s string) []byte {
	units := utf16.Encode([]rune(s))
	b := make([]byte, 2*len(units))
	for i, c := range units {
		b[2*i] = byte(c >> 8)
		b[2*i+1] = byte(c)
	}
	return b
}

func utf16beLess(a, b string) bool {
	return bytes.Compare(utf16be(a), utf16be(b)) < 0
}

// jsonQuote renders s as an ECMAScript JSON.stringify-compatible string token
// (HTML escaping disabled; matches Go's encoding/json otherwise).
func jsonQuote(s string) string {
	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	enc.SetEscapeHTML(false)
	if err := enc.Encode(s); err != nil {
		panic("nlt-toi: string encoding failed")
	}
	return strings.TrimSuffix(buf.String(), "\n")
}

// isFloatNumber reports whether a json.Number needs float formatting (it
// carries a decimal point or exponent) versus integer pass-through.
func isFloatNumber(s string) bool {
	return strings.ContainsAny(s, ".eE")
}

// numberIsZero reports whether an integer number string represents zero
// (e.g. "-0"), which ECMA-262 Number::toString renders as "0".
func numberIsZero(s string) bool {
	return strings.TrimLeft(strings.TrimLeft(s, "-"), "0") == ""
}

func writeJCS(sb *strings.Builder, v interface{}) error {
	switch t := v.(type) {
	case nil:
		sb.WriteString("null")
	case bool:
		if t {
			sb.WriteString("true")
		} else {
			sb.WriteString("false")
		}
	case string:
		sb.WriteString(jsonQuote(t))
	case json.Number:
		s := string(t)
		if isFloatNumber(s) {
			f, err := strconv.ParseFloat(s, 64)
			if err != nil {
				return fmt.Errorf("nlt-toi: invalid number %q: %w", s, err)
			}
			sb.WriteString(FormatNumber(f))
		} else if numberIsZero(s) {
			sb.WriteString("0")
		} else {
			// Integer tokens pass through verbatim so integers beyond 2^53
			// keep exact precision (mirrors the Rust port's behavior).
			sb.WriteString(s)
		}
	case float64:
		sb.WriteString(FormatNumber(t))
	case int:
		sb.WriteString(strconv.FormatInt(int64(t), 10))
	case int8:
		sb.WriteString(strconv.FormatInt(int64(t), 10))
	case int16:
		sb.WriteString(strconv.FormatInt(int64(t), 10))
	case int32:
		sb.WriteString(strconv.FormatInt(int64(t), 10))
	case int64:
		sb.WriteString(strconv.FormatInt(t, 10))
	case uint:
		sb.WriteString(strconv.FormatUint(uint64(t), 10))
	case uint8:
		sb.WriteString(strconv.FormatUint(uint64(t), 10))
	case uint16:
		sb.WriteString(strconv.FormatUint(uint64(t), 10))
	case uint32:
		sb.WriteString(strconv.FormatUint(uint64(t), 10))
	case uint64:
		sb.WriteString(strconv.FormatUint(t, 10))
	case []interface{}:
		sb.WriteByte('[')
		for i, e := range t {
			if i > 0 {
				sb.WriteByte(',')
			}
			if err := writeJCS(sb, e); err != nil {
				return err
			}
		}
		sb.WriteByte(']')
	case map[string]interface{}:
		sb.WriteByte('{')
		keys := make([]string, 0, len(t))
		for k := range t {
			keys = append(keys, k)
		}
		sort.Slice(keys, func(i, j int) bool { return utf16beLess(keys[i], keys[j]) })
		for i, k := range keys {
			if i > 0 {
				sb.WriteByte(',')
			}
			sb.WriteString(jsonQuote(k))
			sb.WriteByte(':')
			if err := writeJCS(sb, t[k]); err != nil {
				return err
			}
		}
		sb.WriteByte('}')
	default:
		return fmt.Errorf("nlt-toi: unsupported type %T", v)
	}
	return nil
}

// CanonicalizeJCS produces the RFC 8785 canonical JSON text for value.
//
// The value is round-tripped through encoding/json with UseNumber so numbers
// are observed as json.Number: integer tokens pass through verbatim (preserving
// precision beyond 2^53) while float tokens are reformatted with FormatNumber.
func CanonicalizeJCS(value interface{}) (string, error) {
	raw, err := json.Marshal(value)
	if err != nil {
		return "", err
	}
	dec := json.NewDecoder(bytes.NewReader(raw))
	dec.UseNumber()
	var normalized interface{}
	if err := dec.Decode(&normalized); err != nil {
		return "", err
	}
	var sb strings.Builder
	if err := writeJCS(&sb, normalized); err != nil {
		return "", err
	}
	return sb.String(), nil
}
