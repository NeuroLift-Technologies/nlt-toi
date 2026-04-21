# Contributing to OTOI Framework

Thank you for your interest in contributing to the OTOI (Orchestrated Terms of Interaction) framework! This project is designed to be accessible to contributors of all technical backgrounds, from users sharing their interaction needs to developers implementing the standard.

## 🌟 How You Can Contribute

### For Everyone

- **Share Your Needs**: Help us understand diverse interaction requirements
- **Test Templates**: Try our TOI templates and report what works or doesn't
- **Improve Documentation**: Help make our guides clearer and more accessible
- **Translate Content**: Help make OTOI available in more languages
- **Report Issues**: Let us know about bugs, unclear instructions, or missing features

### For Non-Technical Contributors

- **User Stories**: Share how you'd like to interact with AI systems
- **Accessibility Feedback**: Help us understand diverse accessibility needs
- **Template Testing**: Try our templates and suggest improvements
- **Community Building**: Help welcome new contributors and users

### For Technical Contributors

- **Code Review**: Help review pull requests for correctness and accessibility
- **Schema Development**: Improve our JSON schemas and validation
- **Tool Development**: Create tools that use the OTOI standard
- **Implementation Examples**: Show how to integrate OTOI in real applications

## 🚀 Getting Started

### 1. Choose Your Contribution Type

Pick what feels right for your skills and interests:

**Documentation & Examples** (No coding required)
- Improve existing documentation
- Create example TOI documents
- Write user guides and tutorials

**Templates & Schemas** (Light technical work)
- Improve user-friendly templates
- Enhance JSON schemas
- Create validation tools

**Code & Implementation** (Technical work)
- Reference implementations
- Integration libraries
- Developer tools

### 2. Set Up Your Environment

**For Documentation Contributors:**
- Fork this repository
- Edit files directly on GitHub or clone locally
- Submit pull requests with your changes

**For Technical Contributors:**
- Fork and clone the repository
- Install any required dependencies
- Follow our coding standards (see below)

## 📋 Contribution Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment:

- **Respectful**: Treat all contributors with respect
- **Inclusive**: Welcome diverse perspectives and experiences
- **Constructive**: Provide helpful, actionable feedback
- **Patient**: Remember that not everyone has the same technical background
- **Accessible**: Consider accessibility in all contributions

### Neurodivergent-Friendly Practices

- **Clear Instructions**: Provide step-by-step guidance
- **Multiple Formats**: Include written, visual, and video explanations when possible
- **Flexible Timelines**: No pressure for immediate responses
- **Sensory Considerations**: Avoid overwhelming layouts or busy designs
- **Processing Time**: Allow time for review and decision-making

### Documentation Standards

- **Plain Language**: Use clear, simple language when possible
- **Structure**: Use consistent headings, lists, and formatting
- **Examples**: Include concrete examples for abstract concepts
- **Accessibility**: Follow web accessibility guidelines
- **Multiple Learning Styles**: Include different ways to understand concepts

### Technical Standards

- **JSON Schema**: Use JSON Schema draft 2020-12 for validation
- **Backwards Compatibility**: Don't break existing implementations
- **Documentation**: Document all public APIs and schemas
- **Testing**: Include tests for new functionality
- **Accessibility**: Ensure tools work with assistive technologies

## 🛠️ Development Process

### For New Features or Major Changes

1. **Create an Issue**: Describe what you'd like to add or change
2. **Discuss**: Get feedback from the community
3. **Plan**: Break down the work into manageable pieces
4. **Implement**: Create your changes in a feature branch
5. **Test**: Ensure everything works as expected
6. **Document**: Update relevant documentation
7. **Submit**: Create a pull request for review

### For Bug Fixes or Small Improvements

1. **Create an Issue**: (optional for obvious bugs)
2. **Fix**: Create your changes in a feature branch
3. **Test**: Verify the fix works
4. **Submit**: Create a pull request

### Pull Request Process

1. **Clear Title**: Describe what your PR does
2. **Description**: Explain the changes and why they're needed
3. **Testing**: Describe how you tested your changes
4. **Documentation**: Update any relevant documentation
5. **Accessibility**: Note any accessibility considerations

### CI and Automation Expectations

This repository uses GitHub Actions to enforce baseline quality checks for
accessibility, schema validity, and security scanning.

- Workflow runbooks and troubleshooting:
  [`docs/development-process.md`](docs/development-process.md)
- PR format and required review metadata:
  [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md)

Before opening a PR, verify these minimum expectations:
1. Updated docs keep accessibility language clear and explicit.
2. Any changed schema/template JSON files parse correctly.
3. Security-sensitive changes include testing notes and rationale in the PR
   description.

### Local Pre-PR Checks (CI Parity)

Run these commands from repository root to reproduce the same checks locally.
Use them before opening a PR that touches the related codepaths.

#### Accessibility check parity

Use for changes under:
`docs/**`, `templates/**`, `schemas/**`, `nlt-otoi/docs/**`,
`nlt-otoi/templates/**`, `nlt-otoi/schemas/**`.

```bash
grep -r "neurodivergent\|ADHD\|autism\|accessibility" docs/ nlt-otoi/docs/
grep -r "clear\|simple\|easy\|understand" docs/ nlt-otoi/docs/
python3 nlt-otoi/tools/validators/toi-validator.py nlt-otoi/templates/personal-toi/adhd-optimized-toi.json
```

#### Schema validation parity

Use for changes under:
`schemas/**`, `nlt-otoi/schemas/**`, `nlt-otoi/templates/**`,
`nlt-otoi/tools/validators/**`.

```bash
python - <<'PY'
import glob, json, sys
paths = glob.glob('schemas/**/*.json', recursive=True)
paths += glob.glob('nlt-otoi/schemas/**/*.json', recursive=True)
paths += glob.glob('nlt-otoi/templates/**/*.json', recursive=True)
errors = []
for path in paths:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            json.load(f)
    except Exception as exc:
        errors.append((path, exc))
if errors:
    for path, exc in errors:
        print(f'Invalid JSON: {path}: {exc}')
    sys.exit(1)
print('All schema/template JSON files parse successfully.')
PY
```

#### Security scan parity

Use for changes under:
`src/**`, `nlt-otoi/tools/**`, `schemas/**`, `nlt-otoi/schemas/**`.

```bash
python3 -m pip install bandit
python3 -m bandit -r src/ nlt-otoi/tools/ -f json -o /tmp/bandit-report.json --exit-zero
python3 - <<'PY'
import json, sys
with open('/tmp/bandit-report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)
high = [r for r in report.get('results', []) if r.get('issue_severity') == 'HIGH']
if high:
    print(f'HIGH findings: {len(high)}')
    sys.exit(1)
print('No HIGH Bandit findings.')
PY
```

## 🎯 Priority Areas

We especially welcome contributions in these areas:

### High Priority
- Real-world example TOI documents
- Accessibility improvements
- User-friendly documentation
- Translation into other languages

### Medium Priority
- Tool integrations and plugins
- Additional schema validation
- Performance improvements
- Extended examples and use cases

### Future Considerations
- Mobile app integration
- Voice interface considerations
- AR/VR interaction patterns
- IoT device integration

## 📝 Issue Templates

When creating issues, please use our templates:

- **Bug Report**: For reporting problems
- **Feature Request**: For suggesting new features
- **Documentation**: For documentation improvements
- **Accessibility**: For accessibility-related issues
- **Question**: For asking questions about usage

## 🤝 Community Guidelines

### Communication Channels

- **GitHub Issues**: For bugs, features, and technical discussion
- **GitHub Discussions**: For general questions and community chat
- **Email**: For sensitive or private matters

### Response Times

- **Issues**: We aim to respond within 1-2 business days
- **Pull Requests**: Initial review within 3-5 business days
- **Questions**: Usually answered within 1 business day

### Getting Help

Stuck? Here are ways to get help:

1. **Check Documentation**: Look through our guides and examples
2. **Search Issues**: See if your question has been asked before
3. **Ask in Discussions**: Post in GitHub Discussions
4. **Create an Issue**: For specific bugs or feature requests

## 🏆 Recognition

We believe in recognizing all types of contributions:

- **Contributors List**: All contributors are listed in our README
- **Special Recognition**: Outstanding contributions get special mention
- **Community Roles**: Active contributors may be invited to help moderate
- **Speaking Opportunities**: We'll help promote your work in the community

## 📚 Resources

### For New Contributors
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Markdown Guide](https://www.markdownguide.org/)
- [JSON Schema Tutorial](https://json-schema.org/learn/)

### For Understanding OTOI
- [Framework Overview](/docs/framework-overview.md)
- [Implementation Guide](/docs/implementation-guide.md)
- [Best Practices](/docs/best-practices.md)

### Accessibility Resources
- [Web Content Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/WCAG21/quickref/)
- [Inclusive Design Principles](https://inclusivedesignprinciples.org/)
- [Neurodiversity Design Guidelines](https://neurodiversity.design/)

## 📞 Contact

- **General Questions**: Create a GitHub Discussion
- **Security Issues**: Email [security@neurolift.otoi] (when available)
- **Partnership Inquiries**: Email [partnerships@neurolift.otoi] (when available)

---

**Thank you for helping make AI interaction more accessible, respectful, and user-controlled!**

*This contributing guide is a living document. If you have suggestions for improvement, please contribute them!*