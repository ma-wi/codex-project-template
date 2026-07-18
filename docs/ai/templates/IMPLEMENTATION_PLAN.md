# Implementation plan: <title>

- Status: draft | accepted | in-progress | blocked | completed
- Requirement:
- Accepted specification:
- Specification status: ready-for-implementation | not-required
- Work directory:
- Owner/agent:
- Last updated:

## Discovery basis

- Discovery artifact, if used:
- Shared understanding confirmed by:
- Confirmation date:
- Remaining accepted assumptions:

## Problem and desired outcome

## Optional user stories or journey scenarios

Use only when they clarify user-visible behavior. Keep each story tied to acceptance criteria. Omit this section for purely technical work.

| ID | Actor | Goal or scenario | Value/outcome | Acceptance criteria |
|---|---|---|---|---|
| US-1 | | | | AC-1 |

## Scope

### In scope

### Out of scope / non-goals

## Current-state findings

## Facts, assumptions, and open questions

### Confirmed facts

### Assumptions

### Open questions or blockers

## Instruction capture

| User instruction | Classification | Persistent location or temporary scope |
|---|---|---|
| | requirement / task-only / rule / ADR / constraint / future work | |

## External reference assessment

- MCP consultation required: yes | no
- Reason:
- Narrow topics or questions:
- Retrieved source identifiers:
- Adopted guidance and project-specific adaptation:

## Test seams inherited from the specification

- Primary seam:
- Secondary seams:
- Seams deliberately avoided:
- Any justified deviation from the specification:

## Proposed approach

## Affected areas

- Components and files:
- Public interfaces:
- Data and migrations:
- Dependencies:
- Configuration:
- Deployment and operation:
- Documentation:

## Implications and risks

- Compatibility:
- Security and privacy:
- Performance and capacity:
- Accessibility and UX:
- Observability:
- Rollback and recovery:

## Work items

Create separate files under `tasks/` only for independently implementable or verifiable work. Keep small subtasks here.

| ID | Title | Status | Depends on | Task file |
|---|---|---|---|---|
| T001 |  | draft | none | `tasks/T001-<slug>.md` |

## Acceptance criteria traceability

| Criterion | Work item | Verification evidence |
|---|---|---|
| AC-1 | T001 | Test or command |

## Test strategy

Tests should exercise the agreed stable seams and avoid coupling to private implementation details.

- Unit:
- Integration:
- End-to-end:
- Regression:
- Manual verification exception, if any:

## Verification plan

```bash
./scripts/check-work-state.py
./scripts/format.sh --check
./scripts/lint.sh
./scripts/test.sh
./scripts/check-dependencies.sh
./scripts/security.sh
./scripts/build.sh
./scripts/verify.sh
```

Additional project-specific checks:

## Documentation plan

## Closeout plan

- Durable decisions to convert to ADRs:
- Current-state documentation to update:
- Potential follow-up issues:
- Temporary artifacts to remove before merge:

## Deviations discovered during implementation

Record only material deviations and update the affected sections above.
