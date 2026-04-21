"""TOI-OTOI Governance and Orchestration Layer.

This module provides the governance framework for the NeuroLift AI-Fusion system:
    - TOIParser: Reads and validates user interaction preferences
    - OTOIOrchestrator: Coordinates multiple Advocates under user governance
    - PrivacyGuardian: Enforces privacy-first architecture with local-only processing
"""

from .toi_parser import TOIParser, TOIPreferences
from .otoi_orchestrator import OTOIOrchestrator, CollaborationContext
from .privacy_guardian import PrivacyGuardian, PrivacyPolicy

__all__ = [
    "TOIParser",
    "TOIPreferences",
    "OTOIOrchestrator",
    "CollaborationContext",
    "PrivacyGuardian",
    "PrivacyPolicy",
]
