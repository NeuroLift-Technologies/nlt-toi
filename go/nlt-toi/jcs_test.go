package nlt_toi

import (
	"encoding/json"
	"math"
	"strings"
	"testing"
)

func mustParse(t *testing.T, raw string) interface{} {
	t.Helper()
	dec := json.NewDecoder(strings.NewReader(raw))
	dec.UseNumber()
	var v interface{}
	if err := dec.Decode(&v); err != nil {
		t.Fatalf("parse %s: %v", raw, err)
	}
	return v
}

func canon(t *testing.T, raw string) string {
	t.Helper()
	s, err := CanonicalizeJCS(mustParse(t, raw))
	if err != nil {
		t.Fatalf("canonicalize %s: %v", raw, err)
	}
	return s
}

func TestFormatNumberIntegers(t *testing.T) {
	cases := []struct {
		in   float64
		want string
	}{
		{42.0, "42"},
		{-42.0, "-42"},
		{0.0, "0"},
		{-0.0, "0"},
	}
	for _, c := range cases {
		if got := FormatNumber(c.in); got != c.want {
			t.Fatalf("FormatNumber(%v) = %q, want %q", c.in, got, c.want)
		}
	}
}

func TestFormatNumberFloats(t *testing.T) {
	cases := []struct {
		in   float64
		want string
	}{
		{0.1, "0.1"},
		{0.5, "0.5"},
		{1.5, "1.5"},
		{0.000001, "0.000001"},
		{123.456, "123.456"},
		{100.0, "100"},
		{10000000.0, "10000000"},
	}
	for _, c := range cases {
		if got := FormatNumber(c.in); got != c.want {
			t.Fatalf("FormatNumber(%v) = %q, want %q", c.in, got, c.want)
		}
	}
}

func TestFormatNumberScientific(t *testing.T) {
	cases := []struct {
		in   float64
		want string
	}{
		{1e-7, "1e-7"},
		{1e7, "10000000"},
		{1e21, "1e+21"},
		{1e20, "100000000000000000000"},
		{-1.5e-8, "-1.5e-8"},
	}
	for _, c := range cases {
		if got := FormatNumber(c.in); got != c.want {
			t.Fatalf("FormatNumber(%v) = %q, want %q", c.in, got, c.want)
		}
	}
}

func TestFormatNumberSpecial(t *testing.T) {
	cases := []struct {
		in   float64
		want string
	}{
		{math.NaN(), "NaN"},
		{math.Inf(1), "Infinity"},
		{math.Inf(-1), "-Infinity"},
	}
	for _, c := range cases {
		if got := FormatNumber(c.in); got != c.want {
			t.Fatalf("FormatNumber(%v) = %q, want %q", c.in, got, c.want)
		}
	}
}

func TestJCSSortsKeys(t *testing.T) {
	got := canon(t, `{"b": 1, "a": {"z": 2, "y": 3}}`)
	want := `{"a":{"y":3,"z":2},"b":1}`
	if got != want {
		t.Fatalf("got %q, want %q", got, want)
	}
}

func TestJCSUnicodeKeySorting(t *testing.T) {
	got := canon(t, `{"🎉": 1, "a": 2}`)
	want := `{"a":2,"🎉":1}`
	if got != want {
		t.Fatalf("got %q, want %q", got, want)
	}
}

func TestNumberFormattingPreserved(t *testing.T) {
	got := canon(t, `{"small": 0.000001, "large": 1000000.0, "int": 42.0}`)
	for _, want := range []string{"0.000001", "1000000", "42"} {
		if !strings.Contains(got, want) {
			t.Fatalf("canonical %q missing %q", got, want)
		}
	}
}

func TestIntegerPrecisionPreserved(t *testing.T) {
	// Integers beyond 2^53 must pass through verbatim (no float rounding).
	got := canon(t, `{"big": 9007199254740993, "huge": 123456789012345678901234567890}`)
	want := `{"big":9007199254740993,"huge":123456789012345678901234567890}`
	if got != want {
		t.Fatalf("got %q, want %q", got, want)
	}
}

func TestCanonicalizeToBytes(t *testing.T) {
	bytes, err := CanonicalizeToBytes(mustParse(t, `{"a": 1, "b": 2}`))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if string(bytes) != `{"a":1,"b":2}` {
		t.Fatalf("got %q", string(bytes))
	}
}

func TestContentHash(t *testing.T) {
	hash, err := ContentHash(mustParse(t, `{"test": "data"}`))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(hash) != 64 {
		t.Fatalf("expected 64 hex chars, got %d", len(hash))
	}
}

func TestTierRank(t *testing.T) {
	if TierRank("personal") != 1 || TierRank("community") != 2 || TierRank("project") != 3 {
		t.Fatal("tier ranks not in precedence order")
	}
	if TierRank("bogus") != 0 {
		t.Fatal("unknown tier should rank 0")
	}
}

// Cross-runtime parity vectors — byte-for-byte identical to the assertions in
// packages/toi/test/canonicalize.test.ts, tests/test_canonicalize.py, and
// crates/nlt-toi (cross_runtime_parity). Green here means the Go port
// canonicalizes identically to the TS, Python, and Rust references (the
// Phase 0 conformance gate).
func TestParityRecursiveUTF16KeySorting(t *testing.T) {
	got := canon(t, `{"b": 1, "a": [{"d": true, "c": null}, "x"], "ä": 2, "A": 3}`)
	want := `{"A":3,"a":[{"c":null,"d":true},"x"],"b":1,"ä":2}`
	if got != want {
		t.Fatalf("got %q, want %q", got, want)
	}
}

func TestParityArrayElementOrderPreserved(t *testing.T) {
	if got := canon(t, `[3, 1, 2]`); got != `[3,1,2]` {
		t.Fatalf("got %q", got)
	}
}

func TestParityJSONLiterals(t *testing.T) {
	got := canon(t, `{"t": true, "f": false, "n": null}`)
	if got != `{"f":false,"n":null,"t":true}` {
		t.Fatalf("got %q", got)
	}
}

func TestParityNullArrayElements(t *testing.T) {
	if got := canon(t, `[1, null, 3]`); got != `[1,null,3]` {
		t.Fatalf("got %q", got)
	}
}

func TestParityECMAScriptNumberSerialization(t *testing.T) {
	cases := map[string]string{
		"1.5":      "1.5",
		"-0.0":     "0",
		"1e21":     "1e+21",
		"100.0":    "100",
		"0.000001": "0.000001",
		"1e-7":     "1e-7",
		"1e-6":     "0.000001",
		"123.456":  "123.456",
		"1e20":     "100000000000000000000",
		"-1.5e-8":  "-1.5e-8",
	}
	for in, want := range cases {
		if got := canon(t, in); got != want {
			t.Fatalf("canon(%s) = %q, want %q", in, got, want)
		}
	}
}

func TestParityNumberInCustomObject(t *testing.T) {
	got := canon(t, `{"custom": {"threshold": 0.000001}}`)
	if got != `{"custom":{"threshold":0.000001}}` {
		t.Fatalf("got %q", got)
	}
}

func TestParityStringEscapingPerJSON(t *testing.T) {
	got := canon(t, `"a\"b\\c"`)
	if got != `"a\"b\\c"` {
		t.Fatalf("got %q", got)
	}
}

func TestParityUTF8BytesMatchText(t *testing.T) {
	text := `{"ä":1}`
	bytes, err := CanonicalizeToBytes(mustParse(t, text))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if string(bytes) != text {
		t.Fatalf("got %q, want %q", string(bytes), text)
	}
	if len(bytes) != len(text) {
		t.Fatalf("byte length mismatch: got %d, want %d", len(bytes), len(text))
	}
}
