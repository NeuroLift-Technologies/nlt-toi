"""OTOI (Orchestrated Terms of Interaction) Orchestrator.

Multi-agent coordination layer that enforces TOI across all agents,
tools, and handoffs. OTOI is the orchestration brain that ensures
consistency and compliance end-to-end.

Key Responsibilities:
    - Policy enforcement: Propagate TOI to every agent and tool
    - Handoff integrity: Preserve context, provenance, and user intent
    - Conflict resolution: Resolve policy clashes transparently
    - Observability: Log actions and maintain auditable trail

Neurodivergent-Friendly Design:
    - Transparent decision-making visible to user
    - User TOI always takes priority
    - Clear escalation paths when conflicts arise
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol
from uuid import uuid4

from .toi_parser import TOIPreferences


class AgentCapability(str, Enum):
    """Capabilities that agents can provide."""
    ATTENTION_SUPPORT = "attention-support"
    IMPULSE_MANAGEMENT = "impulse-management"
    TIME_MANAGEMENT = "time-management"
    MEMORY_SUPPORT = "memory-support"
    EMOTIONAL_REGULATION = "emotional-regulation"
    TASK_INITIATION = "task-initiation"
    PLANNING = "planning"
    FOCUS = "focus"
    SAFETY = "safety"
    GENERAL = "general"


class ConflictResolutionStrategy(str, Enum):
    """How to resolve conflicts between agents or preferences."""
    USER_TOI_FIRST = "user-toi-first"
    SAFETY_FIRST = "safety-first"
    EVIDENCE_BASED = "evidence-based"
    USER_DECIDES = "user-decides"
    CONSENSUS = "consensus"


class ContextSharingPolicy(str, Enum):
    """How context should be shared between agents."""
    FULL = "full"
    SELECTIVE = "selective"
    MINIMAL = "minimal"
    NONE = "none"


@dataclass
class AgentInfo:
    """Information about a registered agent.
    
    Agents register their capabilities so the orchestrator
    can route requests appropriately.
    """
    agent_id: str
    name: str
    capabilities: List[AgentCapability]
    description: str = ""
    priority: int = 0
    is_active: bool = True

    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability."""
        return capability in self.capabilities


@dataclass
class HandoffContext:
    """Context passed during agent handoffs.
    
    Preserves user intent and provenance across agent transitions.
    """
    handoff_id: str
    source_agent: Optional[str]
    target_agent: str
    user_intent: str
    toi_preferences: TOIPreferences
    shared_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    provenance: List[Dict[str, Any]] = field(default_factory=list)

    def add_provenance(self, agent_id: str, action: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add provenance entry for audit trail."""
        entry = {
            "agent_id": agent_id,
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        self.provenance.append(entry)


@dataclass
class CollaborationContext:
    """Context for multi-agent collaboration.
    
    Manages how agents work together while respecting
    user TOI and OTOI coordination rules.
    """
    collaboration_id: str
    participating_agents: List[str]
    user_toi: TOIPreferences
    context_sharing: ContextSharingPolicy
    conflict_resolution: ConflictResolutionStrategy
    shared_state: Dict[str, Any] = field(default_factory=dict)
    decision_log: List[Dict[str, Any]] = field(default_factory=list)

    def log_decision(
        self,
        agent_id: str,
        decision: str,
        rationale: str,
        toi_compliant: bool = True,
    ) -> None:
        """Log a decision for transparency and audit."""
        self.decision_log.append({
            "agent_id": agent_id,
            "decision": decision,
            "rationale": rationale,
            "toi_compliant": toi_compliant,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


@dataclass
class OrchestratorConfig:
    """Configuration for the OTOI Orchestrator.
    
    Defines the coordination rules for multi-agent collaboration.
    """
    context_sharing: ContextSharingPolicy = ContextSharingPolicy.SELECTIVE
    conflict_resolution: ConflictResolutionStrategy = ConflictResolutionStrategy.USER_TOI_FIRST
    handoff_logging: bool = True
    provenance_tracking: bool = True
    max_concurrent_agents: int = 5


class AgentProtocol(Protocol):
    """Protocol that agents must implement for orchestration.
    
    Agents registered with the OTOI Orchestrator should implement
    this protocol for proper lifecycle management and coordination.
    """
    
    @property
    def agent_id(self) -> str:
        """Unique identifier for the agent."""
        ...
    
    async def initialize(self) -> None:
        """Initialize the agent before first use.
        
        Called when the agent is first registered or reactivated.
        Use for resource allocation, connection setup, etc.
        """
        ...
    
    async def shutdown(self) -> None:
        """Clean up agent resources before removal.
        
        Called when the agent is unregistered or system shuts down.
        Use for cleanup, saving state, closing connections, etc.
        """
        ...
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status.
        
        Returns:
            Dictionary with status information (health, metrics, etc.)
        """
        ...
    
    async def process(
        self,
        user_input: str,
        context: HandoffContext,
    ) -> Dict[str, Any]:
        """Process user input with given context.
        
        Args:
            user_input: The user's input/request
            context: Handoff context with TOI and provenance
            
        Returns:
            Response dictionary with agent's output
        """
        ...


class OTOIOrchestrator:
    """Orchestrates multiple agents under TOI governance.
    
    The OTOI Orchestrator coordinates agents to ensure they:
    - Honor user TOI preferences in all interactions
    - Share context appropriately between agents
    - Resolve conflicts transparently
    - Maintain provenance for auditability
    
    Example:
        >>> orchestrator = OTOIOrchestrator(config)
        >>> orchestrator.register_agent(my_agent_info)
        >>> context = await orchestrator.create_collaboration(user_toi, agents)
        >>> result = await orchestrator.dispatch(agent_id, user_input, context)
        
    OTOI Priority Order (when conflicts arise):
        1. User TOI preferences
        2. Safety constraints
        3. Evidence-based decisions
        4. Efficiency considerations
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """Initialize the orchestrator.
        
        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self.config = config or OrchestratorConfig()
        self._agents: Dict[str, AgentInfo] = {}
        self._agent_instances: Dict[str, AgentProtocol] = {}
        self._handoff_log: List[HandoffContext] = []
        self._active_collaborations: Dict[str, CollaborationContext] = {}

    def register_agent(
        self,
        agent_info: AgentInfo,
        agent_instance: Optional[AgentProtocol] = None,
    ) -> None:
        """Register an agent with the orchestrator.
        
        Args:
            agent_info: Information about the agent's capabilities
            agent_instance: Optional agent instance for direct dispatch
            
        Raises:
            ValueError: If agent with same ID already registered
        """
        if agent_info.agent_id in self._agents:
            raise ValueError(f"Agent '{agent_info.agent_id}' already registered")
        self._agents[agent_info.agent_id] = agent_info
        if agent_instance is not None:
            self._agent_instances[agent_info.agent_id] = agent_instance

    def unregister_agent(self, agent_id: str) -> None:
        """Remove an agent from the orchestrator.
        
        Args:
            agent_id: ID of agent to remove
        """
        self._agents.pop(agent_id, None)
        self._agent_instances.pop(agent_id, None)

    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get information about a registered agent.
        
        Args:
            agent_id: ID of agent to look up
            
        Returns:
            AgentInfo if found, None otherwise
        """
        return self._agents.get(agent_id)

    def list_agents(
        self,
        capability: Optional[AgentCapability] = None,
        active_only: bool = True,
    ) -> List[AgentInfo]:
        """List registered agents, optionally filtered.
        
        Args:
            capability: Filter by specific capability
            active_only: Only return active agents
            
        Returns:
            List of matching agents
        """
        agents = list(self._agents.values())
        
        if active_only:
            agents = [a for a in agents if a.is_active]
            
        if capability is not None:
            agents = [a for a in agents if a.has_capability(capability)]
            
        return sorted(agents, key=lambda a: a.priority, reverse=True)

    def select_agents(
        self,
        user_input: str,
        toi: TOIPreferences,
        required_capabilities: Optional[List[AgentCapability]] = None,
    ) -> List[AgentInfo]:
        """Select appropriate agents for a task based on TOI.
        
        Respects user's delegation comfort and agent coordination
        preferences from their TOI.
        
        Args:
            user_input: The user's request
            toi: User's TOI preferences
            required_capabilities: Specific capabilities needed
            
        Returns:
            List of suitable agents, respecting TOI limits
        """
        # Respect delegation comfort level
        delegation = toi.collaboration.delegation_comfort
        if delegation == "none":
            return []
            
        agents = self.list_agents(active_only=True)
        
        # Filter by required capabilities
        if required_capabilities:
            agents = [
                a for a in agents
                if any(a.has_capability(cap) for cap in required_capabilities)
            ]
        
        # Limit based on coordination preference
        coordination = toi.collaboration.agent_coordination
        if coordination == "centralized":
            # Return single best agent
            return agents[:1] if agents else []
        elif coordination == "user-mediated":
            # Return limited set for user to choose
            return agents[:3]
        else:
            # Distributed or autonomous - return all suitable
            return agents[:self.config.max_concurrent_agents]

    async def create_collaboration(
        self,
        toi: TOIPreferences,
        agent_ids: List[str],
    ) -> CollaborationContext:
        """Create a new collaboration context for multiple agents.
        
        Args:
            toi: User's TOI preferences to govern the collaboration
            agent_ids: IDs of agents participating
            
        Returns:
            CollaborationContext for the agents to use
        """
        # Map user preferences to OTOI settings
        conflict_strategy = self._map_conflict_resolution(toi)
        
        context = CollaborationContext(
            collaboration_id=f"collab-{uuid4().hex[:8]}",
            participating_agents=agent_ids,
            user_toi=toi,
            context_sharing=self.config.context_sharing,
            conflict_resolution=conflict_strategy,
        )
        
        self._active_collaborations[context.collaboration_id] = context
        return context

    def _map_conflict_resolution(self, toi: TOIPreferences) -> ConflictResolutionStrategy:
        """Map user's conflict resolution preference to strategy."""
        user_pref = toi.collaboration.conflict_resolution
        mapping = {
            "user-decides": ConflictResolutionStrategy.USER_DECIDES,
            "consensus": ConflictResolutionStrategy.CONSENSUS,
            "priority-based": ConflictResolutionStrategy.USER_TOI_FIRST,
            "expertise-weighted": ConflictResolutionStrategy.EVIDENCE_BASED,
        }
        return mapping.get(user_pref, ConflictResolutionStrategy.USER_TOI_FIRST)

    def create_handoff(
        self,
        source_agent: Optional[str],
        target_agent: str,
        user_intent: str,
        toi: TOIPreferences,
        context: Optional[Dict[str, Any]] = None,
    ) -> HandoffContext:
        """Create a handoff context for agent transition.
        
        Args:
            source_agent: Agent handing off (None if user-initiated)
            target_agent: Agent receiving the handoff
            user_intent: The user's original intent
            toi: User's TOI preferences
            context: Optional shared context
            
        Returns:
            HandoffContext for the transition
        """
        handoff = HandoffContext(
            handoff_id=f"handoff-{uuid4().hex[:8]}",
            source_agent=source_agent,
            target_agent=target_agent,
            user_intent=user_intent,
            toi_preferences=toi,
            shared_context=context or {},
        )
        
        if self.config.handoff_logging:
            self._handoff_log.append(handoff)
            
        return handoff

    async def dispatch(
        self,
        agent_id: str,
        user_input: str,
        handoff: HandoffContext,
    ) -> Dict[str, Any]:
        """Dispatch a request to an agent.
        
        Ensures the agent receives proper context and TOI.
        
        Args:
            agent_id: Target agent ID
            user_input: User's input
            handoff: Handoff context with TOI and provenance
            
        Returns:
            Agent's response
            
        Raises:
            ValueError: If agent not found or not active
        """
        agent_info = self._agents.get(agent_id)
        if not agent_info:
            raise ValueError(f"Agent '{agent_id}' not registered")
        if not agent_info.is_active:
            raise ValueError(f"Agent '{agent_id}' is not active")
            
        agent_instance = self._agent_instances.get(agent_id)
        if not agent_instance:
            raise ValueError(f"No instance registered for agent '{agent_id}'")
        
        # Add provenance for the dispatch
        if self.config.provenance_tracking:
            handoff.add_provenance(
                agent_id=agent_id,
                action="dispatch",
                metadata={"input_length": len(user_input)},
            )
        
        # Dispatch to agent
        result = await agent_instance.process(user_input, handoff)
        
        # Log completion
        if self.config.provenance_tracking:
            handoff.add_provenance(
                agent_id=agent_id,
                action="complete",
                metadata={"has_response": bool(result)},
            )
            
        return result

    def log_interaction(
        self,
        collaboration_id: str,
        agent_id: str,
        decision: str,
        rationale: str,
        toi_compliant: bool = True,
    ) -> None:
        """Log an interaction decision for transparency.
        
        Part of the OTOI observability layer - maintains
        audit trail for user review.
        
        Args:
            collaboration_id: The collaboration context
            agent_id: Agent making the decision
            decision: What was decided
            rationale: Why it was decided
            toi_compliant: Whether decision honors user TOI
        """
        context = self._active_collaborations.get(collaboration_id)
        if context:
            context.log_decision(
                agent_id=agent_id,
                decision=decision,
                rationale=rationale,
                toi_compliant=toi_compliant,
            )

    def get_handoff_history(self) -> List[HandoffContext]:
        """Get the handoff history for audit purposes.
        
        Returns:
            List of all handoffs (oldest first)
        """
        return list(self._handoff_log)

    def get_decision_log(self, collaboration_id: str) -> List[Dict[str, Any]]:
        """Get the decision log for a collaboration.
        
        Args:
            collaboration_id: The collaboration to query
            
        Returns:
            List of decision entries
        """
        context = self._active_collaborations.get(collaboration_id)
        return list(context.decision_log) if context else []


__all__ = [
    "OTOIOrchestrator",
    "OrchestratorConfig",
    "AgentInfo",
    "AgentCapability",
    "HandoffContext",
    "CollaborationContext",
    "ConflictResolutionStrategy",
    "ContextSharingPolicy",
    "AgentProtocol",
]
