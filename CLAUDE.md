# CLAUDE.md - AI Assistant Guide for nlt-otoi Repository

**Repository**: JDUB1216/nlt-otoi
**Purpose**: NeuroLift OTOI Framework - Open standard for user-controlled AI interaction
**Last Updated**: 2025-11-27
**Intended Audience**: Claude, Claude Code, and other AI assistants working with this codebase

---

## EXECUTIVE SUMMARY

You are working in the **NeuroLift OTOI (Orchestrated Terms of Interaction) Framework** repository. This is an open-source project that defines standards for neurodivergent-friendly, privacy-first, user-controlled AI interactions. The repository contains JSON schemas, documentation, templates, and reference implementations for the TOI-OTOI governance framework.

**Mission**: Enable users (especially neurodivergent individuals) to define exactly how AI systems should interact with them, ensuring respectful, accessible, and privacy-preserving AI collaboration.

### Core Principles (Non-Negotiable)

1. **User Control**: Users define interaction terms, AI systems respect them
2. **Neurodivergent-Friendly**: Built for diverse cognitive needs from the ground up
3. **Privacy-First**: User data stays under user control, local by default
4. **Open Standard**: No vendor lock-in, community-driven development
5. **User Agency**: Every design decision preserves user autonomy

---

## REPOSITORY STRUCTURE

```
nlt-otoi/
├── schemas/                          # JSON Schema definitions (JSON Schema draft 2020-12)
│   ├── personal-toi.schema.json     # Individual user interaction preferences
│   └── collaborative-charter.schema.json  # Group/team interaction protocols
│
├── templates/                        # User-friendly templates (Markdown)
│   ├── personal-toi-template.md     # Template for creating personal TOI
│   ├── collaborative-charter-template.md  # Template for team charters
│   └── quick-start-template.md      # Quick start guide for new users
│
├── examples/                         # Real-world examples and reference implementations
│   ├── neurodivergent-examples/     # ADHD, autism, and other neurodivergent TOI examples
│   │   └── adhd-student-example.json
│   ├── team-collaboration/          # Collaborative charter examples
│   │   └── remote-dev-team-charter.json
│   └── neuroLift/                   # Python reference implementation
│       ├── context_capsule.py       # Context management primitives
│       ├── intent_ledger.py         # Intent tracking and provenance
│       ├── orchestrator_patterns.py # Multi-agent coordination patterns
│       └── playbook_engine.py       # Decision playbook execution
│
├── docs/                            # Comprehensive documentation
│   ├── framework-overview.md        # Deep dive into TOI-OTOI philosophy and architecture
│   ├── implementation-guide.md      # Technical guide for developers implementing OTOI
│   ├── best-practices.md            # Best practices for users and developers
│   └── neurolift-integration.md     # Integration with NeuroLift platform
│
├── nlt-otoi/                        # Nested project structure (additional tooling)
│   ├── schemas/v1.0/               # Versioned schema definitions
│   ├── tools/
│   │   ├── generators/             # TOI document generation tools
│   │   │   └── toi-generator.py
│   │   └── validators/             # Schema validation tools
│   │       └── toi-validator.py
│   ├── templates/
│   │   ├── personal-toi/           # Additional TOI templates
│   │   └── custom-instructions/    # AI system custom instructions
│   │       └── cursor-instructions.md
│   └── docs/                       # Additional documentation
│       ├── guides/                 # User guides and quick-start materials
│       ├── accessibility/          # Neurodivergent support documentation
│       └── technical-specs/        # Technical specifications
│
├── .github/                         # GitHub configuration
│   └── ISSUE_TEMPLATE/             # Issue templates for bug reports, features, etc.
│
├── GEMINI_TOPOGRAPHY.py            # Repository navigation and structure guide
├── README.md                        # Project overview and quick start
├── CONTRIBUTING.md                  # Contribution guidelines
├── LICENSE                          # MIT License
└── .gitignore                       # Git ignore patterns
```

### Important Note on Nested Structure

This repository contains a nested `nlt-otoi/` directory with duplicated and extended structure. When working on the codebase:

- **Root level** (`/schemas/`, `/templates/`, `/docs/`, `/examples/`): Primary working files and current implementations
- **Nested level** (`/nlt-otoi/`): Additional tooling, versioned schemas, and extended examples
- **Coordinate between both**: Some files exist in both locations - check timestamps and context to determine canonical version

---

## KEY CONCEPTS

### TOI (Terms of Interaction)

A **Personal TOI** is a user-authored document that defines how AI systems should interact with that individual:

```json
{
  "version": "1.0.0",
  "metadata": { "author": "user-identifier", "created": "2024-01-15T10:00:00Z" },
  "communication": {
    "style": "friendly",              // formal, casual, professional, friendly, adaptive
    "directness": "direct",           // very-direct, direct, moderate, indirect
    "explanation_level": "detailed"   // minimal, concise, detailed, comprehensive
  },
  "cognitive": {
    "processing_time": "moderate",    // immediate, short, moderate, extended, flexible
    "information_structure": "bullet-points",  // linear, hierarchical, visual, bullet-points
    "attention_span": "short-bursts"  // short-bursts, focused-sessions, continuous
  },
  "privacy": {
    "data_retention": "short-term",   // session-only, short-term, long-term, permanent
    "sharing_consent": "never"        // never, explicit-only, aggregate-only
  }
}
```

**Reference**: `/schemas/personal-toi.schema.json` for complete schema definition

### OTOI (Orchestrated Terms of Interaction)

**Multi-agent coordination layer** that enforces individual TOIs across multiple AI agents:

- **Policy Enforcement**: Propagate user TOI to all agents and tools
- **Handoff Integrity**: Preserve context and provenance across agent handoffs
- **Conflict Resolution**: Resolve policy clashes transparently
- **Observability**: Maintain auditable trail of all agent actions

**Reference**: `/examples/neuroLift/orchestrator_patterns.py` for implementation patterns

### Framework Layers

```
┌─────────────────────────────────────────────────────────┐
│  User Interface (User defines TOI preferences)          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  TOI Parser (Read and validate user preferences)        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  OTOI Orchestrator (Multi-agent coordination)           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  AI Agents (TOI-compliant responses)                    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  Privacy Layer (Local processing, user data sovereignty)│
└─────────────────────────────────────────────────────────┘
```

---

## TECHNOLOGY STACK

### Languages & Formats

- **Python 3.8+**: Reference implementations, tools, and validators
- **JSON Schema (draft 2020-12)**: Schema validation and type definitions
- **Markdown**: Documentation and templates
- **YAML**: Configuration files (in nested `nlt-otoi/` structure)
- **JSON**: Schema files and example documents

### Python Dependencies

Key packages used in reference implementations (see examples):

```python
# Core Python features used
from __future__ import annotations
import asyncio              # Async/await patterns for agent coordination
from dataclasses import dataclass, field  # Structured data
from datetime import datetime, timezone   # Timestamp handling
from typing import Protocol, Optional, Dict, List, Any, Callable, Awaitable
from uuid import uuid4      # Unique identifier generation
```

No external dependencies in core schemas - intentionally minimal for broad adoption.

### Validation Standards

- **JSON Schema Version**: `https://json-schema.org/draft/2020-12/schema`
- **Schema ID Format**: `https://github.com/JDUB1216/nlt-otoi/schemas/{schema-name}.schema.json`
- **Versioning**: Semantic versioning (MAJOR.MINOR.PATCH) in schema version fields

---

## DEVELOPMENT GUIDELINES

### Code Quality Standards

**When Writing Python Code**:

```python
# Good: Clear, documented, type-hinted
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class HandoffRecord:
    """Structured log entry describing a single agent dispatch.

    Maintains provenance for TOI-OTOI compliance and auditability.
    """
    intent_id: str
    agent: str
    task: str
    thread_id: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def finalize(self, *, added: int, removed: int) -> None:
        """Update record after agent completes work."""
        self.metadata.update({"added": added, "removed": removed})
```

**Principles**:
- ✓ Type hints on all public functions and class attributes
- ✓ Docstrings explaining neurodivergent context where relevant
- ✓ Dataclasses for structured data (immutable where appropriate)
- ✓ Async/await for agent coordination patterns
- ✓ Explicit error handling with user-friendly messages

**When Writing Documentation**:

```markdown
# Good: Clear structure, multiple learning styles

## Quick Start (3 steps)
1. Download template
2. Fill in your preferences
3. Share with AI systems

## Detailed Explanation
[Comprehensive guide with examples...]

## Visual Reference
[Diagram or flowchart if applicable...]
```

**Principles**:
- ✓ Plain language, avoid jargon without explanation
- ✓ Consistent heading hierarchy and formatting
- ✓ Concrete examples for abstract concepts
- ✓ Multiple learning styles (text, visual, step-by-step)
- ✓ Accessibility-first (screen reader friendly, semantic structure)

### Privacy and Security Requirements

**EVERY line of code must respect these principles**:

```python
PRIVACY_REQUIREMENTS = {
    "processing": "Local-first, no cloud dependency for user data",
    "storage": "User device only, encrypted at rest",
    "transmission": "Never without explicit user consent",
    "data_sovereignty": "Complete user control over personal information",
    "sessions": "Ephemeral by default unless user saves",
    "telemetry": "Opt-in only, fully anonymized if enabled",
    "toi_compliance": "User privacy preferences override all defaults"
}
```

**Never**:
- ✗ Transmit user data to cloud services without explicit consent
- ✗ Store personal information without user control
- ✗ Log sensitive data in plain text
- ✗ Share data with third parties without user permission
- ✗ Implement "dark patterns" that reduce user agency

**Always**:
- ✓ Default to most privacy-preserving options
- ✓ Provide clear user controls for data management
- ✓ Encrypt sensitive data at rest (AES-256 standard)
- ✓ Maintain audit trails for data access
- ✓ Enable easy data export and deletion

### Neurodivergent-Centered Design

**Key Considerations**:

1. **Executive Function Support**:
   - Break complex tasks into clear, manageable steps
   - Provide decision trees and structured choices
   - Avoid overwhelming users with too many options at once
   - Support non-linear workflows (users may jump between tasks)

2. **Sensory Preferences**:
   - Support adjustable text density (sparse, moderate, dense)
   - Respect motion sensitivity (disable animations if requested)
   - Provide high contrast and reduced motion options
   - Allow customization of visual presentation

3. **Processing Time**:
   - Never rush users through interactions
   - Provide adequate time between complex questions
   - Support batched interactions (not just real-time)
   - Allow users to save state and return later

4. **Communication Style**:
   - Respect user preferences for directness vs. indirectness
   - Adapt explanation detail level to user needs
   - Provide both immediate and on-request feedback options
   - Use clear, predictable language patterns

5. **Energy Management**:
   - Support "spoon theory" awareness (limited daily energy)
   - Adapt complexity based on user energy levels
   - Provide break reminders when requested
   - Allow interaction frequency preferences

**Implementation Example**:

```python
def adapt_interaction(user_toi: TOI, content: str) -> str:
    """Adapt content presentation to user TOI preferences."""

    # Respect cognitive load preference
    if user_toi.cognitive.cognitive_load == "low":
        content = simplify_content(content)

    # Apply information structure preference
    if user_toi.cognitive.information_structure == "bullet-points":
        content = convert_to_bullets(content)

    # Honor sensory preferences
    if user_toi.cognitive.sensory_preferences.text_density == "sparse":
        content = add_whitespace(content)

    return content
```

---

## COMMON DEVELOPMENT TASKS

### Task 1: Creating or Modifying TOI Schemas

**Location**: `/schemas/personal-toi.schema.json` or `/schemas/collaborative-charter.schema.json`

**Guidelines**:
1. Use JSON Schema draft 2020-12 specification
2. All required fields must have clear descriptions
3. Provide example values for enum types
4. Maintain backwards compatibility when updating
5. Update version number in schema if making breaking changes

**Example Schema Addition**:

```json
{
  "new_preference": {
    "type": "string",
    "enum": ["option1", "option2", "option3"],
    "description": "Clear explanation of what this preference controls",
    "examples": ["option1"]
  }
}
```

**Validation**: Test with `/nlt-otoi/tools/validators/toi-validator.py`

### Task 2: Adding Documentation

**Location**: `/docs/` directory

**Guidelines**:
1. Use clear heading hierarchy (H1 for title, H2 for major sections)
2. Include concrete examples for every abstract concept
3. Provide multiple learning approaches (text, code, visual)
4. Consider accessibility (alt text, semantic markup)
5. Link to related documentation and schemas

**Template**:

```markdown
# Document Title

Brief 1-2 sentence overview of what this document covers.

## Quick Start (For Those Who Want to Jump In)
- Step 1: Concrete action
- Step 2: Another concrete action
- Step 3: Final step

## Detailed Guide (For Those Who Want Context)
[Comprehensive explanation with examples...]

## Technical Reference (For Developers)
[API documentation, code samples, edge cases...]

## Related Resources
- [Link to related doc](path/to/doc.md)
- [External resource](https://example.com)
```

### Task 3: Implementing TOI-Compliant Features

**Reference**: `/docs/implementation-guide.md` for comprehensive patterns

**Basic Pattern**:

```python
class TOICompliantAgent:
    """Example agent that respects user TOI preferences."""

    def __init__(self, user_toi: Dict[str, Any]):
        self.toi = user_toi
        self.communication_style = user_toi["communication"]["style"]
        self.processing_time = user_toi["cognitive"]["processing_time"]
        self.privacy_settings = user_toi["privacy"]

    def generate_response(self, query: str) -> str:
        """Generate TOI-adapted response to user query."""

        # 1. Generate base response
        response = self._base_response(query)

        # 2. Adapt communication style
        if self.communication_style == "formal":
            response = self._make_formal(response)
        elif self.communication_style == "casual":
            response = self._make_casual(response)

        # 3. Apply cognitive preferences
        if self.toi["cognitive"]["information_structure"] == "bullet-points":
            response = self._convert_to_bullets(response)

        # 4. Honor privacy preferences
        if self.privacy_settings["data_retention"] == "session-only":
            self._mark_for_deletion_after_session(response)

        return response
```

### Task 4: Adding Examples

**Location**: `/examples/` directory

**Guidelines**:
1. Use real-world, relatable scenarios
2. Include comprehensive TOI document (all required fields)
3. Add inline comments explaining choices
4. Validate against schema before committing
5. Consider diverse use cases (different disabilities, contexts)

**Example Structure**:

```json
{
  "version": "1.0.0",
  "metadata": {
    "created": "2024-01-15T10:00:00Z",
    "updated": "2024-01-15T10:00:00Z",
    "author": "example-user-pseudonym",
    "description": "Clear description of the use case this TOI addresses"
  },
  "communication": {
    "style": "friendly",
    "directness": "direct",
    "_comment": "Explanation of why this user chose these preferences"
  }
}
```

### Task 5: Working with Multi-Agent Orchestration

**Reference**: `/examples/neuroLift/orchestrator_patterns.py`

**Key Components**:

1. **AgentRegistry**: Declarative capability mapping
2. **Orchestrator**: Central router with intent ledger integration
3. **HandoffRecord**: Immutable audit artifacts
4. **EventRelay**: Async event bus for agent coordination

**Example Usage**:

```python
from examples.neuroLift.orchestrator_patterns import (
    AgentRegistry,
    AgentRegistration,
    Orchestrator
)

# 1. Create registry and register agents
registry = AgentRegistry()
registry.register(AgentRegistration(
    name="example-agent",
    entrypoint=my_agent_function,
    modalities=["text"],
    affordances=["summarize", "analyze"]
))

# 2. Initialize orchestrator
orchestrator = Orchestrator(registry)

# 3. Dispatch to agent with TOI context
result = await orchestrator.dispatch(
    agent_name="example-agent",
    capsule=context_capsule,
    task="Summarize this information",
    metadata={"user_toi": user_toi_dict}
)
```

---

## GIT WORKFLOW

### Branch Strategy

- **main**: Stable, production-ready code
- **Feature branches**: `feature/description-of-feature`
- **Bug fixes**: `fix/description-of-bug`
- **Documentation**: `docs/description-of-update`
- **Claude branches**: `claude/claude-md-migpjct2lab0edv0-*` (AI development branches)

### Commit Message Guidelines

**Format**:
```
<type>: <concise summary in imperative mood>

<optional detailed explanation>
<why this change was needed>

<optional references to issues>
```

**Types**:
- `feat`: New feature or enhancement
- `fix`: Bug fix
- `docs`: Documentation update
- `refactor`: Code refactoring without behavior change
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, build, etc.)
- `schema`: Changes to JSON schemas

**Examples**:

```
feat: Add energy_management section to personal TOI schema

Adds support for spoon theory and energy-aware interaction preferences.
Includes batched interaction frequency and break reminders.

Closes #42
```

```
docs: Update implementation guide with Python async patterns

Adds comprehensive examples of async/await usage in OTOI orchestration.
Improves accessibility of code samples with more detailed comments.
```

### Pull Request Process

1. **Create descriptive PR title**: Summarize the change clearly
2. **Provide context**: Explain what and why in PR description
3. **Reference issues**: Link to related issues or discussions
4. **Test changes**: Ensure schema validation passes, examples work
5. **Update documentation**: Keep docs in sync with code changes
6. **Consider accessibility**: Note any accessibility implications

**PR Template**:

```markdown
## Summary
[Brief description of changes]

## Motivation
[Why this change is needed]

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
[How changes were tested]

## Documentation
[Documentation updates included]

## Accessibility Considerations
[Any accessibility impacts or improvements]

## Related Issues
Closes #XX
```

---

## FILE CONVENTIONS

### JSON Schema Files

**Naming**: `{concept-name}.schema.json`
**Location**: `/schemas/` (current version) or `/nlt-otoi/schemas/v1.0/` (versioned)
**Format**: JSON, 2-space indentation
**Required fields**: `$schema`, `$id`, `title`, `description`, `type`

**Example Header**:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/JDUB1216/nlt-otoi/schemas/personal-toi.schema.json",
  "title": "Personal Terms of Interaction (TOI)",
  "description": "Schema for defining individual user preferences for AI interaction",
  "type": "object",
  "required": ["version", "metadata", "communication", "cognitive", "privacy"]
}
```

### Python Files

**Naming**: `snake_case.py`
**Location**: `/examples/neuroLift/` or `/nlt-otoi/tools/`
**Format**: 4-space indentation, max line length 100 characters
**Required**: Type hints, docstrings, `__all__` export list

**Example Header**:

```python
"""Brief module description.

Longer explanation of what this module provides and how it fits into
the OTOI framework. Include examples if helpful.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

__all__ = [
    "ExportedClass",
    "exported_function",
]
```

### Markdown Documentation

**Naming**: `kebab-case.md`
**Location**: `/docs/` or `/nlt-otoi/docs/`
**Format**: CommonMark with GitHub Flavored Markdown extensions
**Structure**: H1 title, H2 major sections, H3 subsections

**Example Structure**:

```markdown
# Document Title

Brief introduction paragraph.

## Section 1: Overview
[Content...]

### Subsection 1.1: Details
[Content...]

## Section 2: Implementation
[Content...]

## Related Resources
- [Link 1](path/to/resource)
- [Link 2](external-url)
```

### Template Files

**Naming**: `{purpose}-template.md`
**Location**: `/templates/` or `/nlt-otoi/templates/`
**Format**: Markdown with inline instructions in `[brackets]` or `<!-- comments -->`

**Example**:

```markdown
# Personal TOI Template

## Metadata
- **Created**: [YYYY-MM-DD]
- **Author**: [Your identifier - can be pseudonymous]
- **Purpose**: [Brief description of this TOI's purpose]

## Communication Preferences
- **Style**: [Choose: formal, casual, professional, friendly, adaptive]
  <!-- Explanation: How you prefer AI to communicate with you -->
```

---

## TESTING AND VALIDATION

### Schema Validation

**Tool**: `/nlt-otoi/tools/validators/toi-validator.py`

**Usage**:

```python
import json
import jsonschema

def validate_toi(toi_document: dict, schema_path: str) -> bool:
    """Validate TOI document against schema."""
    with open(schema_path, 'r') as schema_file:
        schema = json.load(schema_file)

    try:
        jsonschema.validate(toi_document, schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"TOI validation error: {e.message}")
        return False
```

**Test Before Committing**:
```bash
# Validate all example TOI documents
python nlt-otoi/tools/validators/toi-validator.py examples/neurodivergent-examples/*.json
```

### Integration Testing

**For Python Code**:

```python
import asyncio
from examples.neuroLift.orchestrator_patterns import (
    build_default_registry,
    Orchestrator
)

async def test_orchestrator():
    """Test basic orchestrator functionality."""
    registry = build_default_registry()
    orchestrator = Orchestrator(registry)

    # Create test context
    from examples.neuroLift.context_capsule import ContextCapsule, ContextSlice

    test_slice = ContextSlice(
        topic="test",
        payload={"message": "test message"},
        tags=["test"],
        provenance={"source": "test"}
    )
    capsule = ContextCapsule([test_slice])

    # Test dispatch
    result = await orchestrator.dispatch(
        agent_name="focus-agent",
        capsule=capsule,
        task="Test task"
    )

    assert result is not None
    assert len(orchestrator.handoff_log) == 1
    print("✓ Orchestrator test passed")

if __name__ == "__main__":
    asyncio.run(test_orchestrator())
```

### Documentation Testing

**Checklist**:
- [ ] All code examples run without errors
- [ ] Links to other docs resolve correctly
- [ ] JSON examples validate against schemas
- [ ] Markdown renders correctly (check with preview)
- [ ] Accessibility: Headings are hierarchical
- [ ] Accessibility: Code blocks have language specified
- [ ] Accessibility: Links have descriptive text (not "click here")

---

## IMPORTANT REMINDERS

### What Makes This Project Unique

**Not Traditional AI Standards Work**:
- This is **user governance over AI**, not AI governance over users
- Privacy isn't a feature - it's the foundational architecture
- Neurodivergent needs drive design, not added as afterthought
- Open standard - no vendor lock-in or corporate control

**Real-World Impact**:
- These schemas affect how vulnerable people interact with AI daily
- Executive function challenges are deeply personal and often shame-inducing
- Your code/docs will be used by people who've been failed by inaccessible systems
- Quality and clarity matter because real dignity is at stake

**Community-Driven**:
- Decisions made with neurodivergent community input
- Multiple learning styles and accessibility needs considered
- Inclusive development process (see CONTRIBUTING.md)
- Everyone's contributions valued equally

### Critical Principles to Uphold

**Always**:
- ✓ Preserve user agency in every design decision
- ✓ Default to maximum privacy protection
- ✓ Support diverse cognitive needs and working styles
- ✓ Provide clear, accessible documentation
- ✓ Maintain backwards compatibility when possible
- ✓ Include concrete examples with explanations

**Never**:
- ✗ Reduce user control or agency
- ✗ Compromise on privacy for convenience
- ✗ Use ableist language or assumptions
- ✗ Create features that increase user shame
- ✗ Design dependency patterns (build capacity instead)
- ✗ Assume one cognitive style works for everyone

---

## WORKING WITH JOSHUA (Repository Owner)

### Context About Joshua

**Cognitive Profile**: Adult with ADHD, neurodivergent founder of NeuroLift Technologies
**Expertise**: Systems thinking, pattern recognition, multi-AI orchestration
**Working Style**: Multi-threaded, interest-driven development

### Collaboration Guidelines

**Communication Style**:
- Be direct and structured in technical discussions
- Provide 2-3 options with tradeoffs, not single prescriptive paths
- Connect work to mission impact (motivating for interest-driven focus)
- Don't assume thread abandonment - he works on multiple things in parallel

**Respecting Agency**:
- Present options and reasoning, let him decide
- Avoid "you should" language - suggest "options include..."
- He understands the mission deeply - trust his architectural judgment
- Your role: technical implementation of vision, not defining vision

**Supporting Flow States**:
- When in hyperfocus, provide comprehensive implementations
- Save clarifications for natural pause points
- Preserve work state across context switches
- Don't require linear progression through tasks

**Decision-Making**:
```python
# Good approach:
def suggest_implementation(options: List[Approach]) -> None:
    """Present viable approaches with tradeoffs."""
    for option in options:
        print(f"Approach: {option.name}")
        print(f"Pros: {option.advantages}")
        print(f"Cons: {option.tradeoffs}")
        print(f"Privacy impact: {option.privacy_considerations}")
    print("Which direction aligns with your vision?")

# Avoid:
def prescriptive() -> None:
    """This is the only correct way."""
    # Removes agency, may miss insights
```

---

## FREQUENTLY ASKED QUESTIONS

### Q: What's the difference between TOI and OTOI?

**A**:
- **TOI (Terms of Interaction)**: Personal document defining how **one user** wants AI to interact with them
- **OTOI (Orchestrated Terms of Interaction)**: Coordination layer that enforces TOI across **multiple AI agents**

Think of it like: TOI is your personal preferences, OTOI is the system that makes sure every AI agent respects those preferences.

### Q: Why JSON Schema instead of other validation approaches?

**A**:
- Widely supported across languages and platforms
- Human-readable and editable
- Enables client-side validation (privacy-preserving)
- No vendor lock-in
- Good tooling ecosystem

### Q: Can I add new fields to the TOI schema?

**A**:
Yes, with guidelines:
1. Add as optional field (don't break existing TOI documents)
2. Provide clear description and examples
3. Consider privacy implications
4. Update documentation
5. Increment schema version appropriately (minor for additions, major for breaking changes)

### Q: How do I handle conflicting preferences in collaborative charters?

**A**:
See `/schemas/collaborative-charter.schema.json` and `/docs/implementation-guide.md` section on "Collaborative Charter Implementation". General principle: Individual TOI preferences should be honored when possible, with explicit conflict resolution protocols defined in the charter.

### Q: What if an AI system can't fully implement all TOI preferences?

**A**:
- **Graceful degradation**: Implement what you can, fail gracefully for what you can't
- **Transparency**: Inform user which preferences are honored and which aren't
- **Priority**: Privacy preferences are non-negotiable, adapt what you can otherwise
- See `/docs/best-practices.md` for "Graceful Degradation" section

### Q: Is this only for neurodivergent users?

**A**:
No - OTOI benefits everyone who wants control over AI interactions. However, it was **designed with neurodivergent needs first**, ensuring accessibility is built-in rather than added later. This "curb cut effect" makes the standard better for all users.

---

## QUICK REFERENCE LINKS

### Essential Documentation
- [Framework Overview](/docs/framework-overview.md) - Philosophy and architecture
- [Implementation Guide](/docs/implementation-guide.md) - Developer technical guide
- [Best Practices](/docs/best-practices.md) - Guidelines for users and developers
- [Contributing Guidelines](/CONTRIBUTING.md) - How to contribute

### Schemas
- [Personal TOI Schema](/schemas/personal-toi.schema.json) - Individual user preferences
- [Collaborative Charter Schema](/schemas/collaborative-charter.schema.json) - Group protocols

### Examples
- [ADHD Student Example](/examples/neurodivergent-examples/adhd-student-example.json)
- [Orchestrator Patterns](/examples/neuroLift/orchestrator_patterns.py)
- [Remote Dev Team Charter](/examples/team-collaboration/remote-dev-team-charter.json)

### Tools
- [TOI Generator](/nlt-otoi/tools/generators/toi-generator.py)
- [TOI Validator](/nlt-otoi/tools/validators/toi-validator.py)
- [Repository Guide](/GEMINI_TOPOGRAPHY.py)

### Templates
- [Personal TOI Template](/templates/personal-toi-template.md)
- [Collaborative Charter Template](/templates/collaborative-charter-template.md)
- [Quick Start Template](/templates/quick-start-template.md)

---

## NEXT STEPS FOR NEW CONTRIBUTORS

### First Time Working with This Repository?

**1. Read These First** (20 minutes):
- This file (CLAUDE.md) - Overview and conventions
- [README.md](/README.md) - Project introduction
- [CONTRIBUTING.md](/CONTRIBUTING.md) - Contribution process

**2. Explore These Next** (30 minutes):
- [Framework Overview](/docs/framework-overview.md) - Understand TOI-OTOI philosophy
- [Personal TOI Schema](/schemas/personal-toi.schema.json) - See structure
- [ADHD Student Example](/examples/neurodivergent-examples/adhd-student-example.json) - Real-world use

**3. Try This** (15 minutes):
- Create a personal TOI for yourself using [template](/templates/personal-toi-template.md)
- Validate it against the schema
- Think about how your preferences would affect AI interaction

**4. Ready to Contribute?**
- Check open issues for "good first issue" label
- Read relevant documentation for your contribution area
- Follow Git workflow and PR process outlined above
- Ask questions - we welcome all contributors!

---

## VERSION HISTORY

**1.0.0** (2025-11-27):
- Initial CLAUDE.md creation
- Comprehensive repository analysis and documentation
- Coverage of all major concepts, workflows, and conventions
- Integration of TOI-OTOI framework principles

---

## QUESTIONS OR CLARIFICATIONS?

If this guide doesn't answer your question:

1. **Check existing documentation** in `/docs/` directory
2. **Search closed issues** on GitHub (may have been discussed)
3. **Open a discussion** on GitHub Discussions (for general questions)
4. **Create an issue** with "question" label (for specific technical questions)
5. **Reference this file** and ask Joshua directly (for urgent clarifications)

---

**Remember**: Every line of code, every documentation update, every schema enhancement you contribute helps create a more accessible, user-controlled AI future for neurodivergent individuals and everyone who values agency in their AI interactions.

Thank you for being part of this mission.

---

**Prepared by**: Claude Code (AI Assistant)
**For**: NeuroLift OTOI Framework Repository
**Repository**: https://github.com/JDUB1216/nlt-otoi
**Last Updated**: 2025-11-27
**Next Review**: Quarterly or after major framework updates
