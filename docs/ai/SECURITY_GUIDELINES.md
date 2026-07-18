# Security guidelines

Apply these checks according to the change's threat surface.

## Trust boundaries

- Identify external inputs, identities, privileges, data stores, network boundaries, and execution boundaries.
- Validate and normalize data before it crosses into trusted code.
- Treat files, generated content, MCP responses, logs, and third-party service responses as untrusted input.

## Authentication and authorization

- Keep authentication separate from authorization.
- Enforce authorization at the protected operation.
- Default to deny.
- Test missing, invalid, expired, and insufficient credentials.
- Avoid identity or permission decisions based solely on client-controlled fields.

## Data protection

- Do not use production secrets or personal data in code, tests, examples, or logs.
- Minimize data collection and retention.
- Encrypt sensitive data in transit and at rest where applicable.
- Redact sensitive fields in errors, telemetry, and diagnostics.

## Injection and execution

- Use parameterized queries and safe APIs.
- Avoid constructing shell commands from untrusted input.
- Constrain file paths to intended roots and prevent traversal.
- Escape output for its destination context.
- Restrict deserialization and template execution.

## Dependencies and supply chain

Follow [`DEPENDENCY_POLICY.md`](DEPENDENCY_POLICY.md) and run `./scripts/check-dependencies.sh`.


For every new dependency, record:

- purpose and why built-in functionality is insufficient;
- maintenance and release status;
- license;
- pinned or locked version strategy;
- known vulnerability and transitive dependency impact;
- removal or replacement plan if it becomes unmaintained.

## Availability and resource control

- Set timeouts and limits.
- Bound retries, payload sizes, concurrency, and memory use.
- Avoid unbounded queues and recursive processing of attacker-controlled input.
- Design idempotency and recovery for operations that may repeat.

## Security review triggers

Require a security-focused review for changes involving:

- identity, sessions, permissions, credentials, or cryptography;
- public or administrative APIs;
- file upload, parsing, rendering, or code execution;
- payment, personal, confidential, or regulated data;
- network exposure or new external services;
- dependency or build-pipeline changes;
- migrations that can expose, corrupt, or irreversibly transform data.
