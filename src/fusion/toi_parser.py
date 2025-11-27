"""TOI (Terms of Interaction) Parser.

Reads and validates user interaction preferences from TOI documents.
TOI functions as a user-authored "constitution" that agents must honor.

Key Responsibilities:
    - Parse TOI documents (JSON/YAML)
    - Validate against schema
    - Provide typed access to preferences
    - Support preference inheritance and defaults

Neurodivergent-Friendly Design:
    - Clear validation error messages
    - Progressive disclosure of settings
    - Sensible defaults for common use cases
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import jsonschema


class CommunicationStyle(str, Enum):
    """User's preferred communication style."""
    FORMAL = "formal"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    ADAPTIVE = "adaptive"


class DirectnessLevel(str, Enum):
    """User's preferred level of directness in communication."""
    VERY_DIRECT = "very-direct"
    DIRECT = "direct"
    MODERATE = "moderate"
    INDIRECT = "indirect"
    CONTEXT_SENSITIVE = "context-sensitive"


class ProcessingTime(str, Enum):
    """Time user needs to process information."""
    IMMEDIATE = "immediate"
    SHORT = "short"
    MODERATE = "moderate"
    EXTENDED = "extended"
    FLEXIBLE = "flexible"


class InformationStructure(str, Enum):
    """User's preferred way to receive structured information."""
    LINEAR = "linear"
    HIERARCHICAL = "hierarchical"
    VISUAL = "visual"
    BULLET_POINTS = "bullet-points"
    NARRATIVE = "narrative"


class DataRetention(str, Enum):
    """How long user data should be kept."""
    SESSION_ONLY = "session-only"
    SHORT_TERM = "short-term"
    LONG_TERM = "long-term"
    PERMANENT = "permanent"
    USER_CONTROLLED = "user-controlled"


class SharingConsent(str, Enum):
    """User's data sharing permissions."""
    NEVER = "never"
    EXPLICIT_ONLY = "explicit-only"
    AGGREGATE_ONLY = "aggregate-only"
    RESEARCH_APPROVED = "research-approved"


@dataclass
class CommunicationPreferences:
    """User's communication preferences.
    
    Defines how AI should communicate with the user,
    respecting their cognitive style and preferences.
    """
    style: CommunicationStyle = CommunicationStyle.ADAPTIVE
    directness: DirectnessLevel = DirectnessLevel.DIRECT
    feedback_preference: str = "on-request"
    question_style: str = "structured"
    explanation_level: str = "detailed"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommunicationPreferences":
        """Create from dictionary, handling enum conversion."""
        return cls(
            style=CommunicationStyle(data.get("style", "adaptive")),
            directness=DirectnessLevel(data.get("directness", "direct")),
            feedback_preference=data.get("feedback_preference", "on-request"),
            question_style=data.get("question_style", "structured"),
            explanation_level=data.get("explanation_level", "detailed"),
        )


@dataclass
class CognitivePreferences:
    """User's cognitive accessibility preferences.
    
    Supports neurodivergent users by adapting to their
    information processing style and energy levels.
    """
    processing_time: ProcessingTime = ProcessingTime.MODERATE
    information_structure: InformationStructure = InformationStructure.BULLET_POINTS
    cognitive_load: str = "moderate"
    attention_span: str = "flexible"
    decision_support: str = "step-by-step"
    sensory_preferences: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CognitivePreferences":
        """Create from dictionary, handling enum conversion."""
        return cls(
            processing_time=ProcessingTime(data.get("processing_time", "moderate")),
            information_structure=InformationStructure(data.get("information_structure", "bullet-points")),
            cognitive_load=data.get("cognitive_load", "moderate"),
            attention_span=data.get("attention_span", "flexible"),
            decision_support=data.get("decision_support", "step-by-step"),
            sensory_preferences=data.get("sensory_preferences", {}),
        )


@dataclass
class PrivacyPreferences:
    """User's privacy and data handling requirements.
    
    Enforces user control over their data, supporting
    the privacy-first architecture principle.
    """
    data_retention: DataRetention = DataRetention.SESSION_ONLY
    sharing_consent: SharingConsent = SharingConsent.NEVER
    anonymization: bool = True
    third_party_access: bool = False
    audit_trail: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PrivacyPreferences":
        """Create from dictionary, handling enum conversion."""
        return cls(
            data_retention=DataRetention(data.get("data_retention", "session-only")),
            sharing_consent=SharingConsent(data.get("sharing_consent", "never")),
            anonymization=data.get("anonymization", True),
            third_party_access=data.get("third_party_access", False),
            audit_trail=data.get("audit_trail", True),
        )


@dataclass
class EnergyManagement:
    """User's energy and interaction management preferences.
    
    Supports spoon theory and energy-aware interaction,
    critical for neurodivergent users.
    """
    interaction_frequency: str = "on-demand"
    complexity_adaptation: bool = True
    break_reminders: bool = True
    energy_level_tracking: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnergyManagement":
        """Create from dictionary."""
        return cls(
            interaction_frequency=data.get("interaction_frequency", "on-demand"),
            complexity_adaptation=data.get("complexity_adaptation", True),
            break_reminders=data.get("break_reminders", True),
            energy_level_tracking=data.get("energy_level_tracking", False),
        )


@dataclass
class CollaborationPreferences:
    """User's multi-agent collaboration preferences.
    
    Defines how multiple Advocates should coordinate
    when working together on user's behalf.
    """
    agent_coordination: str = "user-mediated"
    conflict_resolution: str = "user-decides"
    delegation_comfort: str = "simple-tasks"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CollaborationPreferences":
        """Create from dictionary."""
        return cls(
            agent_coordination=data.get("agent_coordination", "user-mediated"),
            conflict_resolution=data.get("conflict_resolution", "user-decides"),
            delegation_comfort=data.get("delegation_comfort", "simple-tasks"),
        )


@dataclass
class TOIPreferences:
    """Complete user TOI (Terms of Interaction) preferences.
    
    The user's personal interaction contract that all
    Advocates must honor when interacting with them.
    
    Attributes:
        version: Schema version for compatibility checking
        metadata: Document metadata (created, updated, author)
        communication: Communication style preferences
        cognitive: Cognitive accessibility preferences
        privacy: Privacy and data handling requirements
        energy_management: Energy and interaction management
        collaboration: Multi-agent collaboration preferences
        accessibility: Specific accessibility requirements
    """
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    communication: CommunicationPreferences = field(default_factory=CommunicationPreferences)
    cognitive: CognitivePreferences = field(default_factory=CognitivePreferences)
    privacy: PrivacyPreferences = field(default_factory=PrivacyPreferences)
    energy_management: EnergyManagement = field(default_factory=EnergyManagement)
    collaboration: CollaborationPreferences = field(default_factory=CollaborationPreferences)
    accessibility: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TOIPreferences":
        """Create TOIPreferences from a dictionary.
        
        Args:
            data: Dictionary containing TOI data, typically from JSON
            
        Returns:
            TOIPreferences instance with parsed values
        """
        return cls(
            version=data.get("version", "1.0.0"),
            metadata=data.get("metadata", {}),
            communication=CommunicationPreferences.from_dict(data.get("communication", {})),
            cognitive=CognitivePreferences.from_dict(data.get("cognitive", {})),
            privacy=PrivacyPreferences.from_dict(data.get("privacy", {})),
            energy_management=EnergyManagement.from_dict(data.get("energy_management", {})),
            collaboration=CollaborationPreferences.from_dict(data.get("collaboration", {})),
            accessibility=data.get("accessibility", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "version": self.version,
            "metadata": self.metadata,
            "communication": {
                "style": self.communication.style.value,
                "directness": self.communication.directness.value,
                "feedback_preference": self.communication.feedback_preference,
                "question_style": self.communication.question_style,
                "explanation_level": self.communication.explanation_level,
            },
            "cognitive": {
                "processing_time": self.cognitive.processing_time.value,
                "information_structure": self.cognitive.information_structure.value,
                "cognitive_load": self.cognitive.cognitive_load,
                "attention_span": self.cognitive.attention_span,
                "decision_support": self.cognitive.decision_support,
                "sensory_preferences": self.cognitive.sensory_preferences,
            },
            "privacy": {
                "data_retention": self.privacy.data_retention.value,
                "sharing_consent": self.privacy.sharing_consent.value,
                "anonymization": self.privacy.anonymization,
                "third_party_access": self.privacy.third_party_access,
                "audit_trail": self.privacy.audit_trail,
            },
            "energy_management": {
                "interaction_frequency": self.energy_management.interaction_frequency,
                "complexity_adaptation": self.energy_management.complexity_adaptation,
                "break_reminders": self.energy_management.break_reminders,
                "energy_level_tracking": self.energy_management.energy_level_tracking,
            },
            "collaboration": {
                "agent_coordination": self.collaboration.agent_coordination,
                "conflict_resolution": self.collaboration.conflict_resolution,
                "delegation_comfort": self.collaboration.delegation_comfort,
            },
            "accessibility": self.accessibility,
        }


class TOIParser:
    """Parses and validates TOI (Terms of Interaction) documents.
    
    TOI is the user's personal contract that defines how AI systems
    should interact with them. This parser ensures documents are valid
    and provides typed access to preferences.
    
    Example:
        >>> parser = TOIParser()
        >>> toi = parser.parse_file("my-preferences.json")
        >>> print(toi.communication.style)
        CommunicationStyle.FRIENDLY
        
    Neurodivergent-Friendly Features:
        - Clear, structured error messages
        - Helpful guidance on fixing validation issues
        - Sensible defaults for missing optional fields
    """

    def __init__(self, schema_path: Optional[Path] = None):
        """Initialize the TOI parser.
        
        Args:
            schema_path: Optional path to custom schema file.
                        Uses built-in schema if not provided.
        """
        self._schema: Optional[Dict[str, Any]] = None
        self._schema_path = schema_path
        
    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema for validation."""
        if self._schema is not None:
            return self._schema
            
        if self._schema_path is not None:
            with open(self._schema_path, 'r', encoding='utf-8') as f:
                self._schema = json.load(f)
        else:
            # Use the repository's schema
            repo_root = Path(__file__).parent.parent.parent
            schema_path = repo_root / "schemas" / "personal-toi.schema.json"
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    self._schema = json.load(f)
            else:
                # Minimal inline schema for standalone use
                self._schema = {
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "type": "object",
                    "required": ["version", "communication", "cognitive", "privacy"],
                }
        return self._schema

    def parse_file(self, file_path: Union[str, Path]) -> TOIPreferences:
        """Parse a TOI document from a file.
        
        Args:
            file_path: Path to the JSON TOI file
            
        Returns:
            Parsed TOIPreferences object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
            jsonschema.ValidationError: If document doesn't match schema
        """
        path = Path(file_path)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return self.parse(data)

    def parse(self, data: Dict[str, Any]) -> TOIPreferences:
        """Parse a TOI document from a dictionary.
        
        Args:
            data: Dictionary containing TOI data
            
        Returns:
            Parsed TOIPreferences object
            
        Raises:
            jsonschema.ValidationError: If document doesn't match schema
        """
        self.validate(data)
        return TOIPreferences.from_dict(data)

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate a TOI document against the schema.
        
        Args:
            data: Dictionary containing TOI data
            
        Returns:
            True if valid
            
        Raises:
            jsonschema.ValidationError: If validation fails
        """
        schema = self._load_schema()
        jsonschema.validate(data, schema)
        return True

    def is_valid(self, data: Dict[str, Any]) -> bool:
        """Check if a TOI document is valid without raising exceptions.
        
        Args:
            data: Dictionary containing TOI data
            
        Returns:
            True if valid, False otherwise
        """
        try:
            self.validate(data)
            return True
        except jsonschema.ValidationError:
            return False

    def get_validation_errors(self, data: Dict[str, Any]) -> List[str]:
        """Get user-friendly validation error messages.
        
        Provides clear, helpful error messages suitable for
        neurodivergent users who may find technical errors confusing.
        
        Args:
            data: Dictionary containing TOI data
            
        Returns:
            List of user-friendly error messages
        """
        schema = self._load_schema()
        validator = jsonschema.Draft202012Validator(schema)
        errors = []
        
        for error in validator.iter_errors(data):
            path = " → ".join(str(p) for p in error.absolute_path) if error.absolute_path else "document root"
            message = self._format_error_message(error, path)
            errors.append(message)
            
        return errors

    def _format_error_message(self, error: jsonschema.ValidationError, path: str) -> str:
        """Format a validation error into a user-friendly message.
        
        Args:
            error: The validation error
            path: Path to the error location
            
        Returns:
            User-friendly error message with guidance
        """
        base_message = f"📍 At '{path}': {error.message}"
        
        # Add helpful guidance based on error type
        if "required" in error.message.lower():
            guidance = "\n   💡 This field is required. Please add it to your TOI."
        elif "enum" in error.message.lower():
            guidance = "\n   💡 Please use one of the allowed values."
        elif "type" in error.message.lower():
            guidance = "\n   💡 Check the data type matches what's expected."
        else:
            guidance = ""
            
        return base_message + guidance

    def create_default(self) -> TOIPreferences:
        """Create a TOIPreferences with sensible defaults.
        
        Creates a privacy-first, neurodivergent-friendly default
        configuration that users can customize.
        
        Returns:
            TOIPreferences with default values
        """
        return TOIPreferences(
            version="1.0.0",
            metadata={
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "author": "default",
                "description": "Default TOI configuration",
            },
        )


__all__ = [
    "TOIParser",
    "TOIPreferences",
    "CommunicationStyle",
    "DirectnessLevel",
    "ProcessingTime",
    "InformationStructure",
    "DataRetention",
    "SharingConsent",
    "CommunicationPreferences",
    "CognitivePreferences",
    "PrivacyPreferences",
    "EnergyManagement",
    "CollaborationPreferences",
]
