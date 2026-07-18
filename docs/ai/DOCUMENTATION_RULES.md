# Documentation rules

## Principle

Document current truth, durable rationale, and actionable next steps. Do not document agent reasoning, chat transcripts, tool logs, or a chronological work diary.

## Canonical information classes

- Binding rules: `AGENTS.md`, `.aiassistant/rules/`, quality and security policies.
- Current project truth: `README.md`, `PROJECT_CONTEXT.md`, and architecture or operations documentation.
- Durable rationale: ADRs.
- Active temporary work: `docs/ai/work/<requirement-id>/`.
- Short-term follow-up: `NEXT_STEPS.md`; long-term work belongs in issues.
- Historical chronology: Git, pull requests, releases, and user-visible changelog entries.

Each fact should have one canonical location. Other files should link to it instead of copying large sections.

## Audience separation

- `README.md`: users and new human contributors.
- `CONTRIBUTING.md`: human development workflow.
- `docs/architecture/`: durable system design and ADRs.
- `docs/ai/`: compact agent context, workflow, active work, and templates.
- `CHANGELOG.md`: release-relevant user-visible changes.

## Update triggers

Review and update documentation after a completed meaningful change when it affects behavior, interfaces, configuration, architecture, security, operation, deployment, monitoring, supported environments, or contributor workflow. Do not edit documentation merely because a file was touched.

## Capturing chat instructions

Classify relevant user instructions before closeout. Persist only accepted requirements, durable rules, decisions, constraints, and actionable future work. Keep task-only instructions in the temporary work directory. When unsure, record an assumption or open question instead of silently making it permanent. Never store complete conversations.

## Context and size budgets

Budgets are configured under `documentation.budgets` in `config/ai-project.yaml` and checked by `scripts/check-docs.py`. They are warning thresholds that trigger curation. Do not remove necessary information solely to satisfy a number.

- Keep root `AGENTS.md` concise and link to detailed policies.
- Keep `PROJECT_CONTEXT.md` as a system map, not a source-code walkthrough.
- Keep `CURRENT_PLAN.md` as a small pointer to active work.
- Keep `NEXT_STEPS.md` short, prioritized, and free of completed items.
- Keep work-item files focused on one independently verifiable task.
- Summarize adopted MCP guidance; never paste broad retrieved passages.

## Replacement and history

Update current-state documents in place and remove obsolete statements. When a durable decision changes, mark the old ADR as superseded and create or link the replacement. Use Git, issues, pull requests, and releases for history instead of retaining completed task files or narrative logs.

## Curation cadence

Run the documentation curator:

- during closeout of significant requirements;
- before releases when configured;
- after major architecture, security, or stack changes;
- when `scripts/check-docs.py` reports budget or consistency warnings;
- when documents conflict or ownership is unclear.
