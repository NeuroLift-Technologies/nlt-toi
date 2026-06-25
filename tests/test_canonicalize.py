"""RFC 8785 (JCS) known-answer tests, ported from canonicalize.test.ts.

JS-specific cases (dropping ``undefined`` object properties, ``toJSON``/Date) are
omitted — Python has no ``undefined`` and no Date.toJSON; ``None`` maps to JSON
``null`` and is emitted, not dropped.
"""
from __future__ import annotations

import math

import pytest

from nlt_toi import ToiCanonicalizationError, canonicalize, canonicalize_to_bytes


def test_sorts_object_keys_by_utf16_code_unit_recursively():
    assert canonicalize({"b": 1, "a": [{"d": True, "c": None}, "x"], "ä": 2, "A": 3}) == (
        '{"A":3,"a":[{"c":null,"d":true},"x"],"b":1,"ä":2}'
    )


def test_preserves_array_element_order():
    assert canonicalize([3, 1, 2]) == "[3,1,2]"


def test_serializes_json_literals():
    assert canonicalize({"t": True, "f": False, "n": None}) == '{"f":false,"n":null,"t":true}'


def test_encodes_none_array_elements_as_null():
    assert canonicalize([1, None, 3]) == "[1,null,3]"


def test_rejects_non_finite_numbers():
    with pytest.raises(ToiCanonicalizationError):
        canonicalize({"x": math.inf})
    with pytest.raises(ToiCanonicalizationError):
        canonicalize(-math.inf)
    with pytest.raises(ToiCanonicalizationError):
        canonicalize(math.nan)


def test_matches_ecmascript_number_serialization():
    assert canonicalize(1.5) == "1.5"
    assert canonicalize(-0.0) == "0"
    assert canonicalize(1e21) == "1e+21"
    assert canonicalize(100) == "100"


def test_emits_utf8_bytes():
    text = '{"ä":1}'
    data = canonicalize_to_bytes({"ä": 1})
    assert data.decode("utf-8") == text
    # "ä" is one UTF-16 unit but two UTF-8 bytes.
    assert len(data) == len(text) + 1


def test_escapes_strings_per_json():
    assert canonicalize('a"b\\c') == '"a\\"b\\\\c"'


def test_rejects_non_plain_values():
    with pytest.raises(ToiCanonicalizationError):
        canonicalize({1, 2, 3})  # a set is not JSON

    class Tagged:
        kind = "x"

    with pytest.raises(ToiCanonicalizationError):
        canonicalize({"nested": Tagged()})
