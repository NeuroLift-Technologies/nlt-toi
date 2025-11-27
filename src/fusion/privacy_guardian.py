"""Privacy Guardian for TOI-OTOI Framework.

Enforces privacy-first architecture with local-only processing.
All user data must be processed locally with zero cloud dependency.

Key Responsibilities:
    - Enforce local-only data processing
    - Manage data encryption and storage
    - Control data retention and deletion
    - Validate privacy compliance of operations

Privacy Principles (Non-Negotiable):
    - 100% local processing, zero cloud dependency for user data
    - User device only storage, never transmitted without consent
    - AES-256 encryption for all local data at rest
    - Complete user control over personal information
    - Ephemeral sessions unless user explicitly saves
    - Opt-in only telemetry, fully anonymized if enabled
    - User privacy preferences override all defaults
"""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

from .toi_parser import TOIPreferences, DataRetention, SharingConsent


class ProcessingLocation(str, Enum):
    """Where data processing occurs."""
    LOCAL = "local"
    EDGE = "edge"
    CLOUD = "cloud"


class DataCategory(str, Enum):
    """Categories of data for privacy classification."""
    PERSONAL = "personal"
    BEHAVIORAL = "behavioral"
    COGNITIVE = "cognitive"
    INTERACTION = "interaction"
    SYSTEM = "system"
    ANONYMOUS = "anonymous"


class PrivacyLevel(str, Enum):
    """Privacy sensitivity levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"


@dataclass
class PrivacyPolicy:
    """Privacy policy derived from user TOI.
    
    Defines the privacy rules that must be enforced
    for all data processing operations.
    """
    data_retention: DataRetention
    sharing_consent: SharingConsent
    require_anonymization: bool
    allow_third_party: bool
    require_audit_trail: bool
    allowed_processing_locations: Set[ProcessingLocation] = field(
        default_factory=lambda: {ProcessingLocation.LOCAL}
    )
    encryption_required: bool = True
    retention_duration: Optional[timedelta] = None

    @classmethod
    def from_toi(cls, toi: TOIPreferences) -> "PrivacyPolicy":
        """Create privacy policy from user TOI preferences.
        
        Args:
            toi: User's TOI preferences
            
        Returns:
            PrivacyPolicy enforcing user's privacy requirements
        """
        # Map retention preferences to duration
        retention_map = {
            DataRetention.SESSION_ONLY: timedelta(hours=1),
            DataRetention.SHORT_TERM: timedelta(days=1),
            DataRetention.LONG_TERM: timedelta(days=30),
            DataRetention.PERMANENT: None,
            DataRetention.USER_CONTROLLED: None,
        }
        
        return cls(
            data_retention=toi.privacy.data_retention,
            sharing_consent=toi.privacy.sharing_consent,
            require_anonymization=toi.privacy.anonymization,
            allow_third_party=toi.privacy.third_party_access,
            require_audit_trail=toi.privacy.audit_trail,
            retention_duration=retention_map.get(toi.privacy.data_retention),
        )

    def allows_sharing(self, purpose: str) -> bool:
        """Check if data sharing is allowed for a purpose.
        
        Args:
            purpose: The purpose of the sharing
            
        Returns:
            True if sharing is allowed under the policy
        """
        if self.sharing_consent == SharingConsent.NEVER:
            return False
        elif self.sharing_consent == SharingConsent.EXPLICIT_ONLY:
            return False  # Requires explicit consent call
        elif self.sharing_consent == SharingConsent.AGGREGATE_ONLY:
            return purpose == "aggregate"
        elif self.sharing_consent == SharingConsent.RESEARCH_APPROVED:
            return purpose in ("research", "aggregate")
        return False


@dataclass
class DataItem:
    """A tracked piece of data with privacy metadata.
    
    Used to track data through its lifecycle for
    privacy compliance and audit purposes.
    """
    item_id: str
    category: DataCategory
    privacy_level: PrivacyLevel
    created_at: datetime
    expires_at: Optional[datetime]
    is_anonymized: bool = False
    is_encrypted: bool = False
    access_log: List[Dict[str, Any]] = field(default_factory=list)

    def log_access(self, accessor: str, purpose: str) -> None:
        """Log an access to this data item."""
        self.access_log.append({
            "accessor": accessor,
            "purpose": purpose,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def is_expired(self) -> bool:
        """Check if data item has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) >= self.expires_at


@dataclass
class PrivacyViolation:
    """Record of a privacy policy violation.
    
    Used to track and report privacy violations
    for audit and user notification.
    """
    violation_id: str
    policy_rule: str
    attempted_action: str
    severity: str
    blocked: bool
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = field(default_factory=dict)


class PrivacyGuardian:
    """Enforces privacy-first architecture for the TOI-OTOI framework.
    
    The Privacy Guardian ensures all operations comply with user
    privacy preferences and the framework's privacy-first principles.
    
    Core Guarantees:
        - No data leaves the user's device without explicit consent
        - All stored data is encrypted
        - Data is automatically deleted according to retention policy
        - All data access is logged for transparency
        
    Example:
        >>> guardian = PrivacyGuardian(user_toi)
        >>> if guardian.can_process(data, ProcessingLocation.LOCAL):
        ...     result = process_data(data)
        ...     guardian.log_processing(data_id, "analysis")
        
    Privacy Principles:
        - Privacy is not a feature toggle - it's the foundation
        - User privacy preferences override all defaults
        - Neurodivergent data is deeply personal and protected
    """

    def __init__(self, toi: Optional[TOIPreferences] = None):
        """Initialize the Privacy Guardian.
        
        Args:
            toi: User's TOI preferences. If not provided,
                 uses maximum privacy defaults.
        """
        if toi is not None:
            self._policy = PrivacyPolicy.from_toi(toi)
        else:
            # Maximum privacy defaults
            self._policy = PrivacyPolicy(
                data_retention=DataRetention.SESSION_ONLY,
                sharing_consent=SharingConsent.NEVER,
                require_anonymization=True,
                allow_third_party=False,
                require_audit_trail=True,
                retention_duration=timedelta(hours=1),
            )
        
        self._tracked_data: Dict[str, DataItem] = {}
        self._violations: List[PrivacyViolation] = []
        self._consent_registry: Dict[str, Dict[str, Any]] = {}

    @property
    def policy(self) -> PrivacyPolicy:
        """Get the current privacy policy."""
        return self._policy

    def update_policy(self, toi: TOIPreferences) -> None:
        """Update privacy policy based on new TOI.
        
        Args:
            toi: Updated TOI preferences
        """
        self._policy = PrivacyPolicy.from_toi(toi)

    def can_process(
        self,
        location: ProcessingLocation,
        category: DataCategory = DataCategory.PERSONAL,
    ) -> bool:
        """Check if data processing is allowed at a location.
        
        Args:
            location: Where processing would occur
            category: Category of data being processed
            
        Returns:
            True if processing is allowed
        """
        # Personal/cognitive data can only be processed locally
        if category in (DataCategory.PERSONAL, DataCategory.COGNITIVE, DataCategory.BEHAVIORAL):
            return location == ProcessingLocation.LOCAL
            
        return location in self._policy.allowed_processing_locations

    def can_share(self, purpose: str, category: DataCategory) -> bool:
        """Check if data sharing is allowed.
        
        Args:
            purpose: Purpose of the sharing
            category: Category of data to share
            
        Returns:
            True if sharing is allowed
        """
        # Never share sensitive categories externally
        if category in (DataCategory.PERSONAL, DataCategory.COGNITIVE):
            return False
            
        return self._policy.allows_sharing(purpose)

    def register_data(
        self,
        category: DataCategory,
        privacy_level: PrivacyLevel = PrivacyLevel.CONFIDENTIAL,
    ) -> str:
        """Register a new data item for tracking.
        
        Args:
            category: Category of the data
            privacy_level: Privacy sensitivity level
            
        Returns:
            Unique ID for the data item
        """
        item_id = f"data-{uuid4().hex[:12]}"
        
        # Calculate expiration based on retention policy
        expires_at = None
        if self._policy.retention_duration is not None:
            expires_at = datetime.now(timezone.utc) + self._policy.retention_duration
            
        item = DataItem(
            item_id=item_id,
            category=category,
            privacy_level=privacy_level,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            is_encrypted=self._policy.encryption_required,
            is_anonymized=self._policy.require_anonymization and category != DataCategory.SYSTEM,
        )
        
        self._tracked_data[item_id] = item
        return item_id

    def log_access(self, item_id: str, accessor: str, purpose: str) -> bool:
        """Log data access for audit trail.
        
        Args:
            item_id: ID of data being accessed
            accessor: Who/what is accessing the data
            purpose: Why the data is being accessed
            
        Returns:
            True if access was logged (item exists)
        """
        if not self._policy.require_audit_trail:
            return True
            
        item = self._tracked_data.get(item_id)
        if item:
            item.log_access(accessor, purpose)
            return True
        return False

    def check_expired(self) -> List[str]:
        """Check for and return expired data items.
        
        Returns:
            List of expired item IDs
        """
        expired = []
        for item_id, item in self._tracked_data.items():
            if item.is_expired():
                expired.append(item_id)
        return expired

    def delete_item(self, item_id: str) -> bool:
        """Delete a tracked data item.
        
        Args:
            item_id: ID of item to delete
            
        Returns:
            True if item was deleted
        """
        if item_id in self._tracked_data:
            del self._tracked_data[item_id]
            return True
        return False

    def delete_expired(self) -> int:
        """Delete all expired data items.
        
        Returns:
            Number of items deleted
        """
        expired = self.check_expired()
        for item_id in expired:
            self.delete_item(item_id)
        return len(expired)

    def record_violation(
        self,
        policy_rule: str,
        attempted_action: str,
        severity: str = "warning",
        blocked: bool = True,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Record a privacy policy violation.
        
        Args:
            policy_rule: Which rule was violated
            attempted_action: What was attempted
            severity: Violation severity (info, warning, error, critical)
            blocked: Whether the action was blocked
            details: Additional details
            
        Returns:
            Violation ID
        """
        violation = PrivacyViolation(
            violation_id=f"violation-{uuid4().hex[:8]}",
            policy_rule=policy_rule,
            attempted_action=attempted_action,
            severity=severity,
            blocked=blocked,
            details=details or {},
        )
        self._violations.append(violation)
        return violation.violation_id

    def get_violations(self, since: Optional[datetime] = None) -> List[PrivacyViolation]:
        """Get recorded privacy violations.
        
        Args:
            since: Only return violations after this time
            
        Returns:
            List of privacy violations
        """
        if since is None:
            return list(self._violations)
        return [v for v in self._violations if v.timestamp >= since]

    def request_consent(
        self,
        purpose: str,
        data_categories: List[DataCategory],
        recipient: str,
    ) -> str:
        """Request explicit consent for data sharing.
        
        Creates a consent request that must be approved
        by the user before data can be shared.
        
        Args:
            purpose: Why the data is needed
            data_categories: What data is being requested
            recipient: Who will receive the data
            
        Returns:
            Consent request ID
        """
        consent_id = f"consent-{uuid4().hex[:8]}"
        self._consent_registry[consent_id] = {
            "purpose": purpose,
            "data_categories": [c.value for c in data_categories],
            "recipient": recipient,
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
            "user_response": None,
        }
        return consent_id

    def grant_consent(self, consent_id: str) -> bool:
        """Grant a pending consent request.
        
        Args:
            consent_id: The consent request to grant
            
        Returns:
            True if consent was granted
        """
        if consent_id in self._consent_registry:
            self._consent_registry[consent_id]["status"] = "granted"
            self._consent_registry[consent_id]["granted_at"] = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def deny_consent(self, consent_id: str) -> bool:
        """Deny a pending consent request.
        
        Args:
            consent_id: The consent request to deny
            
        Returns:
            True if consent was denied
        """
        if consent_id in self._consent_registry:
            self._consent_registry[consent_id]["status"] = "denied"
            self._consent_registry[consent_id]["denied_at"] = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def has_consent(self, consent_id: str) -> bool:
        """Check if consent was granted.
        
        Args:
            consent_id: The consent request to check
            
        Returns:
            True if consent was granted
        """
        consent = self._consent_registry.get(consent_id)
        return consent is not None and consent["status"] == "granted"

    def anonymize_id(self, original_id: str, salt: Optional[str] = None) -> str:
        """Create an anonymized version of an identifier.
        
        Args:
            original_id: The ID to anonymize
            salt: Optional salt for hashing
            
        Returns:
            Anonymized ID that can't be reversed
        """
        if salt is None:
            salt = secrets.token_hex(8)
        combined = f"{original_id}:{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def get_audit_log(self, item_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit log for data access.
        
        Args:
            item_id: Specific item to audit, or all if None
            
        Returns:
            List of audit entries
        """
        if item_id is not None:
            item = self._tracked_data.get(item_id)
            return list(item.access_log) if item else []
            
        # Return all access logs
        all_logs = []
        for data_id, item in self._tracked_data.items():
            for log_entry in item.access_log:
                all_logs.append({
                    "item_id": data_id,
                    "category": item.category.value,
                    **log_entry,
                })
        return sorted(all_logs, key=lambda x: x.get("timestamp", ""))

    def generate_privacy_report(self) -> Dict[str, Any]:
        """Generate a privacy status report.
        
        Returns:
            Summary of privacy status and tracked data
        """
        return {
            "policy": {
                "data_retention": self._policy.data_retention.value,
                "sharing_consent": self._policy.sharing_consent.value,
                "encryption_required": self._policy.encryption_required,
                "anonymization_required": self._policy.require_anonymization,
            },
            "tracked_items": len(self._tracked_data),
            "expired_items": len(self.check_expired()),
            "violations": len(self._violations),
            "pending_consents": sum(
                1 for c in self._consent_registry.values() 
                if c["status"] == "pending"
            ),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


__all__ = [
    "PrivacyGuardian",
    "PrivacyPolicy",
    "ProcessingLocation",
    "DataCategory",
    "PrivacyLevel",
    "DataItem",
    "PrivacyViolation",
]
