# Agent workflow

## Phase 0: Planning-mode selection

Read `planning.mode` from `config/ai-project.yaml`:

- `interview`: use structured discovery;
- `synthesize`: convert already supplied, confirmed conversation and repository context into a specification without repeating answered questions;
- `auto`: select interview mode when material decisions remain unclear, otherwise synthesize.

Synthesis must not invent missing product or architecture decisions. Material gaps remain blockers or explicit assumptions.

## Phase 1: Discovery interview when required

Use this phase for an initial project, major subsystem, broad feature, or materially ambiguous requirement. Create:

```text
docs/ai/work/<requirement-id>/DISCOVERY.md
```

Use `docs/ai/templates/FEATURE_DISCOVERY.md`. Resolve decision dependencies one branch at a time. For each material question, give a recommended answer and trade-offs. Keep the artifact concise by recording decisions and unresolved points rather than a conversation transcript.

The phase ends only when:

- the problem, users, desired outcomes, main workflows, scope, non-goals, constraints, and success criteria are understood;
- material contradictions and blocking decisions are resolved;
- remaining uncertainty is explicitly accepted as an assumption or delegated implementation detail;
- the user explicitly confirms shared understanding.

Do not implement during discovery. After confirmation, use the accepted discovery result as input to specification.

## Phase 2: Intake and specification

Inputs:

- requirement, issue, or task;
- repository instructions;
- relevant project context.

Required output:

- normalized problem statement;
- testable acceptance criteria;
- explicit scope and non-goals;
- identified ambiguities, assumptions, and blockers.

For significant features, create:

```text
docs/ai/work/<requirement-id>/SPEC.md
```

Use `docs/ai/templates/FEATURE_SPEC.md`. Inspect applicable ADRs and existing domain terminology before writing it. The specification defines stable behavior, durable decisions, acceptance criteria, and primary/secondary test seams. It should avoid volatile file-level implementation detail.

The phase ends with `Status: ready-for-implementation` and `Ready for implementation: yes`. If confirmation is required, use `awaiting-confirmation` until the decision owner confirms it. Do not implement while material requirements remain contradictory, unsafe, or unconfirmed.

## Phase 3: Repository inspection and implementation planning

Inspect relevant code, tests, configuration, architecture, and local instructions before proposing changes.

For non-trivial work, create:

```text
docs/ai/work/<requirement-id>/
├── SPEC.md
├── PLAN.md
└── tasks/
    ├── T001-<slug>.md
    └── T002-<slug>.md
```

Derive `PLAN.md` from the ready specification using `docs/ai/templates/IMPLEMENTATION_PLAN.md` and `docs/ai/templates/WORK_ITEM.md` for independently implementable tasks. Keep small subtasks directly in the plan rather than creating excessive task files.

Update `docs/ai/CURRENT_PLAN.md` to point to the requirement, work directory, plan, phase, and current task. Complete the external-reference assessment in `PLAN.md`. Query the standards MCP only for concrete unresolved decisions.

The planner may set task status only to `draft` or `ready`.

Required output:

- optional user stories or journey scenarios only when they clarify user-visible behavior;
- affected components and interfaces;
- task decomposition and dependencies;
- acceptance-criteria traceability;
- risks and implications;
- test strategy and explicit stable test seams;
- verification commands;
- documentation updates;
- rollback or recovery approach where relevant.

## Phase 4: Implementation

The implementer selects a `ready` task, changes it to `in-progress`, and implements the smallest coherent solution. Add tests with the behavior change. Run focused checks after each meaningful work unit, not after every file read or intermediate edit.

A meaningful work unit is a completed behavior slice, refactoring step, migration step, or defect fix that can be checked independently.

After code and tests are complete, set the task to `implemented`. After its required focused checks pass, set it to `verified`. Record concise result evidence in the task file.

If implementation invalidates the plan, update `PLAN.md` before continuing. Do not silently expand scope.

## Phase 5: Verification

Run focused checks first, then the full verification command:

```bash
./scripts/verify.sh
```

The work-state gate validates the active plan pointer and task statuses. Record exact commands, pass/fail status, and skipped checks. A skipped mandatory check leaves the work incomplete.

## Phase 6: Independent review

Use a fresh agent context where practical. The reviewer reads the requirement, accepted `SPEC.md` when present, active `PLAN.md`, task files, diff, tests, and relevant documentation. The reviewer verifies that agreed test seams are exercised and that tests do not unnecessarily couple to private implementation details. The reviewer may use the MCP only under the conditions in `AGENTS.md`.

Write the result to:

```text
docs/ai/work/<requirement-id>/REVIEW.md
```

Use `docs/ai/templates/REVIEW_REPORT.md`. A successful reviewer may advance verified tasks to `reviewed`. Findings return affected tasks to `in-progress` or `blocked`.

## Phase 7: Remediation

The implementer addresses findings, updates affected task files, re-runs focused checks, and then runs the complete verification suite. A fresh review verifies fixes for `P0` and `P1` findings.

## Phase 8: Closeout

Create `CLOSEOUT.md` from `docs/ai/templates/WORK_CLOSEOUT.md` and confirm:

- every required task is `reviewed` and then marked `done`;
- every acceptance criterion has implementation and verification evidence;
- no unresolved `P0` or `P1` finding remains;
- durable decisions were transferred to ADRs;
- current-state documentation is accurate;
- unresolved work was moved to `NEXT_STEPS.md` or an issue;
- full verification passed.

Keep temporary work artifacts through final review. Before final merge, delete the completed work directory after all durable information has been transferred, unless the project explicitly chooses to retain it. Reset `CURRENT_PLAN.md` to its idle state.

Git history and the pull request retain the planning and review trail. Do not keep verbose task history in permanent documentation.


## Phase 9: Knowledge curation

For significant work or when configured in `config/ai-project.yaml`, use `docs/ai/agents/documentation-curator.md` before final cleanup. Classify durable user instructions, reconcile documentation with the final code and CI configuration, run `./scripts/check-docs.py`, and transfer durable information to canonical documents.

Do not preserve temporary plans or reviews merely as documentation history. Do not delete unresolved constraints, migration knowledge, security findings, or decisions that have not been transferred. Record the audit in `CLOSEOUT.md` or use `docs/ai/templates/KNOWLEDGE_AUDIT.md`.
