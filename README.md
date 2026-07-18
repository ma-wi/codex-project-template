# Codex project template

This repository is a technology-neutral starting point for projects developed with a coding agent such as Codex in IntelliJ IDEA. It defines how agents plan, implement, test, verify, document, and review changes while keeping the persistent context small.

The template combines four control layers:

1. `AGENTS.md` contains concise, binding repository instructions.
2. `docs/ai/` contains the current project context, workflows, role definitions, and task templates.
3. `scripts/` provides stable quality-gate commands for agents, developers, and CI.
4. CI and independent review verify that the process produced a correct result.

## Fast bootstrap

1. Copy the template into an empty directory.
2. Edit `config/ai-project.yaml`. Python is enabled by default; enable React, Bash, or .NET/VB/PowerShell only when needed.
3. Open the directory in IntelliJ IDEA.
4. Run:

```bash
./scripts/bootstrap.sh
```

The bootstrap generates `scripts/project.env`, updates the compact project context, creates the Git project mapping, and uses the committed `.aiassistant/rules/` files. It prints the one remaining IntelliJ action: set **Path to rules for AI Self-Review** to `$PROJECT_DIR$/.aiassistant/review/self-review.md`. JetBrains documents this as a project setting but does not expose a stable public CLI or documented project-file key, so the template does not write undocumented plugin internals.

After installing the tools required by the enabled profiles, run `./scripts/verify.sh`.

## Use the template

### 1. Copy it into a new repository

Copy all files, including hidden files, into the root of a new project:

```bash
cp -R codex-project-template/. my-new-project/
cd my-new-project
```

Alternatively, create a repository from this directory using your Git hosting provider's template-repository function.

### 2. Replace project placeholders

Edit these files first:

- `config/ai-project.yaml`: select stacks, MCP use, strictness, and IDE bootstrap behavior.
- `README.md`: replace this template documentation with the product-facing project README after initialization.
- `docs/ai/PROJECT_CONTEXT.md`: describe purpose, architecture, technologies, constraints, and critical paths.
- `docs/ai/QUALITY_GATES.md`: decide which checks are mandatory.
- `scripts/project.env.example`: copy to `scripts/project.env` and configure commands that auto-detection cannot determine reliably.
- `SECURITY.md`: add the real reporting channel and supported-version policy.
- `CONTRIBUTING.md`: add project-specific development and pull-request conventions.

Then run:

```bash
cp scripts/project.env.example scripts/project.env
chmod +x scripts/*.sh
./scripts/verify.sh
```

`project.env` is intentionally ignored by the template. Commit project-wide commands directly into the scripts or create a committed configuration file if every developer and CI environment should use the same values.

### 3. Configure IntelliJ IDEA

1. Open the repository in IntelliJ IDEA.
2. Enable the desired coding agent.
3. Enable the `engineering-knowledge` MCP server when the project uses one.
4. Confirm that the agent can read the root `AGENTS.md`.
5. Keep approval and sandbox settings restrictive by default. Grant broader access only for a specific justified action.

The MCP is merely available after activation. The rules in `AGENTS.md` tell the agent when to consult it and how to avoid loading excessive reference text.

### 4. Give the agent an initial requirement

Place an initial requirement in a task, issue, prompt, or a copy of:

```text
docs/ai/templates/REQUIREMENTS.md
```

A recommended first instruction is:

```text
Read AGENTS.md and the requirement. Inspect the repository before proposing a solution.
Create docs/ai/CURRENT_PLAN.md from the implementation-plan template.
Consult the `engineering-knowledge` MCP only for decisions identified in the plan.
Do not implement until the plan contains scope, non-goals, assumptions,
acceptance criteria, risks, affected areas, and verification steps.
Then implement, test, run ./scripts/verify.sh, and create an independent review report.
```

### 5. Run the agent workflow

The standard lifecycle is:

```text
Requirement
  -> repository inspection
  -> temporary work directory, plan, and task decomposition
  -> targeted standards lookup when needed
  -> task-by-task implementation and tests
  -> focused checks
  -> full verification
  -> independent review
  -> remediation and re-verification
  -> closeout, durable documentation, and temporary-work cleanup
```

For separate agents or sessions, use the role files in `docs/ai/agents/`:

- `planner.md`
- `implementer.md`
- `tester.md`
- `security-reviewer.md`
- `code-reviewer.md`
- `documentation-reviewer.md`
- `documentation-curator.md`
- `closer.md`

A role file supplements rather than replaces `AGENTS.md`.

## Directory overview

```text
.
├── AGENTS.md                         Binding repository instructions
├── README.md                         Human-facing template usage
├── CONTRIBUTING.md                   Contributor workflow
├── SECURITY.md                       Security reporting and policy
├── CHANGELOG.md                      Release-level user-visible changes
├── docs/
│   ├── architecture/
│   │   ├── overview.md               Current architecture
│   │   └── decisions/                Durable architecture decisions
│   └── ai/
│       ├── PROJECT_CONTEXT.md         Compact agent-oriented project map
│       ├── WORKFLOW.md                Phase transitions and outputs
│       ├── QUALITY_GATES.md           Required verification policy
│       ├── SECURITY_GUIDELINES.md     Project security checklist
│       ├── DEPENDENCY_POLICY.md       Package and supply-chain policy
│       ├── REVIEW_GUIDELINES.md       Review method and severity
│       ├── DOCUMENTATION_RULES.md     Context-minimizing documentation rules
│       ├── DEFINITION_OF_DONE.md      Completion criteria
│       ├── CURRENT_PLAN.md            Compact pointer to active work
│       ├── work/                      Temporary per-requirement plans, tasks, and reviews
│       ├── NEXT_STEPS.md              Short prioritized follow-up list
│       ├── DECISIONS.md               Small operational decisions
│       ├── agents/                    Role-specific instructions
│       └── templates/                 Reusable task artifacts
├── scripts/                           Stable quality-gate interface
└── .github/workflows/ci.yml           Example CI integration
```

## Quality-gate scripts

The scripts auto-detect common ecosystems, including Gradle, Maven, Node.js, Python, Go, and Rust. Auto-detection is deliberately conservative. A real project should review and configure every gate.

Available commands:

```bash
./scripts/check-work-state.py # Validate active plan and task metadata
./scripts/format.sh          # Apply formatting where supported
./scripts/format.sh --check  # Check formatting without changing files
./scripts/lint.sh            # Lint and static analysis
./scripts/test.sh            # Automated tests
./scripts/check-dependencies.sh # Package policy, CVEs, licenses, reputation
./scripts/check-docs.py         # Documentation links, pointers, budgets, placeholders
./scripts/security.sh        # Secret and static security checks
./scripts/build.sh           # Build or package
./scripts/verify.sh          # Run all mandatory gates
```

Override detected commands in `scripts/project.env`:

```bash
FORMAT_CHECK_CMD='./gradlew spotlessCheck'
FORMAT_APPLY_CMD='./gradlew spotlessApply'
LINT_CMD='./gradlew checkstyleMain detekt'
TEST_CMD='./gradlew test integrationTest'
SECURITY_CMD='./gradlew dependencyCheckAnalyze'
DEPENDENCY_SCAN_CMD='./gradlew dependencyCheckAnalyze'
DEPENDENCY_REPUTATION_CMD='' # Optional approved service/CLI
REQUIRE_DEPENDENCY_SCANNERS=1
BUILD_CMD='./gradlew assemble'
```

Each command is executed through `bash -lc`. Do not place secrets in this file or in command output.

### Mandatory versus unavailable checks

A missing configured command is reported as `SKIPPED`. This is acceptable while bootstrapping the template, but a production-ready project should define every mandatory gate in `docs/ai/QUALITY_GATES.md` and CI. A skipped mandatory gate must be reported as incomplete, not passed.

Set the following to make selected gates fail when unavailable:

```bash
REQUIRE_FORMAT_CHECK=1
REQUIRE_LINT=1
REQUIRE_TEST=1
REQUIRE_SECURITY=1
REQUIRE_BUILD=1
```

## MCP standards knowledge base

The root `AGENTS.md` contains the default usage policy:

- consult the MCP during significant planning and standards-sensitive decisions;
- ask narrow, decision-specific questions;
- do not retrieve broad collections or repeatedly fetch the same material;
- store adopted decisions locally without copying large source texts;
- prefer project-local accepted rules over general external guidance.

Customize the server and tool names in `docs/ai/PROJECT_CONTEXT.md`. The template intentionally does not hard-code an MCP tool name because IntelliJ and server configurations differ.

## Documentation model

The repository should remain understandable without access to prior agent conversations or the MCP.

Persist only:

- current system behavior and constraints;
- rationale for durable decisions;
- current active plan;
- short actionable next steps;
- verified review and release information.

Do not persist verbose chain-of-thought, trial-and-error logs, copied RAG passages, or a chronological diary. Git history, issues, and pull requests already provide change history.

For non-trivial requirements, active work lives temporarily under:

```text
docs/ai/work/<requirement-id>/
├── PLAN.md
├── tasks/
├── REVIEW.md
├── CHANGE_SUMMARY.md
└── CLOSEOUT.md
```

`CURRENT_PLAN.md` only points to this directory and names the current phase or task. Task states progress through `draft`, `ready`, `in-progress`, `implemented`, `verified`, `reviewed`, and `done`; `blocked` is available when progress cannot continue.

After a requirement closes:

1. Confirm every required task and acceptance criterion has evidence.
2. Move durable architectural decisions into ADRs.
3. Update current-state, user, operational, security, and architecture documentation.
4. Move unresolved work to `NEXT_STEPS.md` or an issue.
5. Keep temporary artifacts until independent review is complete.
6. Remove the completed work directory before final merge after durable information has been transferred, unless project policy retains it.
7. Reset `CURRENT_PLAN.md` to its idle state.

Git history and the pull request retain the temporary planning and review trail.

## Adapting the template

Create nested `AGENTS.md` files only when a directory has genuinely different rules, for example:

```text
frontend/AGENTS.md
backend/AGENTS.md
infrastructure/AGENTS.md
```

Keep nested instructions local and avoid repeating root rules.

Add new permanent templates only when the artifact is repeatedly needed, has a defined owner or update rule, and cannot fit an existing document. Avoid process-document proliferation.

## First project bootstrap checklist

- [ ] Replace template purpose and placeholders.
- [ ] Record supported runtimes and tool versions.
- [ ] Configure deterministic dependency locking.
- [ ] Configure all mandatory quality gates.
- [ ] Add CI branch protection and required checks.
- [ ] Define the security reporting path.
- [ ] Document architecture and trust boundaries.
- [ ] Decide whether the standards MCP is mandatory for specific change classes.
- [ ] Run the initial verification and record skipped gates.
- [ ] Conduct a fresh-context review of the generated project skeleton.

## License

Add the license appropriate for the new project. This template does not impose one.

## Dependency and package security

The template includes a separate package gate:

```bash
./scripts/check-dependencies.sh
```

It always applies local policy from `config/dependency-policy.conf`, `config/dependency-denylist.txt`, and optionally `config/dependency-allowlist.txt`. It detects direct dependencies in common Node.js, Python, Rust, Go, and Maven manifests, rejects configured packages, checks lockfiles, and rejects obvious floating versions.

When installed, the script also runs:

- **OSV-Scanner** for known vulnerabilities in supported manifests and lockfiles;
- **Trivy** for vulnerabilities, secrets, misconfiguration, and risky or unknown licenses;
- an optional organization-approved reputation scanner through `DEPENDENCY_REPUTATION_CMD`;
- an optional project-specific command through `DEPENDENCY_SCAN_CMD`.

Commercial or hosted reputation products such as Socket, Snyk, or Mend are intentionally not hard-coded. Configure the exact approved CLI command in `scripts/project.env`. This avoids silently sending private dependency metadata to an external service.

Set `REQUIRE_DEPENDENCY_SCANNERS=1` in CI once at least one scanner is installed. For high-assurance projects, enable `DEPENDENCY_ALLOWLIST_MODE=1`. Automated scanners complement, but do not replace, the required human review of new packages.


## Documentation curation and chat instruction capture

The template treats documentation as maintained project state rather than a work diary. Material user instructions are classified during planning and closeout as task-only, requirements, durable rules, architecture decisions, operational constraints, or future work. Only durable accepted information is transferred to canonical project documents; complete chat transcripts and large MCP responses are not stored.

Documentation budgets are configured in `config/ai-project.yaml`. Run:

```bash
./scripts/check-docs.py
```

The check reports broken local links, invalid active-plan pointers, unresolved template placeholders, oversized core documents, excessive `NEXT_STEPS.md` items, and oversized active work items. Errors fail `./scripts/verify.sh`; warnings require review rather than automatic deletion.

Use `docs/ai/agents/documentation-curator.md` during significant closeout, before releases, after major architecture changes, or when consistency warnings appear. The curator moves durable decisions to ADRs or current-state documentation and removes obsolete or duplicated temporary content.
