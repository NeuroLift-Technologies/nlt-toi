"""High-level ``.toi`` document generation.

:class:`TOIDocumentGenerator` is a small authoring helper that produces
conforming ``.toi`` v1.0.0 documents from defaults or from a partial
preferences dictionary. It fills the required reserved keys (``$toi``,
``$tier``, ``identity``), applies privacy-first defaults, validates the result
through the canonical schema, and can render a human-readable Markdown
summary for review.

The generated document is plain data — nothing here evaluates preferences as
instructions (SPEC §2). Use :func:`nlt_toi.parse_toi` / :func:`nlt_toi.sign_toi`
for downstream parsing and signing.
"""
from __future__ import annotations

import json
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .constants import TOI_FORMAT_VERSION, TOI_TIERS
from .parse import ToiDocument, parse_toi, serialize_toi

__all__ = ["DEFAULT_DOCUMENT", "TOIDocumentGenerator"]


#: Privacy-first default preferences (CLAUDE.md: default to the most
#: privacy-preserving options; user agency first).
DEFAULT_DOCUMENT: Dict[str, Any] = {
    "$toi": TOI_FORMAT_VERSION,
    "$tier": "personal",
    "identity": {"author": ""},
    "cognitive_profile": {
        "scaffolding_preference": "moderate",
        "attention_model": "variable",
        "energy_model": "variable",
        "thread_support": True,
    },
    "privacy": {
        "retention": "session-only",
        "cross_platform_sharing": "never",
        "training_use": "prohibited",
        "analytics": "prohibited",
        "override_rights": "user-only",
        "data_requests": "honored-immediately",
    },
    "agency": {
        "task_initiation": "user-initiated",
        "ai_suggestions": "on-request",
        "interruptibility": "urgent-only",
        "action_confirmation": "destructive-only",
        "override_authority": "user-final",
    },
    "communication": {
        "tone": "direct",
        "verbosity": "concise",
        "structure": "bullet-points",
        "language": "en",
        "jargon_tolerance": "moderate",
        "pattern_highlighting": False,
        "summary_on_return": True,
        "thread_reconnection": "brief-summary",
    },
    "ethical_pillars": ["user-agency", "privacy-by-default"],
}


def _deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge *overlay* into *base*, returning a new mapping.

    Scalars and lists in *overlay* replace the base value wholesale (arrays are
    atomic leaves per SPEC §9); objects are merged per key.
    """
    result = deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


class TOIDocumentGenerator:
    """Author and validate a single ``.toi`` document.

    Example::

        from nlt_toi import TOIDocumentGenerator

        gen = TOIDocumentGenerator.from_defaults(author="alice")
        gen.validate()
        print(gen.to_markdown())

        gen = TOIDocumentGenerator.from_dict({"communication": {"tone": "friendly"}})
        gen.to_json()
    """

    def __init__(self, document: ToiDocument) -> None:
        """Wrap an already-validated document without re-authoring defaults."""
        self.document: ToiDocument = document

    @classmethod
    def from_defaults(
        cls,
        author: str,
        *,
        tier: str = "personal",
        handle: Optional[str] = None,
        organization: Optional[str] = None,
    ) -> TOIDocumentGenerator:
        """Build a privacy-first personal TOI for *author*.

        The returned document is validated before construction completes.
        """
        if tier not in TOI_TIERS:
            raise ValueError(f"tier must be one of {', '.join(TOI_TIERS)}; got {tier!r}")
        doc: ToiDocument = _deep_merge(DEFAULT_DOCUMENT, {"$tier": tier})
        doc["identity"] = _deep_merge(doc["identity"], {"author": author})
        if handle:
            doc["identity"]["handle"] = handle
        if organization:
            doc["identity"]["organization"] = organization
        doc["$created"] = datetime.now(timezone.utc).date().isoformat()
        doc["$id"] = str(uuid.uuid4())
        return cls(doc).validate()

    @classmethod
    def from_dict(
        cls,
        preferences: Dict[str, Any],
        *,
        author: Optional[str] = None,
        tier: Optional[str] = None,
    ) -> TOIDocumentGenerator:
        """Build a TOI from a (possibly partial) preferences dictionary.

        *preferences* may be a full ``.toi`` document or a partial set of
        content sections; missing fields fall back to the privacy-first
        defaults. ``author``/``tier`` keyword arguments override the document
        values so callers do not have to build the reserved keys by hand.
        """
        doc: ToiDocument = _deep_merge(DEFAULT_DOCUMENT, preferences or {})
        if author is not None:
            doc["identity"] = _deep_merge(doc["identity"], {"author": author})
        if tier is not None:
            if tier not in TOI_TIERS:
                raise ValueError(f"tier must be one of {', '.join(TOI_TIERS)}; got {tier!r}")
            doc["$tier"] = tier
        return cls(doc).validate()

    def validate(self) -> TOIDocumentGenerator:
        """Validate the document against the canonical schema; raise on failure."""
        self.document = parse_toi(self.document)
        return self

    def to_dict(self) -> ToiDocument:
        """Return a fresh copy of the document."""
        return deepcopy(self.document)

    def to_json(self, *, pretty: bool = True) -> str:
        """Serialize the document to its on-disk JSON form."""
        return serialize_toi(self.document, pretty=pretty)

    def to_markdown(self) -> str:
        """Render a human-readable Markdown summary of the document.

        This is a review aid, not a machine format — the canonical form is
        ``to_json()``/the on-disk ``.toi`` file.
        """
        doc = self.document
        lines: list[str] = []
        identity = doc.get("identity", {})
        title = identity.get("author") or doc.get("$tier", "personal")
        lines.append(f"# Terms of Interaction — {title}")
        lines.append("")
        lines.append(f"- **Version**: {doc.get('$toi', '1.0.0')} ({doc.get('$tier', 'personal')} tier)")
        if doc.get("$created"):
            lines.append(f"- **Created**: {doc['$created']}")
        if identity.get("handle"):
            lines.append(f"- **Handle**: {identity['handle']}")
        if identity.get("organization"):
            lines.append(f"- **Organization**: {identity['organization']}")

        sections = [
            ("identity", "Identity"),
            ("cognitive_profile", "Cognitive profile"),
            ("privacy", "Privacy and data"),
            ("agency", "Agency"),
            ("communication", "Communication"),
            ("ethical_pillars", "Ethical pillars"),
        ]
        for key, label in sections:
            value = doc.get(key)
            if not value:
                continue
            lines.append("")
            lines.append(f"## {label}")
            lines.append("")
            if isinstance(value, list):
                for item in value:
                    lines.append(f"- {item}")
            elif isinstance(value, dict):
                for field, field_value in value.items():
                    if field in ("$schema",):
                        continue
                    rendered = str(field_value).replace("_", " ").title() if isinstance(field_value, str) else str(field_value)
                    lines.append(f"- **{field.replace('_', ' ').title()}**: {rendered}")
            else:
                lines.append(f"- {value}")

        if doc.get("custom"):
            lines.append("")
            lines.append("## Custom")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(doc["custom"], indent=2, ensure_ascii=False))
            lines.append("```")

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("_Machine-readable form: JSON following the `.toi` v1.0.0 spec "
                     "(see `nlt_toi` schema)._")
        return "\n".join(lines) + "\n"

    def write(self, path: str, *, pretty: bool = True) -> None:
        """Write the JSON form of the document to *path* (``.toi`` or ``.json``)."""
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.to_json(pretty=pretty))