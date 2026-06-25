"""TOI document generator — core library.

Generates Personal Terms of Interaction (TOI) documents from:
  - A Python dictionary / minimal keyword arguments
  - A JSON or YAML input file
  - Interactive CLI prompts (see :func:`TOIDocumentGenerator.prompt_interactive`)

Each generator instance can render output as Markdown or JSON and validates
the structured data against the bundled JSON Schema (Draft 2020-12) before
returning.

Neurodivergent-friendly design principles applied here:
  - Sensible privacy-first, low-cognitive-load defaults so a user can call
    ``TOIDocumentGenerator.from_defaults()`` and immediately get a valid doc.
  - Every prompt is optional — pressing Enter accepts the default.
  - Validation errors are worded plainly with actionable guidance.
"""
from __future__ import annotations

import importlib.resources
import json
from copy import deepcopy
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, List, Optional, Union

import jsonschema

# ---------------------------------------------------------------------------
# Optional YAML support (PyYAML).  Gracefully degrade if not installed.
# ---------------------------------------------------------------------------
try:
    import yaml as _yaml

    _YAML_AVAILABLE = True
except ImportError:  # pragma: no cover
    _YAML_AVAILABLE = False

# ---------------------------------------------------------------------------
# Canonical JSON Schema location
# ---------------------------------------------------------------------------
# Schemas ship *inside* the installed package (``nlt_toi/schemas/``) — the build
# backend force-includes the repo-root ``schemas/`` directory there (see
# pyproject.toml).  When running from a source checkout (src/ layout, where the
# schemas live at the repo root rather than inside the package), we fall back to
# that location so the library works without an install.
_DEFAULT_SCHEMA_NAME = "personal-toi.schema.json"


def _read_bundled_schema(filename: str) -> str:
    """Return the text of a bundled JSON Schema by *filename*.

    Resolution order:
      1. Package data (``nlt_toi/schemas/<filename>``) — how the schema ships
         when installed from a wheel or sdist.
      2. Repo-root ``schemas/<filename>`` — source-checkout fallback so the
         library works without an install (e.g. ``pytest`` via ``pythonpath``).

    Raises:
        FileNotFoundError: if the schema cannot be located in either place.
    """
    try:
        ref = importlib.resources.files(__package__) / "schemas" / filename
        if ref.is_file():
            return ref.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, NotADirectoryError):
        pass
    # Source checkout: src/nlt_toi/generator.py -> parents[2] == repo root.
    fallback = Path(__file__).resolve().parents[2] / "schemas" / filename
    if fallback.is_file():
        return fallback.read_text(encoding="utf-8")
    raise FileNotFoundError(
        f"Bundled schema {filename!r} could not be located in package data "
        f"or at {fallback}."
    )

# ---------------------------------------------------------------------------
# Privacy-first, neurodivergent-friendly defaults
# ---------------------------------------------------------------------------
DEFAULTS: Dict[str, Any] = {
    "version": "1.0.0",
    "communication": {
        "style": "adaptive",
        "directness": "direct",
        "feedback_preference": "on-request",
        "question_style": "structured",
        "explanation_level": "detailed",
    },
    "cognitive": {
        "processing_time": "flexible",
        "information_structure": "bullet-points",
        "cognitive_load": "moderate",
        "attention_span": "flexible",
        "decision_support": "step-by-step",
        "sensory_preferences": {
            "text_density": "moderate",
            "color_sensitivity": False,
            "motion_sensitivity": False,
        },
    },
    "privacy": {
        "data_retention": "session-only",
        "sharing_consent": "never",
        "anonymization": True,
        "third_party_access": False,
        "audit_trail": True,
    },
    "energy_management": {
        "interaction_frequency": "on-demand",
        "complexity_adaptation": True,
        "break_reminders": True,
        "energy_level_tracking": False,
    },
    "collaboration": {
        "agent_coordination": "user-mediated",
        "conflict_resolution": "user-decides",
        "delegation_comfort": "simple-tasks",
    },
    "accessibility": {
        "screen_reader": False,
        "keyboard_only": False,
        "high_contrast": False,
        "reduced_motion": False,
        "alternative_formats": [],
    },
}


# ---------------------------------------------------------------------------
# Dataclass for a Personal TOI document
# ---------------------------------------------------------------------------

@dataclass
class PersonalTOI:
    """A complete Personal Terms of Interaction document.

    Attributes:
        version: Schema version string (semver).
        metadata: Creation timestamps and author identifier.
        communication: Communication style preferences.
        cognitive: Cognitive accessibility preferences.
        privacy: Privacy and data-handling requirements.
        energy_management: Spoon-theory / energy-aware interaction settings.
        collaboration: Multi-agent collaboration preferences.
        accessibility: Specific assistive-technology requirements.
    """

    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    communication: Dict[str, Any] = field(default_factory=dict)
    cognitive: Dict[str, Any] = field(default_factory=dict)
    privacy: Dict[str, Any] = field(default_factory=dict)
    energy_management: Dict[str, Any] = field(default_factory=dict)
    collaboration: Dict[str, Any] = field(default_factory=dict)
    accessibility: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return the document as a plain dictionary (JSON-serialisable)."""
        return asdict(self)


# ---------------------------------------------------------------------------
# Main generator class
# ---------------------------------------------------------------------------

class TOIDocumentGenerator:
    """Generates, validates, and renders Personal TOI documents.

    Usage (library)::

        gen = TOIDocumentGenerator.from_defaults(author="alice")
        print(gen.to_markdown())
        print(gen.to_json())

    Usage (from file)::

        gen = TOIDocumentGenerator.from_file("preferences.json")
        gen.validate()  # raises jsonschema.ValidationError on failure
        gen.to_markdown()
    """

    def __init__(
        self,
        toi: PersonalTOI,
        schema_path: Optional[Path] = None,
    ) -> None:
        self._toi = toi
        # ``None`` means "use the bundled personal-TOI schema"; a caller-supplied
        # path (``--schema`` / ``from_file(schema_path=...)``) overrides it.
        self._schema_path = schema_path
        self._schema: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Factory constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_defaults(cls, author: str = "anonymous", description: str = "") -> "TOIDocumentGenerator":
        """Create a generator pre-filled with privacy-first, neurodivergent-
        friendly defaults.

        Args:
            author: Identifier for the TOI author (may be pseudonymous).
            description: Optional plain-text description of this TOI's purpose.

        Returns:
            A ready-to-use :class:`TOIDocumentGenerator` instance.
        """
        now = datetime.now(timezone.utc).isoformat()
        data = deepcopy(DEFAULTS)
        data["metadata"] = {
            "created": now,
            "updated": now,
            "author": author,
            "description": description,
        }
        toi = PersonalTOI(
            version=data["version"],
            metadata=data["metadata"],
            communication=data["communication"],
            cognitive=data["cognitive"],
            privacy=data["privacy"],
            energy_management=data["energy_management"],
            collaboration=data["collaboration"],
            accessibility=data["accessibility"],
        )
        return cls(toi)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], schema_path: Optional[Path] = None) -> "TOIDocumentGenerator":
        """Create a generator from a plain dictionary.

        Missing top-level sections are filled from :data:`DEFAULTS` so the
        result is always schema-valid after a successful :meth:`validate` call.

        Args:
            data: Dictionary that (at minimum) contains ``version``,
                  ``metadata``, ``communication``, ``cognitive``, and
                  ``privacy`` keys.
            schema_path: Override the bundled schema with a custom one.

        Returns:
            :class:`TOIDocumentGenerator` populated from *data*.
        """
        merged = deepcopy(DEFAULTS)
        # Shallow-merge each top-level section dict with the caller's values.
        # Nested dicts (e.g. cognitive.sensory_preferences) are replaced wholesale
        # rather than recursively merged; callers should supply a complete nested
        # dict if they want to override nested fields.
        for key, value in data.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value

        toi = PersonalTOI(
            version=merged.get("version", "1.0.0"),
            metadata=merged.get("metadata", {}),
            communication=merged.get("communication", {}),
            cognitive=merged.get("cognitive", {}),
            privacy=merged.get("privacy", {}),
            energy_management=merged.get("energy_management", {}),
            collaboration=merged.get("collaboration", {}),
            accessibility=merged.get("accessibility", {}),
        )
        return cls(toi, schema_path=schema_path)

    @classmethod
    def from_file(cls, path: Union[str, Path], schema_path: Optional[Path] = None) -> "TOIDocumentGenerator":
        """Load a TOI document from a JSON or YAML file.

        The format is inferred from the file extension:
          - ``.json`` → JSON
          - ``.yaml`` / ``.yml`` → YAML (requires PyYAML)

        Args:
            path: Path to the input file.
            schema_path: Override the bundled schema with a custom one.

        Returns:
            :class:`TOIDocumentGenerator` loaded from *path*.

        Raises:
            FileNotFoundError: If *path* does not exist.
            ValueError: If the file extension is not recognised or PyYAML is
                        required but not installed.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")

        suffix = path.suffix.lower()
        if suffix == ".json":
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        elif suffix in {".yaml", ".yml"}:
            if not _YAML_AVAILABLE:
                raise ValueError(
                    "PyYAML is required to load YAML files.  "
                    "Install it with: pip install pyyaml"
                )
            with open(path, "r", encoding="utf-8") as fh:
                data = _yaml.safe_load(fh)
        else:
            raise ValueError(
                f"Unsupported file extension '{suffix}'. "
                "Use .json, .yaml, or .yml."
            )

        return cls.from_dict(data, schema_path=schema_path)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON Schema (cached after first call)."""
        if self._schema is None:
            if self._schema_path is not None:
                with open(self._schema_path, "r", encoding="utf-8") as fh:
                    self._schema = json.load(fh)
            else:
                self._schema = json.loads(_read_bundled_schema(_DEFAULT_SCHEMA_NAME))
        return self._schema

    def validate(self) -> None:
        """Validate the current TOI document against the JSON Schema.

        Uses JSON Schema Draft 2020-12 as shipped in
        ``schemas/personal-toi.schema.json``.

        Raises:
            jsonschema.ValidationError: If the document does not conform to
                the schema.  The error message includes the field path and a
                plain-English hint.
        """
        schema = self._load_schema()
        jsonschema.validate(self._toi.to_dict(), schema)

    def is_valid(self) -> bool:
        """Return ``True`` if the document passes schema validation.

        Unlike :meth:`validate`, this method never raises; validation errors
        are silently swallowed.
        """
        try:
            self.validate()
            return True
        except jsonschema.ValidationError:
            return False

    def get_validation_errors(self) -> List[str]:
        """Return a list of plain-English validation error messages.

        Returns an empty list when the document is valid.
        """
        schema = self._load_schema()
        validator = jsonschema.Draft202012Validator(schema)
        errors: List[str] = []
        for err in sorted(validator.iter_errors(self._toi.to_dict()), key=str):
            path = " → ".join(str(p) for p in err.absolute_path) or "document root"
            errors.append(f"At '{path}': {err.message}")
        return errors

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    @property
    def toi(self) -> PersonalTOI:
        """The underlying :class:`PersonalTOI` dataclass."""
        return self._toi

    def to_dict(self) -> Dict[str, Any]:
        """Return the TOI document as a plain dictionary."""
        return self._toi.to_dict()

    def to_json(self, indent: int = 2) -> str:
        """Serialise the TOI document to a JSON string.

        Args:
            indent: Number of spaces for JSON indentation (default: 2).

        Returns:
            Pretty-printed JSON string.
        """
        return json.dumps(self._toi.to_dict(), indent=indent, ensure_ascii=False)

    def to_markdown(self) -> str:
        """Render the TOI document as a human-readable Markdown string.

        The output is structured for accessibility: clear heading hierarchy,
        bullet-point lists, and plain language.

        Returns:
            Markdown-formatted string.
        """
        toi = self._toi
        meta = toi.metadata
        comm = toi.communication
        cog = toi.cognitive
        priv = toi.privacy
        em = toi.energy_management
        collab = toi.collaboration
        acc = toi.accessibility

        lines: List[str] = []

        # --- Title ---
        lines.append("# Personal Terms of Interaction (TOI)")
        lines.append("")

        # --- Metadata ---
        lines.append("## Metadata")
        lines.append("")
        lines.append(f"- **Version**: {toi.version}")
        if meta.get("author"):
            lines.append(f"- **Author**: {meta['author']}")
        if meta.get("description"):
            lines.append(f"- **Description**: {meta['description']}")
        if meta.get("created"):
            lines.append(f"- **Created**: {meta['created']}")
        if meta.get("updated"):
            lines.append(f"- **Last Updated**: {meta['updated']}")
        lines.append("")

        # --- Communication ---
        lines.append("## Communication Preferences")
        lines.append("")
        if comm.get("style"):
            lines.append(f"- **Style**: {comm['style']}")
        if comm.get("directness"):
            lines.append(f"- **Directness**: {comm['directness']}")
        if comm.get("feedback_preference"):
            lines.append(f"- **Feedback Preference**: {comm['feedback_preference']}")
        if comm.get("question_style"):
            lines.append(f"- **Question Style**: {comm['question_style']}")
        if comm.get("explanation_level"):
            lines.append(f"- **Explanation Level**: {comm['explanation_level']}")
        lines.append("")

        # --- Cognitive ---
        lines.append("## Cognitive Preferences")
        lines.append("")
        if cog.get("processing_time"):
            lines.append(f"- **Processing Time**: {cog['processing_time']}")
        if cog.get("information_structure"):
            lines.append(f"- **Information Structure**: {cog['information_structure']}")
        if cog.get("cognitive_load"):
            lines.append(f"- **Cognitive Load**: {cog['cognitive_load']}")
        if cog.get("attention_span"):
            lines.append(f"- **Attention Span**: {cog['attention_span']}")
        if cog.get("decision_support"):
            lines.append(f"- **Decision Support**: {cog['decision_support']}")
        sensory = cog.get("sensory_preferences", {})
        if sensory:
            lines.append("- **Sensory Preferences**:")
            if "text_density" in sensory:
                lines.append(f"  - Text Density: {sensory['text_density']}")
            if "color_sensitivity" in sensory:
                lines.append(f"  - Color Sensitivity: {sensory['color_sensitivity']}")
            if "motion_sensitivity" in sensory:
                lines.append(f"  - Motion Sensitivity: {sensory['motion_sensitivity']}")
        lines.append("")

        # --- Privacy ---
        lines.append("## Privacy Settings")
        lines.append("")
        if priv.get("data_retention"):
            lines.append(f"- **Data Retention**: {priv['data_retention']}")
        if priv.get("sharing_consent"):
            lines.append(f"- **Sharing Consent**: {priv['sharing_consent']}")
        if "anonymization" in priv:
            lines.append(f"- **Anonymization**: {priv['anonymization']}")
        if "third_party_access" in priv:
            lines.append(f"- **Third-Party Access**: {priv['third_party_access']}")
        if "audit_trail" in priv:
            lines.append(f"- **Audit Trail**: {priv['audit_trail']}")
        lines.append("")

        # --- Energy Management ---
        lines.append("## Energy Management")
        lines.append("")
        if em.get("interaction_frequency"):
            lines.append(f"- **Interaction Frequency**: {em['interaction_frequency']}")
        if "complexity_adaptation" in em:
            lines.append(f"- **Complexity Adaptation**: {em['complexity_adaptation']}")
        if "break_reminders" in em:
            lines.append(f"- **Break Reminders**: {em['break_reminders']}")
        if "energy_level_tracking" in em:
            lines.append(f"- **Energy Level Tracking**: {em['energy_level_tracking']}")
        lines.append("")

        # --- Collaboration ---
        lines.append("## Collaboration Preferences")
        lines.append("")
        if collab.get("agent_coordination"):
            lines.append(f"- **Agent Coordination**: {collab['agent_coordination']}")
        if collab.get("conflict_resolution"):
            lines.append(f"- **Conflict Resolution**: {collab['conflict_resolution']}")
        if collab.get("delegation_comfort"):
            lines.append(f"- **Delegation Comfort**: {collab['delegation_comfort']}")
        lines.append("")

        # --- Accessibility ---
        lines.append("## Accessibility")
        lines.append("")
        if "screen_reader" in acc:
            lines.append(f"- **Screen Reader**: {acc['screen_reader']}")
        if "keyboard_only" in acc:
            lines.append(f"- **Keyboard Only**: {acc['keyboard_only']}")
        if "high_contrast" in acc:
            lines.append(f"- **High Contrast**: {acc['high_contrast']}")
        if "reduced_motion" in acc:
            lines.append(f"- **Reduced Motion**: {acc['reduced_motion']}")
        alt_formats = acc.get("alternative_formats", [])
        if alt_formats:
            lines.append(f"- **Alternative Formats**: {', '.join(alt_formats)}")
        lines.append("")

        # --- Footer ---
        lines.append("---")
        lines.append("")
        lines.append(
            "_Generated by nlt-toi TOI Generator — "
            "NeuroLift Solidarity Framework_"
        )
        lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Interactive prompt
    # ------------------------------------------------------------------

    def prompt_interactive(self) -> None:  # pragma: no cover — UI I/O
        """Interactively prompt the user to customise TOI fields.

        Every question shows the current default in brackets.  Pressing Enter
        without typing anything keeps the default.  This method mutates
        :attr:`toi` in-place.
        """

        def _ask(prompt: str, default: str) -> str:
            """Print *prompt* with *default* hint; return answer or default."""
            answer = input(f"{prompt} [{default}]: ").strip()
            return answer if answer else default

        def _ask_bool(prompt: str, default: bool) -> bool:
            hint = "Y/n" if default else "y/N"
            answer = input(f"{prompt} [{hint}]: ").strip().lower()
            if answer in {"y", "yes"}:
                return True
            if answer in {"n", "no"}:
                return False
            return default

        print(dedent("""
            ╔══════════════════════════════════════════════════════════════╗
            ║         TOI Generator — Interactive Setup                    ║
            ║  Press Enter to accept defaults  •  Ctrl-C to cancel         ║
            ╚══════════════════════════════════════════════════════════════╝
        """))

        # Metadata
        toi = self._toi
        toi.metadata["author"] = _ask("Your name / pseudonym", toi.metadata.get("author", "anonymous"))
        toi.metadata["description"] = _ask("Short description of this TOI", toi.metadata.get("description", ""))
        now = datetime.now(timezone.utc).isoformat()
        toi.metadata.setdefault("created", now)
        toi.metadata["updated"] = now

        print("\n— Communication —")
        style_choices = "formal / casual / professional / friendly / adaptive"
        toi.communication["style"] = _ask(f"Communication style ({style_choices})", toi.communication.get("style", "adaptive"))
        directness_choices = "very-direct / direct / moderate / indirect / context-sensitive"
        toi.communication["directness"] = _ask(f"Directness ({directness_choices})", toi.communication.get("directness", "direct"))
        explain_choices = "minimal / concise / detailed / comprehensive / adaptive"
        toi.communication["explanation_level"] = _ask(f"Explanation level ({explain_choices})", toi.communication.get("explanation_level", "detailed"))

        print("\n— Cognitive —")
        proc_choices = "immediate / short / moderate / extended / flexible"
        toi.cognitive["processing_time"] = _ask(f"Processing time ({proc_choices})", toi.cognitive.get("processing_time", "flexible"))
        struct_choices = "linear / hierarchical / visual / bullet-points / narrative"
        toi.cognitive["information_structure"] = _ask(f"Information structure ({struct_choices})", toi.cognitive.get("information_structure", "bullet-points"))

        print("\n— Privacy —")
        retention_choices = "session-only / short-term / long-term / permanent / user-controlled"
        toi.privacy["data_retention"] = _ask(f"Data retention ({retention_choices})", toi.privacy.get("data_retention", "session-only"))
        sharing_choices = "never / explicit-only / aggregate-only / research-approved"
        toi.privacy["sharing_consent"] = _ask(f"Sharing consent ({sharing_choices})", toi.privacy.get("sharing_consent", "never"))

        print("\n— Accessibility —")
        toi.accessibility["screen_reader"] = _ask_bool("Do you use a screen reader?", toi.accessibility.get("screen_reader", False))
        toi.accessibility["reduced_motion"] = _ask_bool("Prefer reduced motion?", toi.accessibility.get("reduced_motion", False))
        toi.accessibility["high_contrast"] = _ask_bool("Prefer high contrast?", toi.accessibility.get("high_contrast", False))

        print("\n✅  Preferences recorded.  Use --format to choose output format.")

    def save(self, output_path: Union[str, Path], fmt: str = "markdown") -> Path:
        """Write the TOI document to *output_path*.

        Args:
            output_path: Destination file path.
            fmt: ``"markdown"`` (default) or ``"json"``.

        Returns:
            The resolved :class:`~pathlib.Path` that was written.

        Raises:
            ValueError: If *fmt* is not ``"markdown"`` or ``"json"``.
        """
        path = Path(output_path)
        fmt = fmt.lower()
        if fmt in {"markdown", "md"}:
            content = self.to_markdown()
        elif fmt == "json":
            content = self.to_json()
        else:
            raise ValueError(f"Unknown format '{fmt}'. Use 'markdown' or 'json'.")
        path.write_text(content, encoding="utf-8")
        return path


__all__ = [
    "PersonalTOI",
    "TOIDocumentGenerator",
    "DEFAULTS",
]
