"""``toi-generator`` — author and validate ``.toi`` documents from the CLI.

Supports the surface documented for the ``nlt-toi`` package:

- ``--interactive``  run a guided wizard and write the result
- ``--input FILE``   build a document from a JSON preferences file
- ``--validate``     check an existing ``.toi`` document against the schema
- ``--output`` / ``--format``  control where and how the result is written

Output format is inferred from the output filename (``.md`` → Markdown, else
JSON) and can be forced with ``--format``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .errors import ToiError
from .generator import DEFAULT_DOCUMENT, TOIDocumentGenerator
from .parse import safe_parse_toi
from .schema import toi_schema

__all__ = ["build_document", "main", "wizard_document"]

_PROMPT: Callable[[str], str] = input

_OPTIONS: Dict[str, List[str]] = {
    "communication.tone": ["formal", "casual", "professional", "friendly", "direct", "adaptive"],
    "communication.verbosity": ["minimal", "concise", "detailed", "comprehensive", "adaptive"],
    "communication.structure": ["linear", "hierarchical", "visual", "bullet-points", "narrative"],
    "communication.jargon_tolerance": ["none", "low", "moderate", "high"],
    "privacy.retention": ["session-only", "short-term", "long-term", "permanent", "user-controlled"],
    "privacy.cross_platform_sharing": ["never", "explicit-only", "aggregate-only", "research-approved"],
    "privacy.training_use": ["prohibited", "explicit-only", "anonymized-only", "permitted"],
    "privacy.analytics": ["prohibited", "opt-in", "anonymized-only", "permitted"],
    "privacy.override_rights": ["user-only", "delegated", "admin-allowed"],
    "agency.task_initiation": ["user-initiated", "ai-may-suggest", "ai-may-initiate"],
    "agency.ai_suggestions": ["none", "on-request", "proactive"],
    "agency.interruptibility": ["never", "urgent-only", "always"],
    "agency.action_confirmation": ["always", "destructive-only", "never"],
    "agency.override_authority": ["user-final", "shared", "ai-advisory"],
    "cognitive_profile.scaffolding_preference": ["minimal", "moderate", "extensive", "step-by-step"],
    "cognitive_profile.attention_model": ["sustained", "short-bursts", "hyperfocus-prone", "variable"],
    "cognitive_profile.energy_model": ["steady", "variable", "spoon-limited", "burst"],
}


def _lookup(doc: Dict[str, Any], dotted: str) -> Any:
    current: Any = doc
    for part in dotted.split("."):
        current = current.get(part) if isinstance(current, dict) else None
    return current


def _default_for(dotted: str) -> Any:
    return _lookup(DEFAULT_DOCUMENT, dotted)


def wizard_document(
    author: str,
    *,
    tier: str = "personal",
    prompt: Callable[[str], str] = _PROMPT,
) -> TOIDocumentGenerator:
    """Run an interactive multiple-choice wizard and return a generated TOI.

    Each preference is a numbered choice with a privacy-first default shown;
    an empty answer keeps the default. Structured choices (not open-ended
    prompts) keep the wizard accessible for neurodivergent users.
    """
    if not author:
        author = prompt("Author/identifier (shown on the document): ").strip()
    if not author:
        author = "anonymous"

    prefs: Dict[str, Any] = {}
    for dotted, options in _OPTIONS.items():
        default = _default_for(dotted)
        if default not in options and default is not None:
            options = [default] + options
        section, _, field = dotted.partition(".")
        numbered = [f"{i + 1}) {opt}" for i, opt in enumerate(options)]
        answer = prompt(f"{field.replace('_', ' ').title()} (default: {default}) [{', '.join(numbered)}]: ").strip()
        if not answer:
            value: Any = default
        elif answer.isdigit() and 1 <= int(answer) <= len(options):
            value = options[int(answer) - 1]
        else:
            value = answer
        prefs.setdefault(section, {})[field] = value

    return TOIDocumentGenerator.from_dict(prefs, author=author, tier=tier)


def build_document(
    prefs_file: Optional[Path],
    *,
    author: Optional[str],
    tier: Optional[str],
) -> TOIDocumentGenerator:
    """Build a document from a JSON preferences file (or defaults)."""
    if prefs_file is not None:
        try:
            raw = prefs_file.read_text(encoding="utf-8")
        except OSError as err:
            raise ValueError(f"cannot read {prefs_file}: {err}") from err
        try:
            preferences = json.loads(raw)
        except (ValueError, TypeError) as err:
            raise ValueError(f"{prefs_file} is not valid JSON: {err}") from err
        if not isinstance(preferences, dict):
            raise ValueError(f"{prefs_file} must contain a JSON object of preferences")
    else:
        preferences = {}
    return TOIDocumentGenerator.from_dict(preferences, author=author, tier=tier)


def _render(document: TOIDocumentGenerator, fmt: str) -> str:
    if fmt == "markdown":
        return document.to_markdown()
    return document.to_json()


def _infer_format(output: Optional[Path], fmt: Optional[str]) -> str:
    if fmt:
        return fmt
    if output is not None and output.suffix.lower() == ".md":
        return "markdown"
    return "json"


def main(argv: Optional[List[str]] = None) -> int:
    """``toi-generator`` entry point; returns the process exit code."""
    parser = argparse.ArgumentParser(
        prog="toi-generator",
        description="Author and validate .toi (Terms of Interaction) v1.0.0 documents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  toi-generator --interactive --output me.toi\n"
            "  toi-generator --interactive --output me.md\n"
            "  toi-generator --input preferences.json --output me.toi\n"
            "  toi-generator --input me.toi --validate\n"
            "  toi-generator --schema\n"
        ),
    )
    parser.add_argument("--interactive", action="store_true", help="run the guided authoring wizard")
    parser.add_argument("--input", type=Path, metavar="FILE", help="JSON preferences file or a .toi document")
    parser.add_argument("--output", type=Path, metavar="FILE", help="write result here (.md => Markdown, else JSON)")
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        help="output format (default: inferred from --output suffix; JSON if unknown)",
    )
    parser.add_argument("--author", metavar="NAME", help="identity.author for the generated document (default: anonymous)")
    parser.add_argument(
        "--tier",
        choices=["personal", "community", "project"],
        default=None,
        help="interaction tier (default: personal when generating a new document; preserved when --input supplies one)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="with --input, validate the document and report violations",
    )
    parser.add_argument("--schema", action="store_true", help="print the canonical JSON Schema and exit")
    args = parser.parse_args(argv)

    if args.schema:
        json.dump(toi_schema(), sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0

    if args.validate:
        return _run_validate(args.input, parser)

    if args.interactive:
        try:
            document = wizard_document(args.author or "", tier=args.tier or "personal")
        except ToiError as err:
            print(f"error: {err}", file=sys.stderr)
            return 1
    else:
        try:
            document = build_document(args.input, author=args.author, tier=args.tier)
        except (ValueError, ToiError) as err:
            print(f"error: {err}", file=sys.stderr)
            return 1

    try:
        document.validate()
    except ToiError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    fmt = _infer_format(args.output, args.format)
    rendered = _render(document, fmt)
    if args.output is not None:
        try:
            args.output.write_text(rendered, encoding="utf-8")
        except OSError as err:
            print(f"error: cannot write {args.output}: {err}", file=sys.stderr)
            return 1
        print(f"✓ Wrote {fmt} document to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(rendered)
    return 0


def _run_validate(input_path: Optional[Path], parser: argparse.ArgumentParser) -> int:
    if input_path is None:
        parser.error("--validate requires --input FILE")
    try:
        raw = input_path.read_text(encoding="utf-8")
    except OSError as err:
        print(f"error: cannot read {input_path}: {err}", file=sys.stderr)
        return 1
    result = safe_parse_toi(raw)
    if result.success:
        print(f"✓ {input_path} is a valid .toi document", file=sys.stderr)
        return 0
    assert result.error is not None
    print(f"✗ {input_path} is not a valid .toi document", file=sys.stderr)
    if getattr(result.error, "issues", None):
        for issue in result.error.issues:  # type: ignore[attr-defined]
            where = f"{issue.path}: " if issue.path else ""
            print(f"  - {where}{issue.message}", file=sys.stderr)
    else:
        print(f"  - {result.error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())