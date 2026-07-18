# AI Self-Review rules

Review selected changes against `AGENTS.md`, `config/ai-project.yaml`, the active requirement, `docs/ai/CURRENT_PLAN.md`, its referenced `PLAN.md` and work-item files, applicable ADRs, and repository quality policies.

Check for unmet acceptance criteria, regressions, incompatible API/schema/configuration changes, missing tests, security defects, risky dependencies, Python typing and error handling, React accessibility and client-side trust, Bash/PowerShell quoting and error propagation, .NET/VB analyzer and compatibility defects, stale documentation, unrelated changes, and unnecessary complexity.

Severity:

- `P0`: immediate critical risk, exploitable vulnerability, or data loss.
- `P1`: must be fixed before merge.
- `P2`: should be fixed.
- `P3`: optional improvement.

Reference concrete files and locations, explain impact, separate defects from preferences, and never invent successful test or scanner results.


## Documentation integrity

Check whether durable user instructions were captured in the correct canonical artifact, whether temporary work leaked into permanent documentation, and whether obsolete or duplicate guidance should be removed. Consider documentation-budget warnings from `./scripts/check-docs.py`.
