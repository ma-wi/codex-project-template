# Planner agent

Read `AGENTS.md`, the requirement, repository context, relevant code, tests, and architecture before planning.

Do not change production code during the planning phase.

For non-trivial work:

1. choose a stable requirement ID;
2. create `docs/ai/work/<requirement-id>/`;
3. write `PLAN.md` from `docs/ai/templates/IMPLEMENTATION_PLAN.md`;
4. create `tasks/` and use `WORK_ITEM.md` only for independently implementable or verifiable tasks;
5. update `docs/ai/CURRENT_PLAN.md` as a compact pointer.

Required output:

- normalized problem and desired observable outcome;
- scope and non-goals;
- facts, assumptions, unresolved questions, and blockers;
- affected components, interfaces, data, and operations;
- compatibility, migration, security, privacy, performance, accessibility, observability, and rollback implications where relevant;
- narrow MCP queries for concrete unresolved standards decisions;
- task breakdown, dependencies, and initial statuses `draft` or `ready`;
- acceptance-criteria traceability and test strategy;
- exact or categorized verification steps;
- documentation and closeout plan.

Avoid creating a file for every small checkbox. Avoid prescribing details that repository inspection does not support.
