# Review guidelines

## Review inputs

- accepted requirement and acceptance criteria;
- applicable `AGENTS.md` files;
- current plan and deviations;
- complete diff;
- affected tests and call paths;
- verification output;
- updated documentation and architecture decisions.

## Review method

1. Restate the expected behavior.
2. Trace each acceptance criterion to implementation and tests.
3. Inspect failure paths, boundaries, permissions, concurrency, and state transitions.
4. Check compatibility, migrations, rollback, observability, and operational impact.
5. Look for unnecessary complexity, scope expansion, duplication, and hidden coupling.
6. Verify that tests can fail for the intended defect and are not merely asserting mocks.
7. Compare documentation with actual behavior.
8. Confirm reported commands were executed and skipped checks are explicit.

## MCP use during review

Consult the standards MCP only when a new pattern or standard-sensitive area is introduced, a compliance criterion exists, project rules are missing, or the implementation appears to conflict with adopted guidance.

Do not use it to manufacture stylistic preferences. Distinguish:

- violation of a binding repository rule;
- violation of explicitly adopted external guidance;
- optional improvement suggested by general reference material.

Only the first two are normally merge-blocking.

## Finding priorities

- `P0`: exploitable critical vulnerability, imminent data loss, or equivalent emergency.
- `P1`: correctness, security, compatibility, or operability defect that must be fixed before merge.
- `P2`: material quality issue that should be fixed.
- `P3`: optional improvement or maintainability suggestion.

Every finding should include location, evidence, impact, and required change. Avoid vague preferences.

## Verdicts

- `APPROVE`: no unresolved blocking findings.
- `APPROVE_WITH_NOTES`: only non-blocking findings remain.
- `REQUEST_CHANGES`: one or more `P1` findings remain.
- `BLOCK`: a `P0` finding or unsafe uncertainty prevents continuation.
