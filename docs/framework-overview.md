# TOI-OTOI Framework Definition

NeuroLift OTOI Framework: User-defined Terms of Interaction for AI systems. Enables neurodivergent-friendly multi-agent orchestration with privacy-first governance. Open standard for human-controlled AI collaboration.

> Framework description contributed by Joshua Dorsey

## 🎯 TOI-OTOI Framework Deep Dive

**TOI — OTOI: Terms of Interaction — Orchestrated Terms of Interaction**

## Revolutionary Concept

The TOI‑OTOI framework defines how users and AI interact and how those interactions are orchestrated across multiple agents. This framework represents the core governance and orchestration architecture that will power the NeuroLift MVP.

## Framework Philosophy

### TOI (Terms of Interaction)

Governance schema that lets a person define boundaries, preferences, and operational parameters for AI interactions. TOI functions as a user-authored "constitution" that agents must honor.

- Consent and boundaries: What data can be used, when to ask, when to stop
- Communication preferences: tone, pace, modality, and structure
- Safety and privacy rules: red lines, escalation paths, and auditability
- Accessibility clauses: ADHD-friendly patterns like progressive disclosure, chunking, and predictable navigation

### OTOI (Orchestrated Terms of Interaction)

Multi-agent coordination layer that enforces TOI across all agents, tools, and handoffs. OTOI is the orchestration brain that ensures consistency and compliance end-to-end.

- Policy enforcement: propagate TOI to every agent and tool
- Handoff integrity: preserve context, provenance, and user intent across steps
- Conflict resolution: resolve policy clashes and surface decisions transparently
- Observability: log actions, provide explanations, and maintain an auditable trail

### Layer 1: Intelligence Recognition

- User behavior pattern identification
- Cognitive style assessment algorithms
- Strength and challenge mapping
- Preference learning systems

### Layer 2: Organizational Structure

- Task decomposition algorithms
- Priority matrix generation
- Resource allocation optimization
- Timeline management systems

### Layer 3: Optimization Engine

- Performance metric tracking
- Adaptive algorithm adjustment
- Efficiency improvement recommendations
- Outcome prediction modeling

### Layer 4: Integration Interface

- User experience optimization
- Multi-system coordination
- Feedback loop management
- Continuous improvement cycles

## MVP Integration Strategy

The TOI-OTOI framework will serve as the core intelligence layer within the NeuroLift MVP:

1. **Intelligent Task Management**: Automated organization and prioritization
2. **Adaptive Learning Support**: Personalized educational pathways
3. **Cognitive Load Optimization**: Balanced information processing
4. **Performance Enhancement**: Continuous improvement recommendations

## Python Implementation

The TOI-OTOI framework includes a Python implementation in `/src/fusion/` with three core components:

### TOIParser

Parses and validates user TOI documents, providing typed access to preferences:

```python
from src.fusion import TOIParser

parser = TOIParser()

# Parse a TOI file
toi = parser.parse_file("my-preferences.json")

# Access typed preferences
print(toi.communication.style)        # CommunicationStyle.FRIENDLY
print(toi.cognitive.processing_time)  # ProcessingTime.MODERATE
print(toi.privacy.data_retention)     # DataRetention.SESSION_ONLY

# Validate with helpful error messages
errors = parser.get_validation_errors(data)
```

### OTOIOrchestrator

Coordinates multiple agents under TOI governance:

```python
from src.fusion import OTOIOrchestrator
from src.fusion.otoi_orchestrator import AgentInfo, AgentCapability

orchestrator = OTOIOrchestrator()

# Register agents with capabilities
agent = AgentInfo(
    agent_id="focus-agent",
    name="Focus Support",
    capabilities=[AgentCapability.ATTENTION_SUPPORT],
)
orchestrator.register_agent(agent)

# Select agents based on user TOI
agents = orchestrator.select_agents(user_input, toi)

# Create collaboration with TOI governance
context = await orchestrator.create_collaboration(toi, agent_ids)
```

### PrivacyGuardian

Enforces privacy-first architecture with local-only processing:

```python
from src.fusion import PrivacyGuardian

guardian = PrivacyGuardian(toi)

# Check if processing is allowed
if guardian.can_process(ProcessingLocation.LOCAL, DataCategory.PERSONAL):
    # Process data locally
    item_id = guardian.register_data(DataCategory.PERSONAL)
    guardian.log_access(item_id, "focus-agent", "analysis")

# Request explicit consent for sharing
consent_id = guardian.request_consent(
    purpose="research",
    data_categories=[DataCategory.ANONYMOUS],
    recipient="research-team"
)
```

## Development Roadmap

### Phase 1: Framework Specification (100% Complete)

- Core principles documentation
- Technical architecture design
- Integration planning
- Python implementation of TOI-OTOI governance

### Phase 2: Prototype Development (In Progress)

- Proof-of-concept implementation
- Initial testing framework
- Performance validation

### Phase 3: MVP Integration (Scheduled)

- Full system integration
- AI Personas architecture alignment
- User testing and validation

### Phase 4: Optimization (Future)

- Performance refinement
- Feature enhancement
- Scalability improvements

## Innovation Impact

The TOI-OTOI framework represents a paradigm shift in neurodivergent support technology:

- **Personalized Intelligence**: Adapts to individual cognitive patterns
- **Predictive Support**: Anticipates user needs before they arise
- **Continuous Evolution**: Improves through use and feedback
- **Holistic Integration**: Seamlessly connects all system components

---

*This framework embodies a year of collaborative development and represents the innovative foundation of NeuroLift Technologies' approach to empowering neurodivergent individuals.*
