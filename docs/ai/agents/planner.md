# Planner agent

Read `AGENTS.md`, the requirement, repository context, relevant code, tests, and architecture before planning.

Do not change production code during the planning phase.

For non-trivial work:

1. choose a stable requirement ID;
2. create `docs/ai/work/<requirement-id>/`;
3. select `interview` or `synthesize` according to `config/ai-project.yaml`;
4. for significant features, write `SPEC.md` from `FEATURE_SPEC.md`;
5. set the specification to `ready-for-implementation` only after required confirmation and readiness checks;
6. derive `PLAN.md` from the accepted specification using `IMPLEMENTATION_PLAN.md`;
7. create `tasks/` and use `WORK_ITEM.md` only for independently implementable or verifiable tasks;
8. update `docs/ai/CURRENT_PLAN.md` as a compact pointer.

Before specification, inspect applicable ADRs, code, tests, and project documentation for established domain terminology. Reuse those terms consistently and surface conflicts rather than creating synonyms.

## Planning mode selection

Use interview mode when material decisions, boundaries, behaviors, or acceptance criteria remain unclear. Use synthesis mode when the supplied requirement, conversation, and repository context already contain enough confirmed information.

In synthesis mode:

- do not repeat answered questions;
- do not invent absent product or architecture decisions;
- classify unresolved gaps as blockers, accepted assumptions, or implementation details;
- produce `SPEC.md` with status `awaiting-confirmation` when owner confirmation is required;
- stop before implementation if a gap can materially change the result.

## Discovery mode for large or abstract work

Before creating an accepted implementation plan, use `docs/ai/templates/FEATURE_DISCOVERY.md` when the requirement is an initial project, a major subsystem, a broad user-facing feature, or materially underspecified.

Interview rules:

1. Start with the highest-impact unresolved decision.
2. Ask a small, coherent group of related questions rather than a long unprioritized questionnaire.
3. For each question, state your recommended answer and why.
4. Resolve dependencies in order: problem and users, outcomes, workflows, scope, domain rules, data, interfaces, non-functional constraints, operations, then implementation choices.
5. Record confirmed decisions, rejected alternatives, assumptions, and open questions in the discovery artifact.
6. Periodically present a concise shared-understanding summary and ask the user to correct it.
7. Do not implement or mark the plan accepted until the user explicitly confirms shared understanding.
8. End discovery when remaining unknowns can be safely handled as implementation details or recorded assumptions.

User stories are optional. Use them only when they clarify a user-visible workflow, actor, goal, or outcome. Do not manufacture stories for infrastructure, refactoring, security controls, migrations, build tooling, or purely technical work; express those as requirements, constraints, acceptance criteria, or work items instead.

Required output:

- normalized problem and desired observable outcome;
- scope and non-goals;
- facts, assumptions, unresolved questions, and blockers;
- affected components, interfaces, data, and operations;
- compatibility, migration, security, privacy, performance, accessibility, observability, and rollback implications where relevant;
- narrow MCP queries for concrete unresolved standards decisions;
- task breakdown, dependencies, and initial statuses `draft` or `ready`;
- acceptance-criteria traceability, test strategy, and explicit test seams;
- exact or categorized verification steps;
- documentation and closeout plan.

Avoid creating a file for every small checkbox. Avoid prescribing details that repository inspection does not support.
