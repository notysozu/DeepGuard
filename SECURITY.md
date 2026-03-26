# Security Policy

## Supported Versions

This repository is currently maintained on the default branch only. Security
fixes are expected to land there first.

## Reporting a Vulnerability

Please do not open a public issue for suspected security vulnerabilities.

Instead, report issues privately to:

- `SECURITY_CONTACT_PLACEHOLDER`

When reporting, include:

- A clear description of the issue
- Reproduction steps or proof of concept
- The affected area or file paths
- Any suggested mitigation if available

We will acknowledge receipt as soon as practical, investigate, and coordinate a
responsible fix and disclosure plan.

## Secrets and Sensitive Data

- Never commit real API keys, credentials, or private datasets.
- Use `.env` for local secrets and keep `.env.example` scrubbed.
- Review installer scripts before using pipe-to-shell commands.
