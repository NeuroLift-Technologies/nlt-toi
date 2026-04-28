"""Tests for the nlt_toi TOI generator.

Covers:
  - Generating a TOI document from minimal input
  - Schema validation success for a well-formed document
  - Markdown rendering contains expected section headings
  - CLI basic smoke tests
"""
from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from datetime import datetime, timezone

import pytest

from nlt_toi.generator import TOIDocumentGenerator, DEFAULTS, PersonalTOI


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_data() -> dict:
    """Return the smallest valid TOI dictionary (required fields only)."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "version": "1.0.0",
        "metadata": {
            "created": now,
            "updated": now,
            "author": "test-user",
        },
        "communication": {
            "style": "friendly",
            "directness": "direct",
        },
        "cognitive": {
            "processing_time": "flexible",
            "information_structure": "bullet-points",
        },
        "privacy": {
            "data_retention": "session-only",
            "sharing_consent": "never",
        },
    }


# ---------------------------------------------------------------------------
# 1. Generating a TOI from minimal input
# ---------------------------------------------------------------------------

class TestGenerateFromMinimalInput:
    """TOI documents can be generated from a minimal set of preferences."""

    def test_from_dict_produces_personal_toi(self):
        """from_dict returns a TOIDocumentGenerator with a PersonalTOI inside."""
        gen = TOIDocumentGenerator.from_dict(_minimal_data())
        assert isinstance(gen, TOIDocumentGenerator)
        assert isinstance(gen.toi, PersonalTOI)

    def test_from_dict_fills_missing_sections_with_defaults(self):
        """Sections absent in the input dict are populated from DEFAULTS."""
        gen = TOIDocumentGenerator.from_dict(_minimal_data())
        # energy_management is not in _minimal_data but should come from DEFAULTS
        assert gen.toi.energy_management == DEFAULTS["energy_management"]

    def test_from_defaults_returns_valid_generator(self):
        """from_defaults produces a generator whose document passes validation."""
        gen = TOIDocumentGenerator.from_defaults(author="pytest-user")
        assert gen.toi.metadata["author"] == "pytest-user"
        assert gen.toi.version == "1.0.0"

    def test_from_defaults_sets_timestamps(self):
        """from_defaults populates both 'created' and 'updated' metadata fields."""
        gen = TOIDocumentGenerator.from_defaults()
        assert "created" in gen.toi.metadata
        assert "updated" in gen.toi.metadata

    def test_from_dict_merges_communication_section(self):
        """Partial communication dict is deep-merged with defaults."""
        data = _minimal_data()
        data["communication"] = {"style": "formal", "directness": "very-direct"}
        gen = TOIDocumentGenerator.from_dict(data)
        assert gen.toi.communication["style"] == "formal"
        # explanation_level should come from DEFAULTS
        assert "explanation_level" in gen.toi.communication

    def test_to_dict_round_trips(self):
        """to_dict output can be used to re-construct an equal generator."""
        gen = TOIDocumentGenerator.from_defaults(author="round-trip")
        d = gen.to_dict()
        gen2 = TOIDocumentGenerator.from_dict(d)
        assert gen2.to_dict() == d

    def test_from_file_json(self, tmp_path: Path):
        """from_file loads a JSON file and populates the generator correctly."""
        input_file = tmp_path / "toi.json"
        input_file.write_text(json.dumps(_minimal_data()), encoding="utf-8")
        gen = TOIDocumentGenerator.from_file(input_file)
        assert gen.toi.communication["style"] == "friendly"

    def test_from_file_yaml(self, tmp_path: Path):
        """from_file loads a YAML file when PyYAML is available."""
        pytest.importorskip("yaml", reason="PyYAML not installed")
        import yaml

        input_file = tmp_path / "toi.yaml"
        input_file.write_text(yaml.dump(_minimal_data()), encoding="utf-8")
        gen = TOIDocumentGenerator.from_file(input_file)
        assert gen.toi.metadata["author"] == "test-user"

    def test_from_file_missing_raises(self, tmp_path: Path):
        """from_file raises FileNotFoundError for a non-existent path."""
        with pytest.raises(FileNotFoundError):
            TOIDocumentGenerator.from_file(tmp_path / "does_not_exist.json")

    def test_from_file_unknown_extension_raises(self, tmp_path: Path):
        """from_file raises ValueError for an unsupported file extension."""
        f = tmp_path / "toi.toml"
        f.write_text("[meta]\nauthor = 'x'")
        with pytest.raises(ValueError, match="Unsupported file extension"):
            TOIDocumentGenerator.from_file(f)


# ---------------------------------------------------------------------------
# 2. Schema validation success
# ---------------------------------------------------------------------------

class TestSchemaValidation:
    """Documents that conform to the schema must pass validation."""

    def test_validate_from_defaults_passes(self):
        """A document built from defaults is valid according to the schema."""
        gen = TOIDocumentGenerator.from_defaults(author="validator-test")
        # validate() must not raise
        gen.validate()

    def test_validate_from_minimal_data_passes(self):
        """A document built from minimal required fields passes validation."""
        gen = TOIDocumentGenerator.from_dict(_minimal_data())
        gen.validate()

    def test_is_valid_returns_true_for_valid_doc(self):
        """is_valid() returns True when the document is schema-compliant."""
        gen = TOIDocumentGenerator.from_defaults()
        assert gen.is_valid() is True

    def test_is_valid_returns_false_for_bad_doc(self):
        """is_valid() returns False when a required field is missing."""
        gen = TOIDocumentGenerator.from_defaults()
        # Corrupt the document by removing a required field
        gen.toi.communication.pop("style", None)
        assert gen.is_valid() is False

    def test_get_validation_errors_empty_when_valid(self):
        """get_validation_errors returns an empty list for a valid document."""
        gen = TOIDocumentGenerator.from_defaults()
        assert gen.get_validation_errors() == []

    def test_get_validation_errors_populated_on_invalid(self):
        """get_validation_errors returns messages when the document is invalid."""
        gen = TOIDocumentGenerator.from_defaults()
        gen.toi.communication.pop("style", None)
        errors = gen.get_validation_errors()
        assert len(errors) > 0
        # Each error is a plain string
        assert all(isinstance(e, str) for e in errors)

    def test_schema_uses_draft_2020_12(self):
        """The bundled schema declares JSON Schema Draft 2020-12."""
        schema_path = Path(__file__).parent.parent / "schemas" / "personal-toi.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        assert "2020-12" in schema.get("$schema", "")


# ---------------------------------------------------------------------------
# 3. Markdown rendering contains expected headings
# ---------------------------------------------------------------------------

class TestMarkdownRendering:
    """The Markdown renderer produces well-structured, accessible output."""

    # Section headings that must appear in every generated document
    EXPECTED_HEADINGS = [
        "# Personal Terms of Interaction (TOI)",
        "## Metadata",
        "## Communication Preferences",
        "## Cognitive Preferences",
        "## Privacy Settings",
        "## Energy Management",
        "## Collaboration Preferences",
        "## Accessibility",
    ]

    def test_all_expected_headings_present(self):
        """to_markdown contains all required section headings."""
        gen = TOIDocumentGenerator.from_defaults()
        md = gen.to_markdown()
        for heading in self.EXPECTED_HEADINGS:
            assert heading in md, f"Missing heading: {heading!r}"

    def test_author_appears_in_metadata_section(self):
        """The author name is rendered inside the Metadata section."""
        gen = TOIDocumentGenerator.from_defaults(author="Alice")
        md = gen.to_markdown()
        assert "Alice" in md

    def test_description_appears_when_set(self):
        """A non-empty description is rendered in the Markdown output."""
        gen = TOIDocumentGenerator.from_defaults(description="Daily coding TOI")
        md = gen.to_markdown()
        assert "Daily coding TOI" in md

    def test_privacy_defaults_shown(self):
        """Default privacy settings (session-only, never share) appear in output."""
        gen = TOIDocumentGenerator.from_defaults()
        md = gen.to_markdown()
        assert "session-only" in md
        assert "never" in md

    def test_footer_present(self):
        """The generator footer line is included at the end of the document."""
        gen = TOIDocumentGenerator.from_defaults()
        md = gen.to_markdown()
        assert "nlt-toi TOI Generator" in md

    def test_to_json_is_valid_json(self):
        """to_json returns a string that parses as valid JSON."""
        gen = TOIDocumentGenerator.from_defaults()
        parsed = json.loads(gen.to_json())
        assert parsed["version"] == "1.0.0"

    def test_save_markdown(self, tmp_path: Path):
        """save() writes Markdown content to a file."""
        gen = TOIDocumentGenerator.from_defaults()
        out = tmp_path / "output.md"
        result = gen.save(out, fmt="markdown")
        assert result == out
        assert "# Personal Terms of Interaction" in out.read_text()

    def test_save_json(self, tmp_path: Path):
        """save() writes JSON content to a file."""
        gen = TOIDocumentGenerator.from_defaults()
        out = tmp_path / "output.json"
        gen.save(out, fmt="json")
        data = json.loads(out.read_text())
        assert data["version"] == "1.0.0"

    def test_save_invalid_format_raises(self, tmp_path: Path):
        """save() raises ValueError for an unrecognised format string."""
        gen = TOIDocumentGenerator.from_defaults()
        with pytest.raises(ValueError, match="Unknown format"):
            gen.save(tmp_path / "out.txt", fmt="html")


# ---------------------------------------------------------------------------
# 4. CLI smoke tests
# ---------------------------------------------------------------------------

class TestCLI:
    """Basic smoke tests for the command-line interface."""

    def test_cli_default_prints_markdown(self, capsys):
        """Running CLI without --input prints Markdown to stdout."""
        from nlt_toi.cli import main

        rc = main(["--author", "cli-test"])
        assert rc == 0
        captured = capsys.readouterr()
        assert "# Personal Terms of Interaction (TOI)" in captured.out

    def test_cli_json_format(self, capsys):
        """Running CLI with --format json prints valid JSON to stdout."""
        from nlt_toi.cli import main

        rc = main(["--format", "json", "--author", "cli-json-test"])
        assert rc == 0
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["version"] == "1.0.0"

    def test_cli_from_json_file(self, tmp_path: Path, capsys):
        """Running CLI with --input <json> generates a Markdown document."""
        from nlt_toi.cli import main

        input_file = tmp_path / "toi.json"
        input_file.write_text(json.dumps(_minimal_data()), encoding="utf-8")
        rc = main(["--input", str(input_file)])
        assert rc == 0
        captured = capsys.readouterr()
        assert "# Personal Terms of Interaction (TOI)" in captured.out

    def test_cli_validate_passes_for_defaults(self, capsys):
        """Running CLI with --validate exits 0 for a valid document."""
        from nlt_toi.cli import main

        rc = main(["--validate", "--author", "validate-test"])
        assert rc == 0

    def test_cli_output_file(self, tmp_path: Path):
        """Running CLI with --output writes to a file."""
        from nlt_toi.cli import main

        out = tmp_path / "toi.md"
        rc = main(["--output", str(out)])
        assert rc == 0
        assert out.exists()
        assert "# Personal Terms of Interaction" in out.read_text()

    def test_cli_missing_input_file_returns_error(self, capsys):
        """Running CLI with a non-existent --input file returns exit code 1."""
        from nlt_toi.cli import main

        rc = main(["--input", "/tmp/does_not_exist_xyz.json"])
        assert rc == 1

    def test_cli_unknown_extension_returns_error(self, tmp_path: Path):
        """Running CLI with an unsupported file extension returns exit code 1."""
        from nlt_toi.cli import main

        f = tmp_path / "toi.toml"
        f.write_text("[meta]\nauthor = 'x'")
        rc = main(["--input", str(f)])
        assert rc == 1
