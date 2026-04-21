# Security Policy

## Supported Versions

The following versions of the OTOI Framework are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously, especially given that the OTOI Framework handles sensitive user preference data and privacy settings.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by:

1. **GitHub Security Advisories** (preferred): Use the [Security tab](../../security/advisories/new) in this repository to create a private advisory
2. **Email**: Contact the maintainers directly with details of the vulnerability

### What to Include

When reporting a vulnerability, please include:

- **Type of issue** (e.g., data exposure, injection, authentication bypass, etc.)
- **Location**: File paths, function names, or URLs related to the vulnerability
- **Reproduction steps**: Step-by-step instructions to reproduce the issue
- **Impact**: Describe what an attacker could accomplish with this vulnerability
- **Suggested fix** (optional): If you have ideas for how to fix it

### Response Timeline

- **Acknowledgment**: Within 48 hours of receiving your report
- **Initial Assessment**: Within 5 business days
- **Fix Development**: Depends on severity — critical issues within 7 days, others within 30 days
- **Public Disclosure**: Coordinated with the reporter after a fix is available

## Security Considerations for TOI Data

The OTOI Framework handles sensitive user data including:

- **Personal preferences** and cognitive styles
- **Privacy settings** and data sharing consent
- **Accessibility needs** and neurodivergent accommodations
- **Collaboration protocols** and communication preferences

### Privacy-First Principles

- TOI documents should be treated as sensitive personal data
- Never log or expose TOI content in error messages or debug output
- Validate all TOI input before processing
- Respect the `data_retention` and `sharing_consent` fields specified in TOI documents
- Third-party integrations must honor `third_party_access` settings

### Schema Validation Security

- Always validate TOI documents against the official JSON schema before processing
- Reject documents with unexpected additional properties when using strict mode
- Be cautious with user-controlled schema references

## Scope

This security policy covers:

- The OTOI Framework core schemas (`schemas/`)
- Validation and generation tools (`tools/`)
- Python framework code (`src/`)
- Documentation that could expose security-sensitive information

## Out of Scope

- Third-party integrations and platforms using the framework
- User-generated TOI documents (though we accept reports about schema design flaws)
- Social engineering attacks

## Recognition

We appreciate security researchers who responsibly disclose vulnerabilities. With your permission, we will acknowledge your contribution in our security advisory.
