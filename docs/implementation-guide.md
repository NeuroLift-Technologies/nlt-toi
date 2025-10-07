# OTOI Implementation Guide

This guide provides technical details for implementing OTOI support in AI systems, applications, and platforms.

## Quick Start for Developers

### 1. Understand the Schema

OTOI uses JSON Schema to define the structure of TOI documents:

- **Personal TOI**: Individual user preferences ([schema](/schemas/personal-toi.schema.json))
- **Collaborative Charter**: Group interaction protocols ([schema](/schemas/collaborative-charter.schema.json))

### 2. Basic Integration Steps

1. **Parse TOI Documents**: Use the JSON schemas to validate and parse user TOI documents
2. **Adapt Behavior**: Modify your AI's behavior based on TOI preferences
3. **Respect Privacy**: Follow the privacy settings in the TOI document
4. **Provide Feedback**: Let users know how their TOI is being used

### 3. Minimal Implementation

Here's a basic example of integrating Personal TOI:

```javascript
import Ajv from 'ajv';
import personalToiSchema from './schemas/personal-toi.schema.json';

class OTOIAdapter {
  constructor() {
    this.ajv = new Ajv();
    this.validatePersonalToi = this.ajv.compile(personalToiSchema);
  }

  loadTOI(toiDocument) {
    if (!this.validatePersonalToi(toiDocument)) {
      throw new Error('Invalid TOI document');
    }
    this.toi = toiDocument;
    this.adaptBehavior();
  }

  adaptBehavior() {
    // Adapt communication style
    this.communicationStyle = this.toi.communication.style;
    this.directnessLevel = this.toi.communication.directness;
    
    // Respect processing time
    this.processingTime = this.toi.cognitive.processing_time;
    
    // Honor privacy settings
    this.dataRetention = this.toi.privacy.data_retention;
  }

  generateResponse(query) {
    // Apply TOI preferences to response generation
    let response = this.baseGenerateResponse(query);
    
    // Adapt style
    if (this.communicationStyle === 'formal') {
      response = this.makeFormal(response);
    }
    
    // Adapt structure based on cognitive preferences
    if (this.toi.cognitive.information_structure === 'bullet-points') {
      response = this.convertToBulletPoints(response);
    }
    
    return response;
  }
}
```

## Schema Implementation

### Validation

Always validate TOI documents against the schema:

```python
import json
import jsonschema

def validate_toi(toi_document, schema_path):
    with open(schema_path, 'r') as schema_file:
        schema = json.load(schema_file)
    
    try:
        jsonschema.validate(toi_document, schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"TOI validation error: {e.message}")
        return False
```

### Required vs. Optional Fields

The schemas define required fields that must be present:

**Personal TOI Required Fields:**
- `version`
- `metadata` (created, updated, author)
- `communication` (style, directness)
- `cognitive` (processing_time, information_structure)
- `privacy` (data_retention, sharing_consent)

**Handle Missing Optional Fields Gracefully:**

```javascript
function getCommunicationPreference(toi, preference, defaultValue) {
  return toi.communication?.[preference] ?? defaultValue;
}

// Usage
const feedbackStyle = getCommunicationPreference(
  userToi, 
  'feedback_preference', 
  'on-request'
);
```

## Communication Adaptation

### Style Adaptation

```javascript
class CommunicationAdapter {
  constructor(toi) {
    this.style = toi.communication.style;
    this.directness = toi.communication.directness;
    this.explanationLevel = toi.communication.explanation_level;
  }

  adaptMessage(message) {
    let adapted = message;

    // Apply style
    switch (this.style) {
      case 'formal':
        adapted = this.makeFormal(adapted);
        break;
      case 'casual':
        adapted = this.makeCasual(adapted);
        break;
      case 'friendly':
        adapted = this.makeFriendly(adapted);
        break;
    }

    // Apply directness
    switch (this.directness) {
      case 'very-direct':
        adapted = this.makeVeryDirect(adapted);
        break;
      case 'indirect':
        adapted = this.makeIndirect(adapted);
        break;
    }

    return adapted;
  }

  makeFormal(text) {
    // Convert to formal language
    return text
      .replace(/can't/g, 'cannot')
      .replace(/won't/g, 'will not')
      .replace(/I'd/g, 'I would');
  }

  adaptExplanationLevel(explanation) {
    switch (this.explanationLevel) {
      case 'minimal':
        return this.summarize(explanation);
      case 'comprehensive':
        return this.expandWithDetails(explanation);
      default:
        return explanation;
    }
  }
}
```

## Cognitive Accessibility Implementation

### Processing Time Adaptation

```javascript
class CognitiveAdapter {
  constructor(toi) {
    this.processingTime = toi.cognitive.processing_time;
    this.cognitiveLoad = toi.cognitive.cognitive_load;
    this.informationStructure = toi.cognitive.information_structure;
  }

  adaptResponseTiming(response) {
    const delays = {
      'immediate': 0,
      'short': 1000,
      'moderate': 3000,
      'extended': 5000,
      'flexible': 2000
    };

    const delay = delays[this.processingTime] || 0;
    
    if (delay > 0) {
      return this.addTypingIndicator(response, delay);
    }
    
    return response;
  }

  structureInformation(content) {
    switch (this.informationStructure) {
      case 'bullet-points':
        return this.convertToBulletPoints(content);
      case 'hierarchical':
        return this.createHierarchy(content);
      case 'visual':
        return this.addVisualElements(content);
      default:
        return content;
    }
  }

  convertToBulletPoints(text) {
    // Simple implementation - split on sentences and bullet-ize
    const sentences = text.split('. ');
    return sentences.map(sentence => `• ${sentence.trim()}`).join('\n');
  }
}
```

### Sensory Preferences

```javascript
class SensoryAdapter {
  constructor(toi) {
    this.sensory = toi.cognitive.sensory_preferences || {};
  }

  adaptVisualPresentation(content) {
    let adapted = content;

    if (this.sensory.text_density === 'sparse') {
      adapted = this.addWhitespace(adapted);
    }

    if (this.sensory.color_sensitivity) {
      adapted = this.useHighContrast(adapted);
    }

    if (this.sensory.motion_sensitivity) {
      adapted = this.removeAnimations(adapted);
    }

    return adapted;
  }
}
```

## Privacy Implementation

### Data Retention

```javascript
class PrivacyManager {
  constructor(toi) {
    this.dataRetention = toi.privacy.data_retention;
    this.sharingConsent = toi.privacy.sharing_consent;
    this.anonymization = toi.privacy.anonymization;
  }

  handleDataRetention(data) {
    const retentionPolicies = {
      'session-only': () => this.deleteAfterSession(data),
      'short-term': () => this.deleteAfter(data, 24 * 60 * 60 * 1000), // 24 hours
      'long-term': () => this.deleteAfter(data, 30 * 24 * 60 * 60 * 1000), // 30 days
      'user-controlled': () => this.flagForUserDeletion(data),
      'permanent': () => this.retain(data)
    };

    const policy = retentionPolicies[this.dataRetention];
    if (policy) {
      policy();
    }
  }

  canShareData(purpose) {
    switch (this.sharingConsent) {
      case 'never':
        return false;
      case 'explicit-only':
        return this.hasExplicitConsent(purpose);
      case 'aggregate-only':
        return purpose === 'aggregate';
      case 'research-approved':
        return this.isResearchApproved(purpose);
      default:
        return false;
    }
  }
}
```

## Energy Management

### Interaction Frequency Adaptation

```javascript
class EnergyManager {
  constructor(toi) {
    this.energySettings = toi.energy_management || {};
    this.userEnergyLevel = 'moderate'; // Track dynamically
  }

  shouldInteract() {
    const frequency = this.energySettings.interaction_frequency;
    
    switch (frequency) {
      case 'continuous':
        return true;
      case 'batched':
        return this.isBatchTime();
      case 'scheduled':
        return this.isScheduledTime();
      case 'on-demand':
        return this.hasUserRequest();
      default:
        return true;
    }
  }

  adaptComplexity(content) {
    if (!this.energySettings.complexity_adaptation) {
      return content;
    }

    if (this.userEnergyLevel === 'low') {
      return this.simplifyContent(content);
    }

    return content;
  }

  shouldSuggestBreak() {
    return this.energySettings.break_reminders && 
           this.hasBeenActiveFor(30 * 60 * 1000); // 30 minutes
  }
}
```

## Collaborative Charter Implementation

### Multi-User Scenarios

```javascript
class CollaborativeManager {
  constructor(charter, participantTOIs) {
    this.charter = charter;
    this.participantTOIs = participantTOIs;
  }

  resolveConflictingPreferences(preference) {
    const priority = this.charter.integration.toi_priority;
    
    switch (priority) {
      case 'individual-first':
        return this.prioritizeIndividual(preference);
      case 'group-first':
        return this.charter.protocols[preference];
      case 'balanced':
        return this.findCompromise(preference);
      case 'context-dependent':
        return this.contextualDecision(preference);
    }
  }

  findCompromise(preference) {
    const values = this.participantTOIs.map(toi => 
      this.getPreferenceValue(toi, preference)
    );
    
    // Example: Take the most inclusive option
    if (preference === 'communication.explanation_level') {
      return this.getMostDetailed(values);
    }
    
    if (preference === 'cognitive.processing_time') {
      return this.getLongest(values);
    }
    
    return this.getMostCommon(values);
  }
}
```

## Testing and Validation

### Unit Testing TOI Integration

```javascript
describe('OTOI Integration', () => {
  test('adapts communication style correctly', () => {
    const toi = {
      version: '1.0.0',
      communication: { style: 'formal', directness: 'direct' },
      // ... other required fields
    };
    
    const adapter = new OTOIAdapter();
    adapter.loadTOI(toi);
    
    const response = adapter.generateResponse('Hello');
    expect(response).toMatch(/formal language patterns/);
  });

  test('respects privacy settings', () => {
    const toi = {
      privacy: { data_retention: 'session-only' }
    };
    
    const manager = new PrivacyManager(toi);
    manager.handleData(testData);
    
    // Verify data is marked for deletion
    expect(manager.isMarkedForDeletion(testData)).toBe(true);
  });
});
```

### Integration Testing

```javascript
describe('Full OTOI Integration', () => {
  test('end-to-end user interaction', async () => {
    const userToi = loadTestTOI('neurodivergent-user.json');
    const aiSystem = new AISystem();
    
    aiSystem.loadTOI(userToi);
    
    const interaction = await aiSystem.interact('Help me plan my day');
    
    // Verify adaptations were applied
    expect(interaction.style).toBe('structured');
    expect(interaction.processingTime).toBeGreaterThan(2000);
    expect(interaction.format).toBe('bullet-points');
  });
});
```

## Performance Considerations

### Caching TOI Preferences

```javascript
class TOICache {
  constructor() {
    this.cache = new Map();
  }

  getAdaptedResponse(userId, query) {
    const cacheKey = `${userId}:${this.hashQuery(query)}`;
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    const response = this.generateAdaptedResponse(userId, query);
    this.cache.set(cacheKey, response);
    
    return response;
  }
}
```

### Efficient Preference Lookup

```javascript
class PreferenceIndex {
  constructor(toi) {
    this.index = this.buildIndex(toi);
  }

  buildIndex(toi) {
    return {
      communication: new Map([
        ['style', toi.communication.style],
        ['directness', toi.communication.directness],
        // ... other preferences
      ]),
      cognitive: new Map([
        ['processing_time', toi.cognitive.processing_time],
        // ... other preferences
      ])
    };
  }

  get(category, preference) {
    return this.index.get(category)?.get(preference);
  }
}
```

## Security Considerations

### TOI Document Validation

```javascript
function validateTOISource(toi, signature) {
  // Verify the TOI document hasn't been tampered with
  const expectedHash = calculateHash(toi);
  const providedHash = signature.hash;
  
  if (expectedHash !== providedHash) {
    throw new Error('TOI document integrity check failed');
  }
  
  // Verify the signature if present
  if (signature.publicKey) {
    if (!verifySignature(toi, signature)) {
      throw new Error('TOI document signature verification failed');
    }
  }
}
```

### Secure Storage

```javascript
class SecureTOIStorage {
  encrypt(toi, userKey) {
    return crypto.encrypt(JSON.stringify(toi), userKey);
  }

  decrypt(encryptedToi, userKey) {
    const decrypted = crypto.decrypt(encryptedToi, userKey);
    return JSON.parse(decrypted);
  }

  store(userId, toi) {
    const userKey = this.getUserKey(userId);
    const encrypted = this.encrypt(toi, userKey);
    return this.database.store(userId, encrypted);
  }
}
```

## Best Practices

### 1. Graceful Degradation

Always provide fallback behavior when TOI preferences can't be fully honored:

```javascript
function adaptWithFallback(toi, content) {
  try {
    return fullAdaptation(toi, content);
  } catch (error) {
    console.warn('Full TOI adaptation failed, using basic adaptation');
    return basicAdaptation(toi, content);
  }
}
```

### 2. User Feedback

Let users know how their TOI is being used:

```javascript
function generateResponseWithFeedback(toi, query) {
  const response = generateResponse(query, toi);
  
  if (toi.communication.feedback_preference === 'summary') {
    response.metadata = {
      adaptations: [
        'Used formal communication style',
        'Structured information as bullet points',
        'Added 3-second processing delay'
      ]
    };
  }
  
  return response;
}
```

### 3. Progressive Enhancement

Start with basic TOI support and add more sophisticated features over time:

```javascript
class ProgressiveTOIAdapter {
  constructor() {
    this.supportedFeatures = [
      'basic-communication',
      'simple-privacy',
      'cognitive-timing'
    ];
  }

  adapt(toi, content) {
    let adapted = content;
    
    if (this.supports('basic-communication')) {
      adapted = this.adaptCommunication(adapted, toi);
    }
    
    if (this.supports('cognitive-timing')) {
      adapted = this.adaptTiming(adapted, toi);
    }
    
    // Add more features as they're implemented
    
    return adapted;
  }
}
```

## Next Steps

1. **Review the Schemas**: Study the [JSON schemas](/schemas/) in detail
2. **Try the Templates**: Use our [templates](/templates/) to understand user needs
3. **See Examples**: Look at [real implementations](/examples/)
4. **Start Small**: Implement basic communication adaptation first
5. **Test with Users**: Especially neurodivergent and accessibility communities
6. **Contribute Back**: Share your implementation experiences and improvements

## Getting Help

- **Technical Questions**: Create an issue with the "question" label
- **Implementation Problems**: Create an issue with the "bug" label
- **Feature Requests**: Create an issue with the "enhancement" label
- **Community Discussion**: Use GitHub Discussions

---

*Remember: The goal of OTOI is to put users in control of their AI interactions. Every implementation decision should prioritize user agency, accessibility, and respect for diverse needs.*