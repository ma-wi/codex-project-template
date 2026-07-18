# Codex project template

This repository is a reusable starting point for Python projects, optionally with a React frontend, Bash scripts, or a .NET/Visual Basic and PowerShell stack. It is designed for Codex in IntelliJ IDEA and defines how agents discover requirements, create specifications and plans, implement tasks, run quality gates, review changes, and keep documentation concise.

The template uses four control layers:

1. `AGENTS.md` contains the binding repository instructions for coding agents.
2. `.aiassistant/rules/` contains project rules for JetBrains AI Assistant.
3. `docs/ai/` contains current project context, temporary work artifacts, role instructions, and reusable templates.
4. `scripts/` and CI provide repeatable technical quality gates.

## Recommended new-project setup

### 1. Copy the template without its local Git or IntelliJ state

Do not copy the template repository's `.git/` or `.idea/` directories. Use the included project-creation script; hidden template files such as `.gitignore`, `.github/`, `.aiassistant/`, and `.gitkeep` are preserved.

#### Linux, macOS, Git Bash, or WSL

Preview the copy first:

```bash
./scripts/create-project.sh --dry-run /path/to/my-new-project
```

Create the project:

```bash
./scripts/create-project.sh /path/to/my-new-project
cd /path/to/my-new-project
```

The target must be empty by default. Use `--force` only when intentionally merging into an existing directory.

The script prefers `rsync` and uses a portable `tar` fallback. `--dry-run` requires `rsync`.

#### Windows PowerShell

Preview with PowerShell's standard `-WhatIf` behavior:

```powershell
.\scripts\create-project.ps1 -TargetDirectory "C:\Projects\my-new-project" -WhatIf
```

Create the project:

```powershell
.\scripts\create-project.ps1 -TargetDirectory "C:\Projects\my-new-project"
Set-Location "C:\Projects\my-new-project"
```

Use `-Force` only when intentionally merging into a non-empty directory.

#### Manual alternative with `rsync`

```bash
rsync -a \
  --exclude='.git/' \
  --exclude='.idea/' \
  --exclude='scripts/project.env' \
  /path/to/codex-project-template/ \
  /path/to/my-new-project/
```

The trailing `/` on the source is important: it copies the directory contents rather than nesting the template directory itself.

### 2. Configure the project

Edit:

```text
config/ai-project.yaml
```

At minimum, set the project name and enabled stacks:

```yaml
project:
  name: "example-service"
  profile: "python"

stacks:
  python:
    enabled: true
    package_manager: "uv"
  react:
    enabled: false
    directory: "frontend"
    package_manager: "npm"
  bash:
    enabled: false
  dotnet:
    enabled: false
    solution: ""
    visual_basic: true
    powershell: true

engineering_knowledge:
  enabled: true
  mcp_server: "engineering-knowledge"
```

Use `engineering_knowledge.enabled: false` when the MCP should not be used. An unavailable optional MCP must not block normal work; a required standards decision must be reported if it cannot be checked.

Also review:

- `planning`: interview, synthesis, and confirmation behavior;
- `quality`: mandatory gates;
- `ide`: generated IntelliJ project configuration;
- `documentation`: curation behavior and size budgets.

### 3. Run the bootstrap

On Linux, macOS, Git Bash, or WSL:

```bash
./scripts/bootstrap.sh
```

On Windows without a Unix-compatible shell:

```powershell
python .\scripts\bootstrap.py
```

The bootstrap:

- reads `config/ai-project.yaml`;
- generates the local `scripts/project.env` commands;
- updates the bootstrap section in `docs/ai/PROJECT_CONTEXT.md`;
- makes shell scripts executable where supported;
- creates `.idea/vcs.xml` when `ide.create_git_mapping` is enabled;
- reports the remaining manual IntelliJ Self-Review setting.

`scripts/project.env` is local and ignored by Git. Team-wide commands must also be represented in committed scripts or CI rather than existing only in a developer's local file.

### 4. Install the enabled development tools

The bootstrap configures commands but does not install tools globally.

#### Python baseline

With `uv`:

```bash
uv add --dev ruff mypy pytest pytest-cov bandit pip-audit build
```

Or with a virtual environment and pip:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install ruff mypy pytest pytest-cov bandit pip-audit build
```

Typical generated checks include:

```text
ruff format --check .
ruff check .
mypy .
pytest
bandit -q -r . -x tests,.venv,venv
pip-audit
python -m build
```

#### React/TypeScript baseline

The frontend `package.json` should expose at least:

```json
{
  "scripts": {
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "build": "vite build"
  }
}
```

Commit the appropriate lockfile and use frozen/locked installs in CI.

#### Bash baseline

Install `shellcheck`; install `bats` when shell tests are stored under `tests/shell/`.

#### .NET, Visual Basic, and PowerShell baseline

Install the required .NET SDK. For PowerShell analysis and tests, install `PSScriptAnalyzer` and `Pester` in the development or CI environment.

#### Cross-project security tools

For broader repository scanning, install and pin approved versions of:

- OSV-Scanner;
- Trivy;
- Gitleaks, when used by the security command;
- an organization-approved package reputation tool, if configured.

External reputation services are not enabled automatically because they may transmit private dependency metadata.

### 5. Configure IntelliJ IDEA

1. Open the new project directory.
2. Enable the desired Codex coding agent.
3. Enable the `engineering-knowledge` MCP only when configured for the project.
4. Confirm the agent can read the root `AGENTS.md`.
5. Keep command approval and sandbox settings restrictive by default.
6. Configure JetBrains Project Rules from the committed `.aiassistant/rules/` files as appropriate.
7. Set the AI Self-Review rules path under:

```text
Settings
→ Tools
→ AI Assistant
→ Project Settings
→ Path to rules for AI Self-Review
```

Use:

```text
$PROJECT_DIR$/.aiassistant/review/self-review.md
```

The template does not edit undocumented JetBrains plugin settings automatically.

### 6. Initialize Git and GitHub

The copy script excludes the template's `.git/`, so initialize the new repository independently:

```bash
git init
git add .
git commit -m "Initialize project from Codex template"
git branch -M main
git remote add origin git@github.com:ORGANIZATION/REPOSITORY.git
git push -u origin main
```

Recommended GitHub settings:

- protect `main`;
- require pull requests;
- require the CI verification check;
- enable secret scanning and dependency alerts where available;
- enable code scanning such as CodeQL when appropriate;
- prevent direct pushes to the protected branch.

Local IntelliJ files should generally remain uncommitted. The template ignores personal files such as `.idea/workspace.xml` and `.idea/shelf/`. The bootstrap-created `.idea/vcs.xml` may be committed when the team wants a shared Git mapping; otherwise disable `ide.create_git_mapping` or ignore `.idea/` entirely in the target project.

### 7. Complete project-specific documentation

Before calling the project initialized, update:

- `README.md`: product purpose, setup, execution, configuration, and usage;
- `docs/ai/PROJECT_CONTEXT.md`: stack, modules, trust boundaries, constraints, and critical paths;
- `docs/architecture/overview.md`: current architecture and data flow;
- `docs/ai/QUALITY_GATES.md`: mandatory project checks;
- `SECURITY.md`: reporting channel and supported-version policy;
- `CONTRIBUTING.md`: branch, commit, pull-request, and review conventions;
- `config/dependency-policy.conf` and the dependency allow/deny lists;
- `.github/workflows/ci.yml`: runtime setup and pinned scanners.

This README is the template setup guide. After initialization, either adapt it into the product README while retaining a concise contributor setup section, or move the reusable template instructions to an internal project document before replacing them.

### 8. Run the initial verification

```bash
./scripts/verify.sh
```

A strict project is not ready when a mandatory gate is reported as `SKIPPED`. Configure or install the missing tool, or explicitly change the project policy with a documented reason.

## Starting the first requirement

Copy the requirements template to a stable project location:

```bash
cp docs/ai/templates/REQUIREMENTS.md docs/requirements/REQ-001-initial-project.md
```

Recommended planning prompt:

```text
Work as the planning agent.
Read AGENTS.md, config/ai-project.yaml, docs/ai/agents/planner.md,
docs/ai/PROJECT_CONTEXT.md, applicable ADRs, and the requirement.
Inspect the repository before proposing a solution.

Choose interview or synthesis mode according to the planning configuration.
For significant work, create a stable SPEC.md from FEATURE_SPEC.md, then create
a temporary PLAN.md and task files under docs/ai/work/<requirement-id>/.
Use the engineering-knowledge MCP only for targeted decisions when enabled.
Do not implement until shared understanding is confirmed, the specification is
ready-for-implementation, acceptance criteria and test seams are defined, and
the plan is accepted.
```

### Planning modes

`planning.mode` supports:

- `auto`: interview only when material decisions are missing;
- `interview`: resolve decisions with the user before producing the final spec;
- `synthesize`: turn an already complete requirement or conversation into a spec without repeating answered questions.

Large or abstract features use `docs/ai/templates/FEATURE_DISCOVERY.md`. The planner asks dependency-aware questions in small groups, recommends an answer for each material decision, and waits for explicit confirmation of shared understanding.

User stories are optional. Use them only when actor, goal, and outcome clarify user-visible behavior. They do not replace functional requirements, non-functional requirements, edge cases, or acceptance criteria.

## Agent workflow

The standard lifecycle is:

```text
Requirement
  → discovery interview or synthesis
  → accepted SPEC.md with stable test seams
  → temporary PLAN.md and task decomposition
  → implementation and focused checks
  → full verification
  → independent review
  → remediation and re-verification
  → documentation curation and closeout
  → temporary work cleanup
  → pull request and CI
```

Use a fresh agent context for each role when practical:

- `docs/ai/agents/planner.md`
- `docs/ai/agents/implementer.md`
- `docs/ai/agents/tester.md`
- `docs/ai/agents/security-reviewer.md`
- `docs/ai/agents/code-reviewer.md`
- `docs/ai/agents/documentation-reviewer.md`
- `docs/ai/agents/documentation-curator.md`
- `docs/ai/agents/closer.md`

A role file supplements rather than replaces `AGENTS.md`.

## Temporary work model

For a significant requirement:

```text
docs/ai/work/REQ-001-example/
├── DISCOVERY.md       optional while resolving uncertainty
├── SPEC.md            stable behavior and decisions for the feature
├── PLAN.md            temporary implementation strategy
├── tasks/
│   ├── T001-example.md
│   └── T002-example.md
├── REVIEW.md
├── CHANGE_SUMMARY.md
└── CLOSEOUT.md
```

`docs/ai/CURRENT_PLAN.md` remains a small pointer to the active requirement, work directory, spec, plan, phase, and current task.

Task statuses are:

```text
draft → ready → in-progress → implemented → verified → reviewed → done
```

Use `blocked` when work cannot continue. The implementer must not mark its own work `reviewed` or `done`.

Keep temporary artifacts until independent review and knowledge transfer are complete. Before final merge:

1. move durable decisions into ADRs or current-state documentation;
2. update user, operational, security, and architecture documentation;
3. move unresolved work to `NEXT_STEPS.md` or an issue;
4. remove the completed temporary work directory unless project policy retains it;
5. reset `CURRENT_PLAN.md`;
6. run `./scripts/verify.sh` again.

Git history and the pull request preserve the temporary planning trail.

## Quality-gate interface

Agents, developers, reviewers, and CI use the same commands:

```bash
./scripts/format.sh --check
./scripts/lint.sh
./scripts/test.sh
./scripts/check-dependencies.sh
./scripts/security.sh
./scripts/build.sh
./scripts/check-work-state.py
./scripts/check-docs.py
./scripts/verify.sh
```

During implementation, agents run focused checks. Before completion, the implementer and reviewer run the relevant full checks. CI runs `./scripts/verify.sh` independently.

Never accept statements such as "tests should pass" as verification. The completion report must list commands actually executed, their results, and any skipped checks.

## Dependency and supply-chain policy

`scripts/check-dependencies.sh` applies:

- `config/dependency-policy.conf`;
- `config/dependency-denylist.txt`;
- optional `config/dependency-allowlist.txt`;
- lockfile and floating-version rules;
- OSV-Scanner and Trivy when installed;
- ecosystem-specific scanners;
- an optional approved reputation command.

New runtime dependencies require documented necessity, alternatives, maintenance status, provenance, license, vulnerabilities, install behavior, transitive risk, version pinning, and an exit strategy.

## Documentation maintenance

The repository stores current truth, durable decisions, and actionable next steps—not chat transcripts or a chronological work diary.

During planning and closeout, material user instructions are classified as:

- task-only instruction;
- requirement or acceptance criterion;
- durable project rule;
- architecture decision;
- operational or security constraint;
- future work;
- transient conversation detail.

Only accepted durable information is moved into canonical project documentation. Use ADRs for significant decisions and Git/PR history for historical process details.

`./scripts/check-docs.py` checks local links, active-plan pointers, unresolved placeholders, document budgets, and oversized active work items. Use the documentation curator during significant closeout, before releases, after major architecture changes, or when consistency warnings appear.

## Directory overview

```text
.
├── AGENTS.md
├── .aiassistant/
│   ├── rules/
│   └── review/self-review.md
├── config/
│   ├── ai-project.yaml
│   └── dependency-*.txt
├── docs/
│   ├── requirements/
│   ├── architecture/
│   │   └── decisions/
│   └── ai/
│       ├── PROJECT_CONTEXT.md
│       ├── CURRENT_PLAN.md
│       ├── NEXT_STEPS.md
│       ├── agents/
│       ├── templates/
│       └── work/
├── scripts/
│   ├── create-project.sh
│   ├── create-project.ps1
│   ├── bootstrap.sh
│   ├── bootstrap.py
│   └── verify.sh
└── .github/workflows/ci.yml
```

## Initial readiness checklist

- [ ] Template copied without `.git/`, `.idea/`, caches, or local environment files.
- [ ] `config/ai-project.yaml` configured.
- [ ] Bootstrap completed.
- [ ] Required Python, frontend, shell, .NET, and scanner tools installed.
- [ ] IntelliJ Self-Review rules path configured.
- [ ] `engineering-knowledge` enabled or disabled intentionally.
- [ ] Project README and context completed.
- [ ] Architecture and trust boundaries documented.
- [ ] Dependency policy reviewed.
- [ ] All mandatory quality gates configured and passing.
- [ ] GitHub CI and branch protection configured.
- [ ] Fresh-context review of the generated project skeleton completed.

## License

Add the license appropriate for the new project. This template does not impose one.
