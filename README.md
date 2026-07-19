# Codex project template

A secure, review-oriented starting point for complex projects implemented with coding agents in IntelliJ IDEA. Python is enabled by default; React/TypeScript, Bash, and .NET/Visual Basic/PowerShell are optional stacks.

The intended lifecycle uses three fresh agent contexts:

```text
accepted requirement → planner → implementer → independent reviewer
                                      ↑ remediation ↓
                                  curation and closeout
```

`AGENTS.md` contains compact binding rules. `.ai/policies/WORKFLOW.md` is the single canonical lifecycle description. The `.ai/` directory isolates agent configuration, tooling, policies, roles, templates, and temporary state from application-owned paths.

## Create a project

Do not copy the template's `.git`, IDE/agent state, local environments, caches, or this setup README. Preview first.

### Linux, macOS, Git Bash, or WSL

```bash
./.ai/tools/create-project.sh --dry-run /path/to/new-project
./.ai/tools/create-project.sh /path/to/new-project
cd /path/to/new-project
```

### Windows PowerShell

```powershell
.\.ai\tools\create-project.ps1 -TargetDirectory "C:\Projects\new-project" -WhatIf
.\.ai\tools\create-project.ps1 -TargetDirectory "C:\Projects\new-project"
Set-Location "C:\Projects\new-project"
```

The target must be empty unless `--force` or `-Force` is explicitly supplied. Force mode may overwrite same-named template files but must not delete unrelated target content. Dry-run and WhatIf do not create an environment or modify the target.

The copy contains reusable project rules, security policy, configuration, project CI, bootstrap, and verification scripts. It deliberately omits template-only state:

- `README.md`, `CHANGELOG.md`, and `CONTRIBUTING.md`;
- `tests/` and temporary `.ai/work/` artifacts;
- this template repository's own hardening/control-plane requirements, specifications, and ADR;
- the project-copy scripts and `.ai/tools/verify-template.sh`;
- `.ai/config/copy-exclude.txt`, the template-maintenance manifest for copy boundaries;
- the template-only Windows copy-test workflow;
- Git/IDE/agent state, local environments, caches, coverage, and build outputs.

Bootstrap creates the new project README. Create the project changelog and contributing guide only when their actual policies and release process are known. `SECURITY.md` remains as a required project policy scaffold and must be completed with the real private reporting channel.

The copied project does not inherit template self-tests. React bootstrap creates a
scaffold smoke test; other stacks must provide meaningful project tests, and the Bash
gate fails explicitly when `tests/shell` is absent. Before bootstrap, verification
fails with a bootstrap-required message.

## Configure and bootstrap

Edit `.ai/project.yaml` before bootstrap:

- replace `project.name: "CHANGE_ME"`;
- enable only required stacks;
- choose the React package manager and project-relative directories;
- when .NET is enabled, identify its solution and explicit test project;
- enable the engineering-knowledge MCP only when it is actually configured.

All configured paths must remain below the repository root. Absolute paths and `..` traversal are rejected.

Run:

```bash
./.ai/tools/bootstrap.sh
```

Install the template's pinned uv version shown in `.github/workflows/ci.yml` when Python is enabled and the Node.js version from `.node-version` when React is enabled. Bootstrap rejects different versions so generated manifests and lockfiles do not depend silently on the developer machine. For React projects using pnpm or Yarn, bootstrap writes matching `packageManager` metadata so frozen installs use the intended tool family.

Or on Windows without Bash:

```powershell
python .\.ai\tools\bootstrap.py
```

Bootstrap may initialize the configured Python or React project and install the explicitly configured, pinned development tools. It then generates:

```text
.ai/config/project.defaults.env
```

This file is the versioned source of truth for full local verification and CI and
must be committed. Machine-local command overrides belong in ignored
`.ai/config/project.env`; focused gates use them, while `verify.sh` ignores them.
They cannot weaken mandatory policy. Never put secrets in either file.

Review all generated manifest and lockfile changes before committing them.

## Initialize Git and GitHub

```bash
git init
git add .
git commit -m "Initialize project from agent template"
git branch -M main
git remote add origin git@github.com:ORGANIZATION/REPOSITORY.git
git push -u origin main
```

Recommended repository settings:

- protect `main` and require pull requests;
- require the CI verification job;
- prevent direct pushes;
- enable secret scanning, dependency alerts, and code scanning where available;
- use environment protection and OIDC rather than long-lived deployment secrets when deployment is later added.

The included workflow uses least-privilege read permissions, pinned action commits,
versioned runner labels, concurrency cancellation, timeouts, and `./.ai/tools/verify.sh`.

## Initial product planning

Do not invent the final architecture during template setup. First store the supplied requirement under:

```text
docs/requirements/REQ-001-initial-project.md
```

Then start a fresh planning agent. The planner performs discovery when material product or architecture decisions remain unclear, creates the durable specification under `docs/specifications/`, proposes necessary ADRs, and creates only the temporary implementation plan/tasks needed for execution. The named authorized decision owner—not the planning agent—records acceptance.

Accept the specification and architecture decisions before starting the implementation agent.

## Agent roles

Use fresh contexts for the three standard roles. Point each agent at `AGENTS.md`,
`.ai/project.yaml`, its role file, and the accepted requirement or active plan:

- Planner: `.ai/roles/planner.md`
- Implementer: `.ai/roles/implementer.md`
- Independent reviewer: `.ai/roles/code-reviewer.md`

Return findings to the implementation agent. `P0` and `P1` remediations require a fresh reviewer pass.

## Change classes and context cost

- **Trivial:** mechanical and behavior-neutral; no work directory.
- **Normal:** compact plan, tests, full verification, independent review.
- **Significant:** discovery when needed, durable specification, accepted architecture decisions, task decomposition, full verification, independent review, and risk-triggered specialist review.

Only the three primary roles are standard. Security, test, dependency, and documentation guidance are conditional review lenses in `.ai/policies/review-lenses.md`. Agents should load only applicable policy files rather than the entire control plane.

Use one active requirement per Git branch/worktree. Create another worktree when planning a future feature while implementation is still active.

## Durable and temporary information

Durable:

- `docs/requirements/` — accepted source requirements;
- `docs/specifications/` — observable behavior, acceptance criteria, and stable test seams;
- `docs/architecture/decisions/` — accepted architecture decisions;
- maintained product, operation, security, and architecture documentation;
- code and tests.

Temporary:

- `.ai/work/<requirement-id>/PLAN.md`;
- task status files;
- local review and closeout notes.

Keep temporary files through independent review. During closeout, first transfer durable information, then run final verification, summarize the result in the pull request, remove the temporary work directory, and reset `CURRENT_PLAN.md`.

## Verification

Before bootstrap, run only:

```bash
./.ai/tools/verify.sh
```

It recognizes `project.name: "CHANGE_ME"` and validates the template itself:
documentation, shell/Python syntax, copy safety, dependency policy, bootstrap
generation, and lifecycle state checks.

After bootstrap, focused gates are available for configured projects:

```bash
./.ai/tools/format.sh --check
./.ai/tools/lint.sh
./.ai/tools/test.sh
./.ai/tools/check-dependencies.sh
./.ai/tools/security.sh
./.ai/tools/build.sh
./.ai/tools/verify.sh
```

`verify.sh` also runs `./.ai/tools/ci-setup.sh` for configured projects, then every
mandatory gate. It ignores machine-local overrides and does not treat a mandatory
skip as success.

## Dependency and supply-chain baseline

The committed policy requires lockfiles and rejects obvious floating sources. It inspects supported manifests recursively, including frontend subdirectories, Python dependency groups, `uv.lock`, Node lockfiles, Cargo/Go integrity files, and .NET package lockfiles.

New or upgraded dependencies still require human/agent review of necessity, alternatives, provenance, maintenance, license, install behavior, transitive risk, known vulnerabilities, pinning, and replacement strategy. Automated scanners cannot prove that a package is trustworthy.

Use locked/frozen installs in CI. Pin CI actions to reviewed commit SHAs. Optional hosted reputation services must be reviewed for privacy before receiving private dependency metadata.

## IntelliJ IDEA

1. Open the new project directory.
2. Confirm the agent can read the root `AGENTS.md`.
3. Keep command approval and sandbox settings restrictive.
4. Configure JetBrains Project Rules from `.aiassistant/rules/` only when the IDE does not already load `AGENTS.md`.
5. Set the AI Self-Review rules path to:

```text
$PROJECT_DIR$/.aiassistant/review/self-review.md
```

6. Enable the optional engineering-knowledge MCP only when allowed by `.ai/project.yaml`.

## Supported stack notes

- Python uses the pinned `uv` bootstrap, a project-local environment, Ruff, mypy, pytest, Bandit, pip-audit, and build.
- React uses a pinned Vite creator, TypeScript, ESLint, Prettier, Vitest, Testing Library, locked package installation, type checking, and accessibility-focused review.
- React uses fixed frozen installation commands: `npm ci`, `pnpm install --frozen-lockfile`, or `yarn install --immutable`. Bootstrap writes the pnpm/Yarn `packageManager` metadata for React projects that use those managers.
- Bash requires ShellCheck and uses Bats when meaningful shell tests exist.
- .NET uses restore lock mode, format verification, warning-as-error builds, tests, and vulnerable-package inspection. PSScriptAnalyzer and Pester checks are added automatically when project PowerShell files are present during bootstrap.

Remove unused stacks and their rules from a concrete project to reduce context and maintenance cost.

## Optional governance templates

- Use `.ai/templates/THREAT_MODEL.md` for public APIs, sensitive data, identity,
  file parsing, networks, irreversible migrations, or other security-relevant work.
- Use `.ai/templates/OWNERSHIP.md` to record decision owners, review owners, and
  branch-protection expectations before complex implementation begins.

## Updating pinned tool versions

Tool versions are pinned exactly for reproducible bootstraps. When bumping them, change every copy together, then run `./.ai/tools/verify-template.sh`:

- `UV_VERSION`, `VITE_VERSION`, `PNPM_VERSION`, `YARN_VERSION`, `PYTHON_DEV_DEPENDENCIES`, and `REACT_QUALITY_DEPENDENCIES` in `.ai/tools/bootstrap.py`;
- the `astral-sh/setup-uv` `version:` in `.github/workflows/ci.yml`;
- the pinned Ruff, mypy, and Bandit versions in `.ai/tools/verify-template.sh`;
- the runtime pins in `.python-version` and `.node-version`.

Confirm each version resolves on its registry before committing. Bootstrap rejects a mismatched local `uv` or Node.js so generated lockfiles do not depend on an unpinned machine.

## Template acceptance checklist

- [ ] Project name and enabled stacks are configured.
- [ ] Bootstrap completed and generated changes were reviewed.
- [ ] `SECURITY.md`, `.ai/PROJECT_CONTEXT.md`, and required quality decisions are complete.
- [ ] `.ai/config/project.defaults.env`, manifests, and lockfiles are committed.
- [ ] `./.ai/tools/verify.sh` executes every mandatory project gate.
- [ ] GitHub branch protection requires CI.
- [ ] Review/decision ownership is documented for complex or sensitive projects.
- [ ] Threat model is completed when the project has a security-relevant surface.
- [ ] Initial requirement is accepted.
- [ ] Durable specification and architecture decisions are accepted.
- [ ] A fresh planning-to-review lifecycle has been exercised once.

## License

Choose and add the license appropriate for the generated project. The template does not impose one.
