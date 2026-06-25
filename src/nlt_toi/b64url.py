"""base64url (RFC 4648 §5) codec for binary data.

Used to serialize Ed25519 public keys and signatures into the ``$signature``
envelope. Output is unpadded and URL-safe. The decoder is deliberately strict —
it mirrors the reference implementation: surrounding whitespace and ``=`` padding
are tolerated, but a dangling character (length ≡ 1 mod 4) and non-zero trailing
padding bits are rejected as malformed rather than silently truncated.
"""
from __future__ import annotations

import base64

_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
#: Reverse lookup: ASCII code point -> 6-bit value, or -1 if not in the alphabet.
_LOOKUP = [-1] * 128
for _i, _ch in enumerate(_ALPHABET):
    _LOOKUP[ord(_ch)] = _i

# Bytes skipped by the decoder: space, tab, LF, CR, and '=' padding.
_SKIP = frozenset((0x20, 0x09, 0x0A, 0x0D, 0x3D))


def bytes_to_base64url(data: bytes) -> str:
    """Encode bytes as an unpadded base64url string."""
    return base64.urlsafe_b64encode(bytes(data)).rstrip(b"=").decode("ascii")


def base64url_to_bytes(text: str) -> bytes:
    """Decode a base64url string.

    Raises:
        ValueError: on an invalid character, a dangling character, or non-zero
            trailing padding bits.
    """
    out = bytearray()
    value = 0
    bits = 0
    for i, ch in enumerate(text):
        code = ord(ch)
        if code in _SKIP:
            continue
        six = _LOOKUP[code] if code < 128 else -1
        if six < 0:
            raise ValueError(f"Invalid base64url character at index {i}")
        value = (value << 6) | six
        bits += 6
        if bits >= 8:
            bits -= 8
            out.append((value >> bits) & 0xFF)
            value &= (1 << bits) - 1
    # A leftover group of 6 bits is a dangling character that cannot form a byte.
    if bits >= 6:
        raise ValueError("Invalid base64url: dangling characters")
    # Any trailing padding bits left by a partial group MUST be zero.
    if bits > 0 and (value & ((1 << bits) - 1)) != 0:
        raise ValueError("Invalid base64url: non-zero padding bits")
    return bytes(out)
