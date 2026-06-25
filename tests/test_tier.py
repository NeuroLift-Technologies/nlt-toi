"""Tier precedence resolution (§9), ported from tier.test.ts."""
from __future__ import annotations

import pytest

from nlt_toi import ToiTierError, compare_tier, resolve_toi, sort_by_precedence

PERSONAL = {
    "$toi": "1.0.0",
    "$tier": "personal",
    "identity": {"author": "Josh"},
    "communication": {"tone": "direct"},
    "privacy": {"retention": "user-controlled"},
}
COMMUNITY = {
    "$toi": "1.0.0",
    "$tier": "community",
    "identity": {"author": "Group"},
    "communication": {"tone": "friendly", "verbosity": "detailed"},
}
PROJECT = {
    "$toi": "1.0.0",
    "$tier": "project",
    "identity": {"author": "Repo"},
    "communication": {"tone": "professional", "verbosity": "concise", "structure": "linear"},
    "agency": {"action_confirmation": "always"},
}


def test_orders_highest_precedence_first():
    order = [d["$tier"] for d in sort_by_precedence([PROJECT, PERSONAL, COMMUNITY])]
    assert order == ["personal", "community", "project"]


def test_ranks_personal_above_project():
    assert compare_tier("personal", "project") < 0
    assert compare_tier("project", "personal") > 0


def test_personal_terminal_while_lower_tiers_fill_gaps():
    eff = resolve_toi([PROJECT, COMMUNITY, PERSONAL])
    assert eff["$tier"] == "personal"
    assert eff["communication"]["tone"] == "direct"  # personal wins
    assert eff["communication"]["verbosity"] == "detailed"  # community fills
    assert eff["communication"]["structure"] == "linear"  # project fills
    assert eff["agency"]["action_confirmation"] == "always"  # project adds a section
    assert eff["privacy"]["retention"] == "user-controlled"


def test_does_not_mutate_inputs():
    resolve_toi([PROJECT, PERSONAL])
    assert PROJECT["communication"]["tone"] == "professional"
    assert PERSONAL["communication"]["tone"] == "direct"


def test_applies_platform_defaults_at_lowest_precedence():
    eff = resolve_toi(
        [PERSONAL],
        platform_defaults={
            "communication": {"tone": "adaptive", "verbosity": "concise"},
            "agency": {"override_authority": "user-final"},
        },
    )
    assert eff["communication"]["tone"] == "direct"  # personal beats default
    assert eff["communication"]["verbosity"] == "concise"  # default fills
    assert eff["agency"]["override_authority"] == "user-final"  # default adds


def test_throws_on_empty_input():
    with pytest.raises(ToiTierError):
        resolve_toi([])


def test_drops_unknown_reserved_keys_from_effective_view():
    eff = resolve_toi([{**PERSONAL, "$futureReserved": "leak"}])
    assert "$futureReserved" not in eff
    assert eff["$tier"] == "personal"
    assert eff["$toi"] == "1.0.0"
