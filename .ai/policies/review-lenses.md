# Conditional review lenses

Load only the sections relevant to the change.

## Security and privacy

Inspect trust boundaries, authentication, authorization, secrets, personal data, logging, injection, path traversal, unsafe parsing/execution, cryptography, sessions, dependencies, resource exhaustion, insecure defaults, rollback, and operational exposure. Use a separate security reviewer for significant changes to these areas.

## Verification

Confirm tests would detect the intended defect and cover relevant negative, boundary, permission, migration, and recovery behavior. Reproduce failures and record exact commands and environment limitations.

## Documentation

Confirm README, contributor, architecture, ADR, API, operational, security, `.ai/PROJECT_CONTEXT.md`, `.ai/CURRENT_PLAN.md`, and `.ai/NEXT_STEPS.md` content matches current truth. Run `./.ai/tools/check-docs.py`; errors block completion and warnings require an explicit disposition.

## Dependencies and supply chain

Confirm necessity, alternatives, maintainer/provenance, release activity, license, install scripts, transitive risk, vulnerabilities, version/lock strategy, and replacement plan. Review manifest and lockfile diffs and run `./.ai/tools/check-dependencies.sh`.
