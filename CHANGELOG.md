# Changelog

Record release-relevant user-visible changes. Do not use this file as an implementation diary.

## Unreleased

### Added

- Added fail-closed committed gate defaults, locked CI setup, recursive dependency-policy coverage, template self-tests, and Linux/Windows copy-safety tests.
- Added durable specifications, explicit change classes, conditional review lenses, and a one-requirement-per-worktree model.

### Changed

- Reduced the default workflow to planner, implementer, and independent reviewer roles.
- Made accepted specifications durable and temporary plans disposable after reviewed closeout.
- Pinned bootstrap tooling and CI actions and moved generated gate commands to versioned `.ai/config/project.defaults.env`.

### Fixed

- Prevented mandatory quality gates from passing through unconfigured skips.
- Prevented force-copy cleanup from deleting unrelated target content and constrained configured paths to the repository.
- Fixed dependency-policy override propagation and lockfile checks for nested profiles.

### Security

## 2026-07-19

- Bootstrap can initialize uv Python tooling and scaffold an optional Vite React frontend with quality/test dependencies.
