# Personal TOI Specification v1.0

## Overview

The Personal Terms of Interaction (TOI) specification defines a machine-readable JSON schema that allows users to specify their preferences, constraints, and requirements for AI system interactions. This specification is designed with neurodivergent users in mind, providing comprehensive support for different cognitive patterns and accessibility needs.

## Schema Structure

### Root Object

The Personal TOI is a JSON object with the following required top-level properties:

- `metadata`: Schema metadata and version information
- `user_profile`: User's cognitive profile and preferences
- `interaction_preferences`: How the user wants AI to interact with them
- `data_governance`: How the user wants their data to be handled
- `accessibility_needs`: Specific accessibility requirements and preferences

### Metadata Section

```json
{
  "metadata": {
    "version": "v1.0",
    "created_date": "2025-01-06T00:00:00Z",
    "last_updated": "2025-01-06T00:00:00Z",
    "user_id": "optional-user-identifier",
    "tags": ["adhd", "neurodivergent", "optimized"]
  }
}
```

**Required Fields:**
- `version`: Schema version (pattern: `^v\\d+\\.\\d+$`)
- `created_date`: ISO 8601 timestamp when TOI was created
- `last_updated`: ISO 8601 timestamp when TOI was last modified

**Optional Fields:**
- `user_id`: Unique identifier for the user (for privacy)
- `tags`: User-defined tags for categorization

### User Profile Section

The user profile captures the user's cognitive characteristics and communication preferences.

#### Cognitive Patterns

```json
{
  "user_profile": {
    "cognitive_patterns": {
      "attention_patterns": {
        "hyperfocus_capability": true,
        "context_switching_cost": "high",
        "interest_driven": true,
        "multi_threading": true
      },
      "processing_speeds": {
        "variable_speed": true,
        "default_speed": "medium",
        "acceleration_triggers": [
          "high_interest_topics",
          "visual_organization",
          "clear_structure"
        ]
      },
      "memory_preferences": {
        "external_memory": true,
        "visual_organization": true,
        "structured_approach": true
      }
    }
  }
}
```

**Attention Patterns:**
- `hyperfocus_capability`: Can achieve deep immersion in engaging tasks
- `context_switching_cost`: Energy cost of switching between tasks (low/medium/high)
- `interest_driven`: Focus tied to personal engagement level
- `multi_threading`: Can maintain multiple conceptual threads

**Processing Speeds:**
- `variable_speed`: Processing speed varies based on engagement
- `default_speed`: Default processing speed preference (slow/medium/fast)
- `acceleration_triggers`: What helps the user process faster

**Memory Preferences:**
- `external_memory`: Prefers external systems for information storage
- `visual_organization`: Prefers visual organization of information
- `structured_approach`: Prefers structured, organized approaches

#### Communication Style

```json
{
  "user_profile": {
    "communication_style": {
      "directness": "direct",
      "detail_level": "moderate",
      "format_preferences": ["text", "visual"]
    }
  }
}
```

**Communication Preferences:**
- `directness`: Preferred level of directness (very_direct/direct/moderate/indirect)
- `detail_level`: Preferred level of detail (minimal/moderate/comprehensive)
- `format_preferences`: Preferred communication formats (text/visual/audio/interactive)

### Interaction Preferences Section

Defines how the user wants AI systems to interact with them.

#### Response Style

```json
{
  "interaction_preferences": {
    "response_style": {
      "tone": "encouraging",
      "length": "moderate",
      "structure": {
        "use_headings": true,
        "use_bullets": true,
        "use_examples": true,
        "use_visuals": true
      }
    }
  }
}
```

**Response Characteristics:**
- `tone`: Preferred tone (professional/casual/encouraging/matter_of_fact)
- `length`: Preferred length (brief/moderate/detailed)
- `structure`: Response structure preferences

#### Task Management

```json
{
  "interaction_preferences": {
    "task_management": {
      "break_down_tasks": true,
      "provide_progress_tracking": true,
      "suggest_priorities": true,
      "remind_about_deadlines": true,
      "adapt_to_energy_levels": true
    }
  }
}
```

**Task Support Features:**
- `break_down_tasks`: Break complex tasks into smaller steps
- `provide_progress_tracking`: Track and report progress on tasks
- `suggest_priorities`: Suggest task priorities and ordering
- `remind_about_deadlines`: Provide deadline reminders and alerts
- `adapt_to_energy_levels`: Adjust task suggestions based on energy levels

#### Learning Support

```json
{
  "interaction_preferences": {
    "learning_support": {
      "explain_concepts": true,
      "provide_context": true,
      "use_analogies": true,
      "repeat_important_points": true
    }
  }
}
```

**Learning Features:**
- `explain_concepts`: Explain concepts in detail when needed
- `provide_context`: Provide background context for new information
- `use_analogies`: Use analogies and comparisons to explain concepts
- `repeat_important_points`: Repeat and reinforce important information

### Data Governance Section

Defines how the user wants their data to be handled.

#### Data Retention

```json
{
  "data_governance": {
    "data_retention": {
      "conversation_history": "7_days",
      "personal_information": "session_only",
      "learning_data": "30_days"
    }
  }
}
```

**Retention Periods:**
- `conversation_history`: How long to retain conversation history
- `personal_information`: How long to retain personal information
- `learning_data`: How long to retain learning and preference data

**Valid Values:**
- `none`: Don't retain data
- `session_only`: Retain only for current session
- `24_hours`: Retain for 24 hours
- `7_days`: Retain for 7 days
- `30_days`: Retain for 30 days
- `indefinite`: Retain indefinitely

#### Data Usage

```json
{
  "data_governance": {
    "data_usage": {
      "improve_responses": true,
      "personalize_experience": true,
      "share_with_other_ais": false,
      "analytics_and_research": false
    }
  }
}
```

**Usage Permissions:**
- `improve_responses`: Use data to improve AI responses
- `personalize_experience`: Use data to personalize the experience
- `share_with_other_ais`: Share data with other AI systems
- `analytics_and_research`: Use data for analytics and research

#### Privacy Level

```json
{
  "data_governance": {
    "privacy_level": "high"
  }
}
```

**Privacy Levels:**
- `minimal`: Minimal privacy protection
- `moderate`: Moderate privacy protection
- `high`: High privacy protection
- `maximum`: Maximum privacy protection

### Accessibility Needs Section

Defines specific accessibility requirements and preferences.

#### Cognitive Accessibility

```json
{
  "accessibility_needs": {
    "cognitive_accessibility": {
      "reduce_cognitive_load": true,
      "provide_structure": true,
      "use_clear_language": true,
      "provide_multiple_formats": true
    }
  }
}
```

**Cognitive Support:**
- `reduce_cognitive_load`: Minimize cognitive load in interactions
- `provide_structure`: Provide clear structure and organization
- `use_clear_language`: Use clear, jargon-free language
- `provide_multiple_formats`: Provide information in multiple formats

#### Sensory Accessibility

```json
{
  "accessibility_needs": {
    "sensory_accessibility": {
      "visual_preferences": {
        "high_contrast": false,
        "large_text": false,
        "minimal_visual_clutter": true
      },
      "auditory_preferences": {
        "audio_descriptions": false,
        "text_to_speech": false
      }
    }
  }
}
```

**Visual Preferences:**
- `high_contrast`: Prefer high contrast visual elements
- `large_text`: Prefer larger text sizes
- `minimal_visual_clutter`: Prefer minimal visual clutter

**Auditory Preferences:**
- `audio_descriptions`: Prefer audio descriptions of visual content
- `text_to_speech`: Prefer text-to-speech for written content

#### Motor Accessibility

```json
{
  "accessibility_needs": {
    "motor_accessibility": {
      "keyboard_navigation": true,
      "voice_commands": false,
      "gesture_alternatives": true
    }
  }
}
```

**Motor Support:**
- `keyboard_navigation`: Prefer keyboard navigation over mouse
- `voice_commands`: Prefer voice commands when available
- `gesture_alternatives`: Prefer alternatives to complex gestures

### AI Agent Preferences Section

Defines preferences for specific AI agents and platforms.

```json
{
  "ai_agent_preferences": {
    "claude": {
      "use_for": [
        "complex_problem_solving",
        "ethical_reasoning",
        "long_form_writing"
      ],
      "avoid_for": [
        "quick_coding_tasks",
        "rapid_prototyping"
      ],
      "custom_instructions": "Focus on providing comprehensive, well-structured responses..."
    }
  }
}
```

**Agent Configuration:**
- `use_for`: What to use this agent for
- `avoid_for`: What to avoid using this agent for
- `custom_instructions`: Custom instructions for this agent

### Emergency Protocols Section

Defines emergency and safety protocols.

```json
{
  "emergency_protocols": {
    "safety_keywords": [
      "overwhelmed",
      "stuck",
      "confused",
      "frustrated"
    ],
    "emergency_contacts": [
      {
        "name": "Primary Support",
        "contact_method": "email",
        "priority": "primary"
      }
    ],
    "escalation_procedures": {
      "technical_issues": "Escalate to technical support...",
      "safety_concerns": "Immediately notify user...",
      "privacy_breaches": "Immediately stop data processing..."
    }
  }
}
```

**Emergency Features:**
- `safety_keywords`: Keywords that trigger emergency protocols
- `emergency_contacts`: Emergency contact information
- `escalation_procedures`: When and how to escalate issues

## Validation Rules

### Required Fields

The following fields are required in every Personal TOI:

- `metadata.version`
- `metadata.created_date`
- `metadata.last_updated`
- `user_profile.cognitive_patterns`
- `interaction_preferences.response_style`
- `interaction_preferences.task_management`
- `data_governance.data_retention`
- `data_governance.data_usage`

### Data Types

- **Strings**: Must be valid UTF-8 encoded strings
- **Booleans**: Must be `true` or `false`
- **Enums**: Must be one of the specified valid values
- **Arrays**: Must contain only valid items
- **Objects**: Must contain only allowed properties

### Format Validation

- **Dates**: Must be valid ISO 8601 timestamps
- **Versions**: Must match pattern `^v\\d+\\.\\d+$`
- **JSON**: Must be valid JSON syntax

## Examples

### ADHD-Optimized TOI

```json
{
  "metadata": {
    "version": "v1.0",
    "created_date": "2025-01-06T00:00:00Z",
    "last_updated": "2025-01-06T00:00:00Z",
    "tags": ["adhd", "neurodivergent", "optimized"]
  },
  "user_profile": {
    "cognitive_patterns": {
      "attention_patterns": {
        "hyperfocus_capability": true,
        "context_switching_cost": "high",
        "interest_driven": true,
        "multi_threading": true
      }
    }
  },
  "interaction_preferences": {
    "response_style": {
      "tone": "encouraging",
      "length": "moderate",
      "structure": {
        "use_headings": true,
        "use_bullets": true,
        "use_examples": true
      }
    },
    "task_management": {
      "break_down_tasks": true,
      "provide_progress_tracking": true,
      "adapt_to_energy_levels": true
    }
  },
  "data_governance": {
    "data_retention": {
      "conversation_history": "7_days",
      "personal_information": "session_only"
    },
    "data_usage": {
      "improve_responses": true,
      "personalize_experience": true,
      "share_with_other_ais": false
    },
    "privacy_level": "high"
  },
  "accessibility_needs": {
    "cognitive_accessibility": {
      "reduce_cognitive_load": true,
      "provide_structure": true,
      "use_clear_language": true
    }
  }
}
```

## Implementation Guidelines

### For AI Systems

1. **Respect User Preferences**: Always follow the user's defined preferences
2. **Validate TOI**: Ensure the TOI is valid before processing
3. **Handle Errors Gracefully**: Provide clear error messages for invalid TOI
4. **Maintain Privacy**: Respect data governance settings
5. **Support Accessibility**: Implement accessibility features as specified

### For Developers

1. **Use Schema Validation**: Always validate TOI against the schema
2. **Provide Clear Errors**: Give helpful error messages for validation failures
3. **Support Extensions**: Allow for future schema extensions
4. **Test Thoroughly**: Test with various TOI configurations
5. **Document Changes**: Document any schema changes clearly

## Future Extensions

The Personal TOI specification is designed to be extensible. Future versions may include:

- Additional cognitive pattern support
- More granular accessibility options
- Enhanced privacy controls
- Integration with external systems
- Real-time preference updates

## Compliance

This specification follows:

- **JSON Schema Draft 7**: For schema validation
- **WCAG 2.1 AA**: For accessibility compliance
- **GDPR**: For privacy and data protection
- **ISO 8601**: For date and time formatting

---

*This specification is part of the OTOI Framework and is maintained by the NeuroLift Technologies team.*