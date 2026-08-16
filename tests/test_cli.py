"""Tests for the ``toi-generator`` CLI entry point (:mod:`nlt_toi.cli`)."""
from __future__ import annotations

import json

import pytest

from nlt_toi.cli import build_document, main, wizard_document


def _write(tmp_path, name, content):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_generate_from_preferences_file(tmp_path, capsys):
    prefs = _write(tmp_path, "prefs.json", json.dumps({"communication": {"tone": "casual"}}))
    out = tmp_path / "me.toi"
    code = main(["--input", str(prefs), "--author", "carol", "--output", str(out)])
    assert code == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["communication"]["tone"] == "casual"
    assert doc["identity"]["author"] == "carol"
    assert doc["$tier"] == "personal"


def test_generate_prints_to_stdout_when_no_output(capsys):
    code = main(["--author", "anon"])
    assert code == 0
    captured = capsys.readouterr()
    doc = json.loads(captured.out)
    assert doc["identity"]["author"] == "anon"


def test_infer_markdown_from_output_suffix(tmp_path):
    out = tmp_path / "me.md"
    code = main(["--author", "carol", "--output", str(out)])
    assert code == 0
    assert out.read_text(encoding="utf-8").startswith("# Terms of Interaction")


def test_force_json_format_overrides_md_suffix(tmp_path):
    out = tmp_path / "me.md"
    code = main(["--author", "carol", "--output", str(out), "--format", "json"])
    assert code == 0
    json.loads(out.read_text(encoding="utf-8"))


def test_validate_accepts_valid_document(tmp_path, capsys):
    valid = _write(tmp_path, "ok.toi", json.dumps({"$toi": "1.0.0", "$tier": "personal", "identity": {"author": "x"}}))
    assert main(["--input", str(valid), "--validate"]) == 0


def test_validate_rejects_invalid_document(tmp_path, capsys):
    bad = _write(tmp_path, "bad.toi", json.dumps({"$toi": "1.0.0", "$tier": "nope", "identity": {"author": "x"}}))
    assert main(["--input", str(bad), "--validate"]) == 1
    assert "not a valid .toi" in capsys.readouterr().err


def test_validate_requires_input(capsys):
    with pytest.raises(SystemExit):
        main(["--validate"])


def test_bad_preferences_json_returns_error(tmp_path, capsys):
    bad = _write(tmp_path, "bad.json", "not json{")
    assert main(["--input", str(bad), "--author", "carol"]) == 1
    assert "not valid JSON" in capsys.readouterr().err


def test_schema_flag_prints_canonical_schema(capsys):
    assert main(["--schema"]) == 0
    schema = json.loads(capsys.readouterr().out)
    assert schema["$id"].endswith("toi-1.0.0.schema.json")


def test_build_document_without_file_uses_defaults():
    gen = build_document(None, author="zoe", tier="personal")
    assert gen.document["identity"]["author"] == "zoe"


def test_tier_preserved_when_input_supplies_tier(tmp_path):
    prefs = _write(
        tmp_path,
        "community.toi",
        json.dumps({"$toi": "1.0.0", "$tier": "community", "identity": {"author": "alice"}}),
    )
    out = tmp_path / "out.toi"
    assert main(["--input", str(prefs), "--output", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["$tier"] == "community"


def test_tier_explicit_override_wins(tmp_path):
    prefs = _write(
        tmp_path,
        "community.toi",
        json.dumps({"$toi": "1.0.0", "$tier": "community", "identity": {"author": "alice"}}),
    )
    out = tmp_path / "out.toi"
    assert main(["--input", str(prefs), "--tier", "project", "--output", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["$tier"] == "project"


def test_tier_defaults_to_personal_without_input():
    gen = build_document(None, author="zoe", tier=None)
    assert gen.document["$tier"] == "personal"


def test_author_falls_back_to_anonymous_on_cli(tmp_path):
    prefs = _write(tmp_path, "prefs.json", json.dumps({"communication": {"tone": "casual"}}))
    out = tmp_path / "me.toi"
    assert main(["--input", str(prefs), "--output", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["identity"]["author"] == "anonymous"


def test_invalid_enum_in_preferences_returns_clean_error(tmp_path, capsys):
    bad = _write(tmp_path, "bad.json", json.dumps({"communication": {"tone": "gibberish"}}))
    assert main(["--input", str(bad)]) == 1
    err = capsys.readouterr().err
    assert "error:" in err
    assert "Traceback" not in err


def test_wizard_honors_numbered_choices():
    # author, then tone="2" (casual), then all-empty -> defaults.
    answers = iter(["zoe", "2"] + [""] * 17)
    gen = wizard_document("", prompt=lambda _prompt: next(answers))
    assert gen.document["identity"]["author"] == "zoe"
    # Option 2 of tone options is "casual".
    assert gen.document["communication"]["tone"] == "casual"


def test_wizard_defaults_to_anonymous():
    answers = iter([""] * 19)
    gen = wizard_document("", prompt=lambda _prompt: next(answers))
    assert gen.document["identity"]["author"] == "anonymous"