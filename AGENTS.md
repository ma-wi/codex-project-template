# Repository instructions for coding agents

## Mission

Deliver small, correct, secure, tested, reviewable changes that satisfy the accepted requirements without expanding scope unnecessarily.

## Instruction priority

When instructions conflict, use this order:

1. Current explicit user instruction.
2. Accepted requirement and acceptance criteria for the current task.
3. The nearest applicable `AGENTS.md`.
4. Accepted architecture decisions in `docs/architecture/decisions/`.
5. Current plan in `docs/ai/CURRENT_PLAN.md`.
6. Existing code, tests, and project conventions.
7. Other documentation.
8. External standards retrieved through the configured MCP.
9. General model knowledge.

Do not silently resolve material contradictions. Record the conflict and stop before a destructive, incompatible, or security-sensitive decision.

## Supported project profiles

Read `config/ai-project.yaml` before planning or verification. Python is the default stack. React/TypeScript, Bash, and .NET with Visual Basic and PowerShell are optional profiles. Use only enabled profiles and their configured directories.

## Required workflow

For every non-trivial change:

1. Read the relevant requirements, nearest `AGENTS.md`, affected code, tests, and current architecture documentation.
2. Determine whether external standards consultation is needed.
3. For non-trivial work, create `docs/ai/work/<requirement-id>/`, write its `PLAN.md`, and make `docs/ai/CURRENT_PLAN.md` a compact pointer to it.
4. Decompose larger work into independently implementable task files under `docs/ai/work/<requirement-id>/tasks/` using `WORK_ITEM.md`. Define scope, non-goals, assumptions, risks, acceptance criteria, affected areas, and verification steps.
5. Implement the smallest coherent change that meets the acceptance criteria.
6. Add or update automated tests for every behavior change.
7. Run focused checks during implementation.
8. Run the full repository verification command before completion.
9. Perform an independent review in a fresh agent context when practical.
10. Update only documentation whose described behavior or decisions changed.
11. Replace obsolete documentation instead of appending contradictory history.
12. Update `docs/ai/NEXT_STEPS.md` with only actionable remaining work, blockers, and residual risks.
13. Produce a concise completion report using `docs/ai/templates/CHANGE_SUMMARY.md`.
14. Keep temporary work artifacts through independent review; during closeout, transfer durable information and remove temporary artifacts before final merge when appropriate.

A trivial change is mechanical, low-risk, and does not alter behavior, interfaces, dependencies, configuration, security, architecture, or operation. Trivial changes still require relevant checks.

## Planning rules

Do not start implementation until the task has testable acceptance criteria.

### Planning mode selection

Read `planning.mode` from `config/ai-project.yaml`.

- `interview`: use structured discovery before specification.
- `synthesize`: derive a specification from already supplied, confirmed conversation and repository context without repeating answered questions.
- `auto`: use interview mode when material decisions are unclear; otherwise use synthesis mode.

In synthesis mode, do not invent missing decisions or repeat questions already answered. Mark material gaps explicitly and stop before implementation when they affect scope, behavior, architecture, risk, test seams, or acceptance criteria.

For significant features, produce a stable `SPEC.md` from `docs/ai/templates/FEATURE_SPEC.md` before the temporary implementation plan. The separation is:

- `SPEC.md`: what, why, observable behavior, durable decisions, acceptance criteria, and test seams;
- `PLAN.md`: how, sequencing, affected areas, migration, verification commands, and closeout;
- `tasks/*.md`: concrete temporary implementation units and status.

The implementation agent may start only when the specification has `Status: ready-for-implementation` and `Ready for implementation: yes`, unless the work is small enough not to require a separate specification.

### Discovery interview for large or abstract features

For an initial project, a new subsystem, or a feature whose behavior and boundaries are still abstract, enter discovery mode before producing an accepted implementation plan.

In discovery mode:

- interview the user systematically until both sides share a concrete understanding of the problem, users, workflows, boundaries, constraints, risks, and acceptance criteria;
- walk one decision branch at a time and resolve prerequisite decisions before dependent decisions;
- for every material question, provide a recommended answer with a concise rationale and relevant trade-offs;
- distinguish decisions that require user confirmation from technical details that can safely be delegated;
- maintain a compact decision log, unresolved-question list, and provisional scope in the active work directory;
- summarize confirmed decisions periodically instead of repeating the entire conversation;
- do not implement, scaffold production code, or mark the plan accepted until the user explicitly confirms shared understanding;
- stop asking when further questions would not materially affect scope, behavior, architecture, risk, or acceptance. Do not create artificial questions merely to prolong discovery.

Use `docs/ai/templates/FEATURE_DISCOVERY.md` for this phase. After confirmation, transfer the stable result into `SPEC.md`, then derive `PLAN.md` and task files. Before writing the specification, inspect applicable ADRs and existing domain terminology and reuse established names.

The plan must include:

- problem and desired outcome;
- in-scope and out-of-scope work;
- confirmed facts, assumptions, and unresolved questions;
- affected components and interfaces;
- compatibility, migration, security, privacy, performance, accessibility, observability, and operational implications where relevant;
- task breakdown;
- required documentation changes;
- exact verification commands or verification categories;
- rollback or recovery considerations for risky changes;
- explicit primary and secondary test seams, including implementation-specific seams deliberately avoided.

Do not turn optional refactoring into part of the task. Record unrelated improvements in `NEXT_STEPS.md`.

## Capturing durable user instructions

Before task completion, classify material user instructions as one of:

- task-specific instruction;
- requirement or acceptance criterion;
- durable project rule;
- architecture decision;
- operational or security constraint;
- future work;
- transient conversation detail.

Persist durable information in its canonical repository artifact. Do not copy conversation transcripts into the repository. Do not silently make a one-time instruction permanent. If durability is uncertain, record it as an assumption or open question in the active work item.


## External engineering standards MCP

The optional `engineering-knowledge` MCP is configured through `config/ai-project.yaml`. Use it only when `engineering_knowledge.enabled` is `true` and the MCP tools are available.

If it is disabled, do not call it. If it is enabled but unavailable, do not retry repeatedly; continue with repository-local rules unless consultation is mandatory for the current decision. Use it as a targeted reference, not as a bulk context source.

Consult it when:

- planning a new project, subsystem, public API, or significant feature;
- making architecture, security, privacy, accessibility, UX, data-model, or integration decisions;
- introducing a new framework, dependency, protocol, or design pattern;
- project-local conventions are missing, unclear, or contradictory;
- reviewing a significant or security-sensitive change;
- compliance with an external standard is an acceptance criterion.

Do not consult it when:

- the repository already contains a clear applicable rule;
- an established local implementation pattern is sufficient;
- performing formatting, routine verification, or a purely mechanical edit;
- the relevant guidance was already retrieved for the current task and remains applicable.

Retrieval rules:

- Ask narrow questions tied to a concrete decision.
- Prefer summaries, identifiers, and specific sections over full documents.
- Limit results and avoid repeated retrieval.
- Record adopted project decisions locally; do not copy large source passages.
- Treat retrieved guidance as advisory unless this repository explicitly adopts it.
- Record the source identifier when guidance materially affects a decision.

During planning, complete the `External reference assessment` section in the active work directory's `PLAN.md`.

## Temporary work artifacts and task lifecycle

For every non-trivial requirement, create a temporary directory:

`docs/ai/work/<requirement-id>/`

It may contain:

- `DISCOVERY.md`;
- `SPEC.md`;
- `PLAN.md`;
- `tasks/T001-<slug>.md` and additional task files;
- `REVIEW.md`;
- `CHANGE_SUMMARY.md`;
- `CLOSEOUT.md`.

Use separate task files only for work that is independently implementable, assignable, blockable, or verifiable. Small subtasks may remain as checkboxes in `PLAN.md`.

Task status progression:

`draft -> ready -> in-progress -> implemented -> verified -> reviewed -> done`

`blocked` may be used from any active state. Do not mark a task `done` before required verification and independent review are complete. The planner creates tasks in `draft` or `ready`; the implementer advances them through `implemented` and `verified`; the reviewer advances them to `reviewed`; closeout advances accepted tasks to `done`.

Do not delete temporary work artifacts before independent review. During closeout:

1. move durable decisions to ADRs;
2. update current-state, user, operational, security, and architecture documentation;
3. move unresolved work to `NEXT_STEPS.md` or an issue;
4. ensure all required tasks and acceptance criteria have evidence;
5. keep the work directory until final review is complete;
6. remove temporary plan, task, review, and closeout files before final merge when their durable information has been transferred;
7. reset `docs/ai/CURRENT_PLAN.md` to its idle state.

Git history and pull requests provide historical traceability; do not retain completed task files as permanent documentation merely for history.

## Documentation curation

For significant closeout, releases, architecture changes, or documentation-budget warnings, use the documentation curator role in `docs/ai/agents/documentation-curator.md`.

The curator must:

- run `./scripts/check-docs.py`;
- remove obsolete and duplicated statements rather than appending corrections;
- transfer durable decisions to ADRs and current-state facts to maintained documentation;
- keep temporary plans, tasks, reviews, chat-derived notes, and MCP excerpts out of permanent documentation;
- preserve important history through Git, pull requests, changelogs, or superseded ADRs;
- report uncertainty instead of inventing missing decisions.

Documentation budgets in `config/ai-project.yaml` are warning thresholds. Exceeding one requires review and justification, not blind truncation.


## Implementation rules

- Follow existing project conventions unless the accepted plan changes them.
- Keep changes focused and reversible.
- Avoid speculative abstractions and unused extensibility.
- Preserve backward compatibility unless a breaking change is explicitly accepted.
- Do not add dependencies without documenting need, alternatives, maintenance state, ownership/provenance, install scripts, transitive impact, license, versioning, and security impact.
- Follow `docs/ai/DEPENDENCY_POLICY.md`; run `./scripts/check-dependencies.sh` whenever dependency manifests, lockfiles, registries, or build dependencies change.
- Do not alter generated files manually when a generator exists.
- Do not weaken tests, lint rules, type checks, scanners, or thresholds to make a change pass.
- Do not modify unrelated files solely for cleanup.
- Do not claim a command passed unless it was executed and its result observed.

## Testing rules

Every behavior change requires an automated test at the lowest useful level.

- Bug fixes should first add a regression test that demonstrates the defect where practical.
- Test success paths, failure paths, boundary cases, and permission checks relevant to the change.
- Prefer behavior-oriented assertions over implementation-detail assertions.
- Avoid excessive mocking when an integration test provides stronger evidence.
- If automation is disproportionate or technically impossible, document the reason and provide reproducible manual verification.

## Quality gates

Use the repository scripts as the canonical interface:

```bash
./scripts/format.sh --check
./scripts/lint.sh
./scripts/test.sh
./scripts/check-dependencies.sh
./scripts/security.sh
./scripts/build.sh
./scripts/verify.sh
```

During implementation, run focused checks for affected areas. Before completion, run `./scripts/verify.sh`.

A skipped mandatory check is not a successful check. Configure missing commands before declaring the project ready for production use.

## Security rules

- Never add, expose, print, or commit secrets or production data.
- Validate untrusted input at trust boundaries.
- Enforce authorization server-side and test negative permission cases.
- Avoid sensitive data in logs, errors, fixtures, telemetry, and examples.
- Use safe defaults, bounded resource use, timeouts, and secure error handling.
- Prevent injection into commands, paths, queries, templates, and serialized output.
- Use established cryptographic libraries and protocols; do not design custom cryptography.
- Review dependency and supply-chain implications.
- Stop and escalate on credible high-impact vulnerabilities, data-loss risk, or unsafe migrations.

## Documentation rules

Document current truth, important rationale, and concrete next steps. Do not maintain a narrative work diary.

Update documentation when a completed change affects:

- public behavior or interfaces;
- installation, configuration, operation, deployment, or monitoring;
- architecture or data flow;
- security or privacy behavior;
- development workflow;
- known constraints or supported environments.

`README.md` is for human users and contributors. Agent procedures belong in `AGENTS.md` and `docs/ai/`.

Keep `CURRENT_PLAN.md` as a compact pointer to active work. Keep detailed plans, task files, review reports, and closeout material under `docs/ai/work/<requirement-id>/`. Keep `NEXT_STEPS.md` short and prioritized. Use ADRs for durable architecture decisions.

## Review rules

Review must compare requirements, plan, diff, tests, documentation, and verification results.

Findings use these priorities:

- `P0`: immediate critical risk or data loss;
- `P1`: must be fixed before merge;
- `P2`: should be fixed;
- `P3`: optional improvement.

A review must not approve solely because checks pass. Inspect behavior, failure modes, compatibility, security, unnecessary complexity, missing tests, and documentation accuracy.

The implementer may fix findings, but a fresh review should verify the fixes. Use `docs/ai/templates/REVIEW_REPORT.md`.

## Definition of done

A task is complete only when:

- acceptance criteria are met;
- required implementation and tests are complete;
- all configured mandatory quality gates pass;
- security and compatibility implications were assessed;
- affected documentation is current and obsolete text removed;
- no unrelated changes remain;
- no unresolved `P0` or `P1` findings remain;
- residual risks, skipped checks, and next steps are explicit.
