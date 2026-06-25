"""Command-line interface for the TOI generator.

Usage examples
--------------
Generate a TOI interactively and print Markdown::

    toi-generator --interactive

Generate from a JSON file and write Markdown output::

    toi-generator --input preferences.json --output my-toi.md

Generate from a YAML file and write JSON output::

    toi-generator --input preferences.yaml --format json --output my-toi.json

Validate an existing TOI file::

    toi-generator --input my-toi.json --validate

Generate Markdown with defaults (no interaction) and print to stdout::

    toi-generator --author "alice" --description "My daily coding TOI"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import jsonschema

from .generator import TOIDocumentGenerator


def _build_parser() -> argparse.ArgumentParser:
    """Return the configured :class:`argparse.ArgumentParser`."""
    parser = argparse.ArgumentParser(
        prog="toi-generator",
        description=(
            "Generate Personal Terms of Interaction (TOI) documents "
            "for the NeuroLift Solidarity Framework."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        "--input", "-i",
        metavar="FILE",
        type=Path,
        help="JSON or YAML file containing TOI preferences.",
    )
    source_group.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for preferences interactively (overrides --input).",
    )

    parser.add_argument(
        "--format", "-f",
        choices=["markdown", "md", "json"],
        default="markdown",
        metavar="FORMAT",
        help="Output format: 'markdown' (default) or 'json'.",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        type=Path,
        help="Write output to FILE instead of stdout.",
    )
    parser.add_argument(
        "--schema",
        metavar="SCHEMA",
        type=Path,
        help="Override the bundled JSON Schema with a custom one.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help=(
            "Validate the generated (or loaded) document against the schema "
            "and exit with code 0 on success or 1 on failure."
        ),
    )
    parser.add_argument(
        "--author",
        default="anonymous",
        help="Author identifier (used with --interactive or when no --input given).",
    )
    parser.add_argument(
        "--description",
        default="",
        help="Short description of this TOI (used when no --input given).",
    )

    return parser


def main(argv: Optional[list] = None) -> int:
    """Entry point for the ``toi-generator`` command.

    Args:
        argv: Override ``sys.argv[1:]`` for testing.

    Returns:
        Exit code — ``0`` on success, ``1`` on error.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    # ------------------------------------------------------------------
    # Build the generator
    # ------------------------------------------------------------------
    try:
        if args.input:
            gen = TOIDocumentGenerator.from_file(args.input, schema_path=args.schema)
        elif args.interactive:
            gen = TOIDocumentGenerator.from_defaults(
                author=args.author,
                description=args.description,
            )
            gen.prompt_interactive()
        else:
            # No source specified — use defaults with supplied metadata
            gen = TOIDocumentGenerator.from_defaults(
                author=args.author,
                description=args.description,
            )
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # ------------------------------------------------------------------
    # Validate
    # ------------------------------------------------------------------
    if args.validate:
        errors = gen.get_validation_errors()
        if errors:
            print("Validation FAILED:", file=sys.stderr)
            for err in errors:
                print(f"  • {err}", file=sys.stderr)
            return 1
        print("Validation passed ✓")
        return 0

    # ------------------------------------------------------------------
    # Render output
    # ------------------------------------------------------------------
    fmt = args.format.lower()
    if fmt in {"markdown", "md"}:
        content = gen.to_markdown()
    else:
        content = gen.to_json()

    if args.output:
        try:
            args.output.write_text(content, encoding="utf-8")
            print(f"Written to {args.output}")
        except OSError as exc:
            print(f"error: could not write to {args.output}: {exc}", file=sys.stderr)
            return 1
    else:
        print(content)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
