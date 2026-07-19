# Template hardening and context reduction

- Requirement ID: REQ-template-hardening
- Status: ready-for-implementation
- Requirement source: `docs/requirements/REQ-template-hardening.md`
- Decision owner: project owner
- Last updated: 2026-07-19

## Purpose

Make the reusable control plane match its documented fail-closed lifecycle while
reducing duplicated instructions presented to coding agents.

## Scope

### In scope

- Verification configuration precedence and mandatory-gate enforcement.
- Missing-test behavior for supported stacks.
- Repository-bound path validation in lifecycle checks.
- Bootstrap/readiness documentation validation.
- Direct-dependency syntax and source validation.
- Lifecycle ownership, exception language, and conditional-policy routing.
- Removal of demonstrably redundant template guidance and examples.
- Regression and copy-boundary tests.

### Out of scope / non-goals

- Adding application frameworks or deployment automation.
- Accessing or designing production operations.
- Replacing the shell/Python verification architecture.
- Updating runtime versions without a separate demonstrated compatibility need.

## Observable behavior

- A local developer may replace a gate command but cannot locally downgrade a
  committed required gate.
- Required tests fail clearly when no test target exists.
- Lifecycle pointers containing traversal or escaping symlinks fail validation.
- Configured projects remain visibly incomplete until security reporting and core
  quality decisions are filled in.
- Dependency inputs that the policy cannot safely interpret fail instead of being
  ignored.
- Agents propose durable decisions; the named human/authorized decision owner
  accepts them. A closeout context performs curation only after independent review.
- Conditional guidance is routed without duplicating full checklists.

## Security and compatibility

- The production-access prohibition remains absolute and canonical in `AGENTS.md`.
- P0/P1 findings have no acceptance/waiver path.
- Local overrides remain useful for executable locations and equivalent commands.
- Existing project-copy exclusion behavior and stack configuration remain compatible.

## Test seams

- Primary: `tests/test_template.py` integration tests against copied/configured
  temporary repositories.
- Secondary: direct execution of documentation, lifecycle, dependency, bootstrap,
  and verification helpers in isolated temporary directories.
- Avoid: tests coupled only to private helper implementation details.

## Acceptance criteria

The acceptance criteria are AC-1 through AC-8 in
`docs/requirements/REQ-template-hardening.md`.

## Decisions and accepted assumptions

- The user explicitly approved implementation of audit work packages 1–5 on
  2026-07-19.
- Command overrides are allowed; policy/requiredness overrides are not.
- Readiness checks apply after `project.name` is configured, not to pristine template
  state.
- Template-only durable requirement/specification files are excluded from copied
  projects.

## Open questions and blockers

- None.

## Readiness decision

- Shared understanding confirmed: yes
- Confirmed by: project owner
- Confirmation date: 2026-07-19
- Ready for implementation: yes
