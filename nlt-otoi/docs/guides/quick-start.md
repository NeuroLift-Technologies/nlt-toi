# Quick Start Guide

Welcome to OTOI! This guide will help you get started with creating your first Personal Terms of Interaction (TOI) in just 15 minutes.

## What is OTOI?

OTOI (Orchestrated Terms of Interaction) is a framework that puts you in control of how AI systems interact with you. Instead of AI platforms deciding how to work with you, you define the terms that work best for your cognitive patterns and preferences.

## Why OTOI Matters for Neurodivergent Users

- **🎯 User Agency**: You control how AI works with you, not the platform
- **🧠 Cognitive Support**: Built-in support for ADHD, autism, and other neurodivergent patterns
- **🔒 Privacy First**: Complete control over your data and how it's used
- **🤝 Multi-Agent Harmony**: Seamless collaboration between different AI assistants

## Step 1: Choose Your Template (2 minutes)

We provide several templates to get you started:

### For ADHD Users
```bash
# Use the ADHD-optimized template
cp templates/personal-toi/adhd-optimized-toi.json my-personal-toi.json
```

### For Privacy-Focused Users
```bash
# Use the privacy-focused template
cp templates/personal-toi/privacy-focused-toi.json my-personal-toi.json
```

### For Developers
```bash
# Use the developer template
cp templates/personal-toi/developer-toi.json my-personal-toi.json
```

## Step 2: Customize Your TOI (10 minutes)

Open your TOI file in any text editor and customize the key sections:

### 1. Update Your Cognitive Profile
```json
{
  "user_profile": {
    "cognitive_patterns": {
      "attention_patterns": {
        "hyperfocus_capability": true,
        "context_switching_cost": "high",
        "interest_driven": true,
        "multi_threading": true
      }
    }
  }
}
```

### 2. Set Your Communication Preferences
```json
{
  "interaction_preferences": {
    "response_style": {
      "tone": "encouraging",
      "length": "moderate",
      "structure": {
        "use_headings": true,
        "use_bullets": true,
        "use_examples": true
      }
    }
  }
}
```

### 3. Configure Data Privacy
```json
{
  "data_governance": {
    "data_retention": {
      "conversation_history": "7_days",
      "personal_information": "session_only"
    },
    "privacy_level": "high"
  }
}
```

## Step 3: Validate Your TOI (2 minutes)

Make sure your TOI is valid:

```bash
# Validate your TOI
python tools/validators/toi-validator.py my-personal-toi.json

# Check compliance
python tools/validators/compliance-checker.py my-personal-toi.json
```

## Step 4: Deploy to Your AI Assistants (1 minute)

Generate custom instructions for each AI platform:

```bash
# Generate instructions for all platforms
python tools/generators/toi-generator.py my-personal-toi.json

# Or generate for specific platforms
python tools/generators/toi-generator.py my-personal-toi.json --platform claude
python tools/generators/toi-generator.py my-personal-toi.json --platform cursor
```

## Step 5: Test Your Setup

### Test with Claude
1. Copy the generated Claude instructions
2. Paste them into Claude's custom instructions
3. Ask Claude to help with a task
4. Verify it follows your preferences

### Test with Cursor
1. Copy the generated Cursor instructions
2. Paste them into Cursor's custom instructions
3. Start a coding session
4. Verify it supports your development patterns

## Common Customizations

### For ADHD Users
- Set `hyperfocus_capability: true`
- Set `context_switching_cost: "high"`
- Enable task breakdown and progress tracking
- Use visual organization preferences

### For Autism Users
- Set `structured_approach: true`
- Use clear, direct communication
- Provide predictable patterns
- Support special interests

### For Privacy-Conscious Users
- Set `privacy_level: "maximum"`
- Minimize data retention
- Disable data sharing
- Use session-only storage

## Troubleshooting

### Validation Errors
If your TOI doesn't validate:
1. Check the error messages
2. Ensure all required fields are present
3. Verify JSON syntax is correct
4. Use the schema reference for guidance

### AI Not Following TOI
If AI assistants aren't following your TOI:
1. Verify custom instructions were applied correctly
2. Check that the TOI is valid
3. Test with a simple request first
4. Contact support if issues persist

## Next Steps

Now that you have your basic TOI set up:

1. **Explore Examples**: Check out `examples/` for real-world implementations
2. **Read Documentation**: Dive deeper with our comprehensive docs
3. **Join Community**: Connect with other users and contributors
4. **Contribute**: Help improve OTOI for everyone

## Getting Help

- **Documentation**: Check our comprehensive docs in `docs/`
- **Examples**: Look at real-world implementations in `examples/`
- **Community**: Join discussions on GitHub
- **Support**: Contact us at [support@neurolift.tech](mailto:support@neurolift.tech)

## ADHD-Friendly Tips

- **Start Simple**: Don't try to configure everything at once
- **Use Templates**: Start with a template that matches your needs
- **Test Incrementally**: Test each AI assistant one at a time
- **Take Breaks**: Don't try to do everything in one session
- **Ask for Help**: Reach out if you get stuck

---

**Congratulations! You've created your first Personal TOI. You're now in control of how AI systems interact with you.**

*Remember: OTOI is designed to work with your cognitive patterns, not against them. Take your time, experiment, and find what works best for you.*