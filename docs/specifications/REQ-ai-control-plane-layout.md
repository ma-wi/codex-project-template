# AI control-plane layout

- Status: ready-for-implementation
- Ready for implementation: yes

## Outcome

Agent configuration, workflow state, policies, roles, templates, and supporting
tooling live under a dedicated `.ai/` namespace so they cannot collide with an
application's conventional `config/`, `scripts/`, or agent-documentation paths.

## Observable behavior

- `AGENTS.md` remains the root discovery entry point.
- `.ai/project.yaml` contains project choices.
- `.ai/config/` contains agent/tool policy configuration and generated/local gate settings.
- `.ai/tools/` contains bootstrap, verification, quality, and template-copy tooling.
- `.ai/policies/`, `.ai/roles/`, `.ai/templates/`, and `.ai/work/` own agent workflow material.
- `.ai/CURRENT_PLAN.md`, `.ai/NEXT_STEPS.md`, `.ai/PROJECT_CONTEXT.md`, and `.ai/DECISIONS.md` remain compact agent state/context.
- Accepted requirements, specifications, architecture documentation, and ADRs remain under `docs/` as durable project knowledge.
- `.aiassistant/` remains separate because it is the JetBrains integration namespace.
- CI, bootstrap, copy commands, checks, links, tests, and generated documentation use only the new paths.

## Acceptance criteria

- Copied projects contain the agent control plane only under `.ai/` and leave application-owned root namespaces free.
- All agent tooling works from `.ai/` on Linux and Windows copy paths.
- Repository-wide searches find no obsolete live references to the old locations.
- Project quality commands do not accidentally treat `.ai/` tooling as application code.
- Full template verification and independent review pass.

## Test seams

- Primary: template integration tests over bootstrap, lifecycle, copy boundary, and configured-project verification.
- Secondary: repository-wide stale-path search and generated project manifest inspection.
