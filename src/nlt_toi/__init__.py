"""nlt_toi — TOI generator for the NeuroLift Solidarity Framework.

Provides a CLI tool and importable library for creating Personal Terms of
Interaction (TOI) documents from interactive prompts or JSON/YAML input files.
Output can be Markdown (primary) or JSON.  Every generated document is
validated against the included JSON Schema (Draft 2020-12).
"""

from .generator import PersonalTOI, TOIDocumentGenerator, DEFAULTS

__version__ = "0.2.0"

__all__ = [
    "PersonalTOI",
    "TOIDocumentGenerator",
    "DEFAULTS",
]
