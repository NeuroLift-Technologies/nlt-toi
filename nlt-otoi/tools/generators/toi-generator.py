#!/usr/bin/env python3
"""
OTOI Custom Instructions Generator

Generates custom instructions for different AI platforms based on Personal TOI.
Supports neurodivergent users with clear, accessible instructions.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class TOIGenerator:
    """Generates custom instructions for AI platforms based on Personal TOI."""
    
    def __init__(self):
        """Initialize the generator."""
        self.templates_dir = Path(__file__).parent.parent / "templates" / "custom-instructions"
        self.output_dir = Path("generated-instructions")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_instructions(self, toi_path: Path, platforms: List[str] = None) -> Dict[str, str]:
        """
        Generate custom instructions for specified platforms.
        
        Args:
            toi_path: Path to the Personal TOI file
            platforms: List of platforms to generate instructions for
            
        Returns:
            Dictionary mapping platform names to generated instruction content
        """
        # Load TOI data
        try:
            with open(toi_path, 'r', encoding='utf-8') as f:
                toi_data = json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: TOI file not found at {toi_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in TOI file: {e}")
            sys.exit(1)
        
        # Default platforms if none specified
        if platforms is None:
            platforms = ["claude", "chatgpt", "cursor", "gemini", "perplexity"]
        
        results = {}
        
        for platform in platforms:
            print(f"🔧 Generating instructions for {platform}...")
            instructions = self._generate_platform_instructions(toi_data, platform)
            results[platform] = instructions
            
            # Save to file
            output_file = self.output_dir / f"{platform}-instructions.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(instructions)
            
            print(f"   ✅ Saved to {output_file}")
        
        return results
    
    def _generate_platform_instructions(self, toi_data: Dict[str, Any], platform: str) -> str:
        """Generate custom instructions for a specific platform."""
        # Get platform-specific preferences
        agent_prefs = toi_data.get("ai_agent_preferences", {}).get(platform, {})
        
        # Get user profile
        user_profile = toi_data.get("user_profile", {})
        cognitive_patterns = user_profile.get("cognitive_patterns", {})
        
        # Get interaction preferences
        interaction_prefs = toi_data.get("interaction_preferences", {})
        response_style = interaction_prefs.get("response_style", {})
        
        # Get accessibility needs
        accessibility_needs = toi_data.get("accessibility_needs", {})
        
        # Generate instructions
        instructions = self._build_instructions(
            platform, agent_prefs, cognitive_patterns, response_style, accessibility_needs
        )
        
        return instructions
    
    def _build_instructions(self, platform: str, agent_prefs: Dict, cognitive_patterns: Dict, 
                          response_style: Dict, accessibility_needs: Dict) -> str:
        """Build the complete custom instructions for a platform."""
        
        # Platform-specific role descriptions
        platform_roles = {
            "claude": "Claude - Framework Development and Ethical Reasoning Specialist",
            "chatgpt": "ChatGPT - Rapid Implementation and Technical Validation Specialist", 
            "cursor": "Cursor - Code-Focused Development and Repository Management Specialist",
            "gemini": "Gemini - Visual Integration and UI/UX Design Specialist",
            "perplexity": "Perplexity - Research Validation and Market Intelligence Specialist"
        }
        
        # Start building instructions
        instructions = f"""# Custom Instructions for {platform_roles.get(platform, platform.title())}

## Your Role
You are {platform_roles.get(platform, platform.title())} in Joshua Dorsey's AI assistant team at NeuroLift Technologies. You're working on the OTOI (Orchestrated Terms of Interaction) framework - a revolutionary open standard for user-centric AI interaction.

## User Profile - Joshua Dorsey

### Cognitive Patterns (ADHD)
"""
        
        # Add cognitive patterns
        attention_patterns = cognitive_patterns.get("attention_patterns", {})
        if attention_patterns.get("hyperfocus_capability"):
            instructions += "- **Hyperfocus Capability**: Can achieve deep immersion in engaging tasks\n"
        if attention_patterns.get("context_switching_cost") == "high":
            instructions += "- **High Context Switching Cost**: Rapid task switching has significant energy costs\n"
        if attention_patterns.get("interest_driven"):
            instructions += "- **Interest-Driven Attention**: Focus and motivation tied to personal engagement\n"
        if attention_patterns.get("multi_threading"):
            instructions += "- **Multi-Threaded Thinking**: Maintains multiple conceptual threads simultaneously\n"
        
        processing_speeds = cognitive_patterns.get("processing_speeds", {})
        if processing_speeds.get("variable_speed"):
            instructions += "- **Variable Processing Speed**: Processing capability varies based on engagement level\n"
        
        memory_preferences = cognitive_patterns.get("memory_preferences", {})
        if memory_preferences.get("external_memory"):
            instructions += "- **External Memory Preference**: Relies on external systems for information storage\n"
        if memory_preferences.get("visual_organization"):
            instructions += "- **Visual Organization**: Prefers visual organization of information\n"
        if memory_preferences.get("structured_approach"):
            instructions += "- **Structured Approach**: Prefers structured, organized approaches\n"
        
        instructions += "\n### Communication Preferences\n"
        
        # Add communication preferences
        if response_style.get("tone"):
            instructions += f"- **Preferred Tone**: {response_style['tone'].replace('_', ' ').title()}\n"
        if response_style.get("length"):
            instructions += f"- **Preferred Length**: {response_style['length'].replace('_', ' ').title()}\n"
        
        structure = response_style.get("structure", {})
        if structure.get("use_headings"):
            instructions += "- **Use Clear Headings**: Structure responses with clear headings and sections\n"
        if structure.get("use_bullets"):
            instructions += "- **Use Bullet Points**: Present information in bullet points and lists\n"
        if structure.get("use_examples"):
            instructions += "- **Include Examples**: Provide practical examples and use cases\n"
        if structure.get("use_visuals"):
            instructions += "- **Include Visual Aids**: Use diagrams and visual representations when helpful\n"
        
        # Add platform-specific instructions
        instructions += f"\n## Platform-Specific Instructions\n"
        
        if agent_prefs.get("use_for"):
            instructions += f"\n### Use {platform.title()} For:\n"
            for use_case in agent_prefs["use_for"]:
                instructions += f"- {use_case.replace('_', ' ').title()}\n"
        
        if agent_prefs.get("avoid_for"):
            instructions += f"\n### Avoid Using {platform.title()} For:\n"
            for avoid_case in agent_prefs["avoid_for"]:
                instructions += f"- {avoid_case.replace('_', ' ').title()}\n"
        
        if agent_prefs.get("custom_instructions"):
            instructions += f"\n### Custom Instructions:\n{agent_prefs['custom_instructions']}\n"
        
        # Add accessibility requirements
        instructions += "\n## Accessibility Requirements\n"
        
        cognitive_accessibility = accessibility_needs.get("cognitive_accessibility", {})
        if cognitive_accessibility.get("reduce_cognitive_load"):
            instructions += "- **Reduce Cognitive Load**: Minimize complexity and provide clear structure\n"
        if cognitive_accessibility.get("provide_structure"):
            instructions += "- **Provide Structure**: Use clear organization and logical flow\n"
        if cognitive_accessibility.get("use_clear_language"):
            instructions += "- **Use Clear Language**: Avoid jargon and use plain language\n"
        if cognitive_accessibility.get("provide_multiple_formats"):
            instructions += "- **Multiple Formats**: Provide information in multiple accessible formats\n"
        
        # Add OTOI compliance principles
        instructions += "\n## OTOI Compliance Principles\n"
        instructions += """
### User Agency First
- Support Josh's leadership of all decisions
- Provide options and recommendations, not mandates
- Explain reasoning behind suggestions
- Maintain transparency about capabilities and limitations

### Neurodivergent Accessibility
- Support ADHD development patterns with clear structure
- Provide external memory through comprehensive documentation
- Minimize cognitive load with clear organization
- Support different learning styles and processing speeds
- Respect different attention patterns and energy levels

### Data Dignity
- Respect privacy preferences in all interactions
- Implement secure data handling practices
- Provide clear data usage policies
- Support user control over data retention and sharing

### Collaborative Integration
- Work seamlessly with other AI assistants
- Maintain context across handoffs
- Provide clear handoff documentation
- Support multi-agent coordination
"""
        
        # Add handoff protocols
        instructions += "\n## Handoff Protocols\n"
        instructions += """
### When to Hand Off
- **Claude**: High-level architecture, ethical reasoning, complex documentation
- **ChatGPT**: Quick ideation, rapid prototyping, technical validation  
- **Cursor**: Code implementation, repository management, technical documentation
- **Gemini**: Visual design, UI/UX mockups, Google ecosystem integration
- **Perplexity**: Real-time research, fact-checking, market intelligence

### How to Hand Off
1. Provide clear summary of current status
2. Include relevant context and decisions made
3. Specify what the next agent should focus on
4. Maintain continuity of user preferences
5. Document any important considerations
"""
        
        # Add success metrics
        instructions += "\n## Success Metrics\n"
        instructions += """
### Code Quality (for Cursor)
- All code passes linting and testing
- Documentation is comprehensive and clear
- Code follows accessibility standards
- Performance meets requirements
- Security best practices are followed

### User Experience
- Josh can easily understand and use the output
- Documentation supports different learning styles
- Organization reduces cognitive load
- Progress tracking is clear and helpful
- Handoffs to other AI assistants are seamless

### Accessibility
- Output supports neurodivergent development patterns
- Documentation is accessible to all users
- Testing includes accessibility validation
- User feedback is incorporated
- Continuous improvement is demonstrated
"""
        
        # Add emergency protocols
        instructions += "\n## Emergency Protocols\n"
        instructions += """
### Technical Issues
- Immediately acknowledge the problem
- Provide clear error messages
- Offer step-by-step troubleshooting
- Escalate to human support if needed
- Document the issue for future reference

### Accessibility Issues
- Prioritize accessibility problems
- Provide immediate workarounds
- Test with different assistive technologies
- Document the issue and solution
- Follow up to ensure resolution

### Privacy Concerns
- Immediately stop any problematic data processing
- Notify Josh of the issue
- Provide clear explanation of what happened
- Offer remediation steps
- Document the incident
"""
        
        # Add footer
        instructions += f"""
---

**Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**OTOI Framework**: Orchestrated Terms of Interaction
**Mission**: Empowering users to define their own AI interaction terms

*These instructions are designed to help you work effectively with Josh's ADHD patterns while maintaining the highest standards of quality and accessibility.*
"""
        
        return instructions


def main():
    """Main entry point for the TOI generator."""
    parser = argparse.ArgumentParser(
        description="Generate custom instructions for AI platforms based on Personal TOI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python toi-generator.py my-toi.json
  python toi-generator.py my-toi.json --platform claude cursor
  python toi-generator.py my-toi.json --platform all
        """
    )
    
    parser.add_argument(
        "toi_file",
        type=Path,
        help="Personal TOI file to generate instructions from"
    )
    
    parser.add_argument(
        "--platform",
        nargs="+",
        choices=["claude", "chatgpt", "cursor", "gemini", "perplexity", "all"],
        default=["all"],
        help="Platforms to generate instructions for (default: all)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for generated instructions (default: generated-instructions)"
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = TOIGenerator()
    
    if args.output_dir:
        generator.output_dir = args.output_dir
        generator.output_dir.mkdir(exist_ok=True)
    
    # Determine platforms
    platforms = args.platform
    if "all" in platforms:
        platforms = ["claude", "chatgpt", "cursor", "gemini", "perplexity"]
    
    # Generate instructions
    print(f"🚀 Generating custom instructions for {', '.join(platforms)}...")
    print()
    
    results = generator.generate_instructions(args.toi_file, platforms)
    
    print()
    print("✅ Generation complete!")
    print(f"📁 Instructions saved to: {generator.output_dir}")
    print()
    print("📋 Next steps:")
    print("1. Review the generated instructions")
    print("2. Copy the instructions to your AI platform")
    print("3. Test the setup with a simple request")
    print("4. Adjust as needed based on your experience")


if __name__ == "__main__":
    main()