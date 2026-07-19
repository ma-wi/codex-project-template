# Quality gates

Customize this file during project bootstrap. Mark each gate as mandatory, conditional, or not applicable.

| Gate | Policy | Canonical command | Notes |
|---|---|---|---|
| Formatting | Mandatory | `./.ai/tools/format.sh --check` | No formatting drift |
| Linting | Mandatory | `./.ai/tools/lint.sh` | Include project style rules |
| Static typing | Conditional | Included in lint/build | Required for typed projects |
| Unit tests | Mandatory | `./.ai/tools/test.sh` | Behavior changes require tests |
| Integration tests | Conditional | Included in test command | Required for component interactions |
| End-to-end tests | Conditional | Project-specific | Required for critical user flows |
| Build/package | Mandatory | `./.ai/tools/build.sh` | Must produce expected artifact |
| Secret scan | Conditional until configured | `./.ai/tools/security.sh` | Make mandatory before handling credentials or production deployment |
| Dependency scan | Mandatory | `./.ai/tools/security.sh` | Include lockfile-aware audit |
| Static security analysis | Conditional | `./.ai/tools/security.sh` | Mandatory for security-sensitive code |
| License policy | Conditional | Project-specific | Required when distribution demands it |
| Migration validation | Conditional | Project-specific | Include upgrade and rollback behavior |
| Documentation check | Mandatory | Review | Changed behavior must be documented |
| Independent review | Mandatory for normal/significant work | PR or review report | Fresh context required |

## Gate execution policy

During implementation, run the smallest relevant checks. Before completion, run all configured mandatory gates through `./.ai/tools/verify.sh`.

A non-mandatory gate may be skipped only when:

- it is explicitly not applicable; or
- the environment cannot execute it and the limitation is reported.

A skipped mandatory gate fails immediately. Gate commands and required flags are committed in `.ai/config/project.defaults.env`; ignored `.ai/config/project.env` values are local overrides only.

## Failure policy

When a gate fails:

1. preserve the failure evidence;
2. identify the root cause;
3. fix the implementation or test, not the gate;
4. re-run the focused gate;
5. re-run the full verification suite.

Do not disable rules, delete tests, reduce coverage, suppress findings, or change thresholds merely to obtain a passing result.

## Required project decisions

- Minimum coverage policy:
- Supported runtime matrix:
- Warning-as-error policy:
- Security severity threshold:
- Dependency update policy:
- Flaky-test policy:
- CI required checks:

## Dependency and package gate

Run `./.ai/tools/check-dependencies.sh` for changes to manifests, lockfiles, build logic, registries, or generated dependency metadata. It checks repository policy, deny/allow lists, lockfile requirements, floating versions, known vulnerabilities, license risks, and optional package-reputation tooling. The full `verify.sh` workflow also runs this gate.
