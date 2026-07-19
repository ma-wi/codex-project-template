# Requirement: Harden and streamline the coding-agent project template

## Problem

The template has duplicated agent guidance and several gaps between documented
fail-closed guarantees and their technical enforcement. New complex projects must
start from a secure, testable, reviewable control plane without unnecessary agent
context.

## Desired outcome

Copied projects enforce mandatory verification and repository boundaries, expose
incomplete bootstrap/security configuration, use an unambiguous agent lifecycle,
and load substantially less duplicated guidance.

## Functional requirements

- FR-1: Ignored local configuration must not weaken committed mandatory gates.
- FR-2: A mandatory test gate must fail when no meaningful tests exist.
- FR-3: Work-state paths must remain within their declared repository roots after
  normalization.
- FR-4: Bootstrap readiness must detect unfinished security and project policy
  scaffolds.
- FR-5: Dependency policy must fail closed on unsupported direct-dependency syntax
  and reject mutable or remote direct sources.
- FR-6: Decision acceptance, finding exceptions, review, and closeout ownership must
  be unambiguous.
- FR-7: Redundant policies and examples must be removed or consolidated without
  weakening the safety baseline.

## Non-functional requirements

- Preserve Linux and Windows project-copy behavior.
- Preserve the absolute production-access prohibition.
- Do not weaken existing checks or supported-stack verification.
- Keep source-template-only material out of copied projects.

## Acceptance criteria

- [x] AC-1: Local overrides can customize commands but cannot turn committed
  mandatory flags from `1` to `0`.
- [x] AC-2: Bash-only verification fails when its test suite is absent.
- [x] AC-3: Traversal paths in active work and specification pointers are rejected.
- [x] AC-4: A configured copied project fails documentation verification while the
  security reporting scaffold or mandatory project decisions remain incomplete.
- [x] AC-5: Unsupported requirement lines and remote/direct dependency sources fail
  dependency policy checks.
- [x] AC-6: Workflow documents identify the human decision owner and a distinct
  closeout responsibility; P0/P1 findings cannot be waived.
- [x] AC-7: Orphaned duplicate policies and the duplicate ADR example are removed;
  conditional guidance remains discoverable through a compact router.
- [x] AC-8: Linux and Windows copy boundaries remain covered, all configured stack
  gates have negative tests where applicable, and full template verification passes.

## Approval

- Owner: project owner
- Status: accepted
- Date: 2026-07-19
