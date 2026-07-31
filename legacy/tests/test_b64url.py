"""base64url codec: round-trip plus malformed-input rejection (ported from b64url.test.ts)."""
from __future__ import annotations

import pytest

from nlt_toi.b64url import base64url_to_bytes, bytes_to_base64url


def test_round_trips_arbitrary_bytes():
    data = bytes((i * 37) & 0xFF for i in range(64))
    assert base64url_to_bytes(bytes_to_base64url(data)) == data


def test_emits_unpadded_url_safe_output():
    s = bytes_to_base64url(bytes([251, 255, 191]))
    assert not any(c in "+/=" for c in s)


def test_tolerates_surrounding_whitespace():
    s = bytes_to_base64url(bytes([1, 2, 3]))
    assert base64url_to_bytes(f"  {s}\n") == bytes([1, 2, 3])


def test_rejects_invalid_characters():
    with pytest.raises(ValueError):
        base64url_to_bytes("@@@")


def test_rejects_dangling_character():
    with pytest.raises(ValueError):
        base64url_to_bytes("A")
    with pytest.raises(ValueError):
        base64url_to_bytes("AAAAA")


def test_rejects_non_zero_trailing_padding_bits():
    assert base64url_to_bytes("AA") == bytes([0])
    with pytest.raises(ValueError):
        base64url_to_bytes("AB")
