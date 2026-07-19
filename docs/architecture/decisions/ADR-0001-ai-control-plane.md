# ADR-0001: Isolate the agent control plane under `.ai/`

- Status: accepted
- Date: 2026-07-19
- Decision owners: project owner
- Related requirement: `docs/specifications/REQ-ai-control-plane-layout.md`

## Context

The template previously placed agent configuration, tooling, and workflow material
in application-owned root namespaces. Real applications commonly need those
namespaces for their own configuration, scripts, and documentation.

## Decision

Place the generic agent control plane under `.ai/`, split by configuration, tools,
policies, roles, templates, and temporary work. Keep root `AGENTS.md` as the discovery
entry point and keep JetBrains-specific files in `.aiassistant/`.

Durable product knowledge remains visible under `docs/requirements/`,
`docs/specifications/`, and `docs/architecture/`. Human-facing repository files such
as `README.md` and `SECURITY.md` remain at the root when present.

## Consequences

- Application-owned `config/`, `scripts/`, and documentation namespaces remain free.
- CI and contributors use explicit `.ai/tools/*` commands.
- Project linters and scanners must deliberately include or exclude `.ai/` according
  to whether they validate application code or the control plane.
- Every path reference must migrate atomically; compatibility aliases are not retained.
