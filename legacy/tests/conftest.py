"""Shared test helpers — locate the conformance fixtures copied from the
reference implementation (`@neurolift-technologies/toi`)."""
from __future__ import annotations

from pathlib import Path
from typing import List

FIXTURES = Path(__file__).parent / "fixtures"
VALID_DIR = FIXTURES / "valid"
INVALID_DIR = FIXTURES / "invalid"


def valid_files() -> List[Path]:
    return sorted(VALID_DIR.glob("*.toi"))


def invalid_files() -> List[Path]:
    return sorted(INVALID_DIR.glob("*.toi"))
