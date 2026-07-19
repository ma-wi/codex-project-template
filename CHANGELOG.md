# Changelog

Record release-relevant user-visible changes. Do not use this file as an implementation diary.

## Unreleased

### Added

- Added fail-closed committed gate defaults, locked CI setup, recursive dependency-policy coverage, template self-tests, and Linux/Windows copy-safety tests.
- Added durable specifications, explicit change classes, conditional review lenses, and a one-requirement-per-worktree model.
- Added configured-project readiness checks and executable zero-test/missing-tool regressions for generated stack gates.

### Changed

- Reduced the default workflow to planner, implementer, and independent reviewer roles.
- Made accepted specifications durable and temporary plans disposable after reviewed closeout.
- Pinned bootstrap tooling and CI actions and moved generated gate commands to versioned `.ai/config/project.defaults.env`.
- Reduced the default planner context, made lifecycle ownership explicit, and required an explicit .NET test project with non-zero TRX results.

### Fixed

- Prevented mandatory quality gates from passing through unconfigured skips.
- Prevented force-copy cleanup from deleting unrelated target content and constrained configured paths to the repository.
- Fixed dependency-policy override propagation and lockfile checks for nested profiles.
- Prevented local overrides from weakening full verification, normalized lifecycle paths before containment checks, and rejected unsupported Poetry/Cargo source dependencies.

### Security

## 2026-07-19

- Bootstrap can initialize uv Python tooling and scaffold an optional Vite React frontend with quality/test dependencies.
