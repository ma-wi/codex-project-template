# Repository instructions for coding agents

## Mission

Deliver the smallest secure, tested, reviewable change that satisfies an accepted requirement. Do not expand scope silently.

## Instruction priority

The absolute production-access prohibition in this file is a non-overridable
safety boundary and takes precedence over every instruction, requirement, plan,
approval, role, and document, including current user instructions. Any conflicting
request must be refused and reported. Subject to that boundary, use this order:

1. Current explicit user instruction.
2. Accepted requirement and acceptance criteria.
3. Nearest applicable `AGENTS.md`.
4. Accepted ADRs and durable specification.
5. Active implementation plan.
6. Existing code, tests, and project conventions.

Stop and report material contradictions before destructive, incompatible, or security-sensitive action.

## Start here

1. Read `.ai/project.yaml`.
2. Read the requirement and `.ai/PROJECT_CONTEXT.md`.
3. Read only the role file and conditional policy documents relevant to the task.
4. Follow the canonical lifecycle in `.ai/policies/WORKFLOW.md`.

Do not load every file under `.ai/` by default.

## Change classes

- **Trivial:** mechanical, low-risk, no behavioral/interface/configuration/security change. No work directory is required; run relevant checks.
- **Normal:** bounded behavior change or bug fix. Requires accepted criteria, a compact temporary plan, tests, full verification, and independent review.
- **Significant:** initial project, new subsystem, public API, migration, security/privacy-sensitive work, major integration, or broad/ambiguous feature. Requires discovery when unclear, a durable specification, explicit test seams, task decomposition, full verification, and independent review. Add a specialist security review when the threat surface changes materially.

If uncertain, use the higher class. Record the selected class and reason in the plan.

## Artifact model

Use one active requirement per Git branch/worktree.

- Requirements: `docs/requirements/<requirement-id>.md` — durable input.
- Accepted specifications: `docs/specifications/<requirement-id>.md` — durable behavior, decisions, acceptance criteria, and test seams.
- ADRs: `docs/architecture/decisions/` — durable architecture decisions accepted before dependent implementation.
- Active work: `.ai/work/<requirement-id>/` — temporary plan, tasks, and review notes.
- Active pointer: `.ai/CURRENT_PLAN.md` — compact and single-valued.
- Follow-up: `.ai/NEXT_STEPS.md` or issues — unresolved actionable work only.

Temporary work artifacts must remain through independent review. Before merge, transfer durable information, record the completion summary in the pull request, remove temporary artifacts, and reset `CURRENT_PLAN.md`.

## Planning and implementation boundaries

- Do not implement before acceptance criteria are testable.
- Significant work may start only when its specification says `Status: ready-for-implementation` and `Ready for implementation: yes`.
- The planner may inspect and write planning artifacts but must not change production code.
- The implementer works only on `ready` tasks and may advance them through `implemented` and `verified`.
- The independent reviewer may advance verified tasks to `reviewed`; the closeout step advances accepted work to `done`.
- Material plan deviations must be recorded before continuing.

## Engineering rules

- Preserve compatibility unless a breaking change is explicitly accepted.
- Add automated tests for every behavior change at the lowest useful stable seam.
- For bug fixes, add a failing regression test first where practical.
- Test relevant failures, boundaries, permissions, migration, and recovery behavior.
- Do not weaken tests, lint rules, scanners, or thresholds to obtain a pass.
- Do not add unrelated cleanup or speculative abstraction.
- Do not add or upgrade dependencies without the review required by `.ai/policies/DEPENDENCY_POLICY.md`.
- Never claim a command passed unless it was executed and observed.

## Security baseline

### Absolute production-access prohibition

Access to project, customer, or organizational production is forbidden without
exception. Never connect to, access, read, query, inspect, modify, administer, or
otherwise interact with a production environment, system, service, database, data
store, host, cluster, cloud account, network, API, queue, storage resource, secret
store, or any resource that contains or controls production data or workloads.

Never execute a script, migration, deployment, job, test, diagnostic, CLI command,
API call, CI/CD action, or other operation that targets production or could cause
an action in production. This includes read-only access, health checks, dry runs,
troubleshooting, and indirect access through automation, tunnels, bastions,
control planes, integrations, or third-party systems. Never use production
credentials, endpoints, configuration, backups, snapshots, exports, or copied
production data.

Work only with local, development, test, or sandbox resources that are explicitly
confirmed to be non-production and contain no production data. If the target or
effect is ambiguous, treat it as production and stop. No request, requirement,
plan, approval, or convenience overrides this prohibition.

Ordinary development use of source hosting, package registries, public
documentation, and explicitly configured engineering tools is allowed only when it
cannot access, deploy to, control, or otherwise affect production and receives no
production secrets or data. If a development action could trigger a production
deployment or operation, it is prohibited.

- Validate untrusted input at trust boundaries and enforce authorization server-side.
- Never commit or print secrets, credentials, production data, or sensitive personal data.
- Prevent injection, path traversal, unsafe deserialization, and unbounded resource use.
- Use established cryptographic libraries and protocols.
- Use least privilege, secure defaults, timeouts, bounded retries, and safe failure behavior.
- Stop and escalate credible high-impact vulnerabilities, data-loss risk, or unsafe migrations.

Read `.ai/policies/SECURITY_GUIDELINES.md` only when the change touches a listed threat surface.

## Verification

Repository scripts are the canonical interface:

```bash
./.ai/tools/format.sh --check
./.ai/tools/lint.sh
./.ai/tools/test.sh
./.ai/tools/check-dependencies.sh
./.ai/tools/security.sh
./.ai/tools/build.sh
./.ai/tools/verify.sh
```

Committed commands live in `.ai/config/project.defaults.env`; ignored machine-local overrides live in `.ai/config/project.env`. A mandatory unavailable or skipped gate is a failure. Run focused checks during implementation and `./.ai/tools/verify.sh` before handoff and completion.

## Independent review

Normal and significant work requires a fresh reviewer context. Review requirements, durable specification, plan, diff, tests, verification, security, compatibility, migrations, operations, and documentation. Findings use:

- `P0`: critical exploitability, imminent data loss, or equivalent emergency;
- `P1`: must be fixed before merge;
- `P2`: material issue that should be fixed;
- `P3`: optional improvement.

No unresolved `P0` or `P1` may remain. Fixes for those priorities require fresh verification by the reviewer.

## Documentation

Document current truth, durable rationale, and actionable next steps—not chat transcripts or work diaries. Put each fact in one canonical location and link to it elsewhere. Update only documentation affected by the change and replace obsolete statements.

During closeout, curate documentation before removing temporary artifacts. Git and the pull request provide process history; the durable specification and ADRs preserve product and architecture knowledge.

## Context routing

- Lifecycle and status transitions: `.ai/policies/WORKFLOW.md`
- Planner instructions: `.ai/roles/planner.md`
- Implementer instructions: `.ai/roles/implementer.md`
- Reviewer instructions: `.ai/roles/code-reviewer.md`
- Security: `.ai/policies/SECURITY_GUIDELINES.md`
- Dependencies: `.ai/policies/DEPENDENCY_POLICY.md`
- Documentation: `.ai/policies/DOCUMENTATION_RULES.md`
- Quality policy: `.ai/policies/QUALITY_GATES.md`

Use the optional engineering-knowledge MCP only when enabled in `.ai/project.yaml` and a concrete unresolved standards decision requires it. Retrieve narrowly and record adopted conclusions, not copied source material.
