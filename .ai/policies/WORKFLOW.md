# Canonical agent workflow

This file owns the lifecycle. Role files contain only role-specific responsibilities.

## Operating model

Use one active requirement per Git branch or worktree. Planning another feature while implementation is active requires another branch/worktree. `CURRENT_PLAN.md` therefore remains a single compact pointer.

The normal role sequence is:

```text
planner → implementer → independent reviewer
                    ↖ remediation ↙
                 curation and closeout
```

Testing, security, and documentation are review lenses. Use a separate specialist context only for significant risk or an explicit project requirement.

## 1. Intake and classification

The planner reads the requirement, project configuration, current context, applicable ADRs, and relevant existing code/tests. Record the change class:

- `trivial`: mechanical and behavior-neutral;
- `normal`: bounded behavioral work;
- `significant`: initial project, subsystem, public API, migration, sensitive security/privacy work, major integration, or broad ambiguity.

Material uncertainty moves work upward, not downward.

## 2. Discovery and durable specification

For significant or materially unclear work, use `FEATURE_DISCOVERY.md`. Resolve the problem, users, workflows, scope, domain rules, data, interfaces, risks, operations, and acceptance criteria one decision branch at a time. Ask only questions that can materially change the outcome and obtain explicit shared-understanding confirmation.

Create the accepted specification at:

```text
docs/specifications/<requirement-id>.md
```

The specification is durable and owns observable behavior, accepted decisions, scope, acceptance criteria, and stable test seams. New architecture decisions become proposed ADRs during planning and must be accepted before dependent implementation begins.

Implementation may begin only when significant specifications contain:

```text
Status: ready-for-implementation
Ready for implementation: yes
```

## 3. Temporary implementation planning

For normal and significant work create:

```text
.ai/work/<requirement-id>/
├── PLAN.md
└── tasks/                 # only for independently implementable units
```

The plan owns implementation approach, sequencing, affected areas, risks, verification, migration/rollback, and documentation changes. It links to rather than duplicates the durable specification. Update `CURRENT_PLAN.md`.

Planner task statuses are `draft` or `ready`.

## 4. Implementation

The implementer selects a `ready` task, marks it `in-progress`, and implements the smallest coherent behavior slice. Tests change with behavior. After code and tests are complete, mark the task `implemented`; after focused checks pass, mark it `verified`.

Update the plan before material deviations. Do not silently expand scope.

## 5. Full verification

Run:

```bash
./.ai/tools/verify.sh
```

Every configured mandatory gate must execute and pass. Record the exact commands and results in the plan/task handoff. A mandatory skip is a failure.

## 6. Independent review and remediation

Use a fresh reviewer context for normal and significant work. The reviewer compares the requirement, durable specification, accepted ADRs, plan, complete diff, tests, verification evidence, and affected documentation.

The reviewer records findings in `.ai/work/<requirement-id>/REVIEW.md` or directly in the pull request. Verified tasks may become `reviewed`. Findings return affected tasks to `in-progress` or `blocked`.

The implementer remediates findings and reruns focused and full verification. `P0` and `P1` fixes require a fresh reviewer pass.

## 7. Curation and closeout

Only after review is satisfied:

1. reconcile current-state documentation with the final code;
2. ensure accepted architecture decisions are in ADRs;
3. move unresolved work to issues or `NEXT_STEPS.md`;
4. run `./.ai/tools/check-docs.py` and final `./.ai/tools/verify.sh`;
5. record outcome, verification, residual risks, and dependency changes in the pull request;
6. mark reviewed tasks `done`;
7. remove the temporary work directory after durable information is transferred;
8. reset `CURRENT_PLAN.md` to idle.

The accepted requirement, specification, ADRs, code, tests, maintained documentation, and pull request are the lasting record. Temporary task history is not retained merely as documentation.

## Status model

```text
draft → ready → in-progress → implemented → verified → reviewed → done
```

`blocked` may be used from an active state with a concrete blocking condition.

## External reference decision

Consult the configured engineering-knowledge MCP only for a concrete unresolved architecture, security, privacy, accessibility, public-interface, integration, or dependency decision when local guidance is insufficient. Record source identifiers and adopted conclusions in the durable specification or ADR. Do not store broad excerpts.
