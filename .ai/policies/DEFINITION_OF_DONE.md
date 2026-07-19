# Definition of done

A change is complete only when all applicable items are satisfied.

## Requirements

- [ ] The accepted problem and outcome are clear.
- [ ] Acceptance criteria are testable and met.
- [ ] Scope and non-goals were respected.
- [ ] Assumptions and deviations are explicit.

## Implementation

- [ ] The smallest coherent solution was implemented.
- [ ] Compatibility and migration implications were addressed.
- [ ] New dependencies were justified and reviewed.
- [ ] No unrelated cleanup or generated local state is included.

## Tests and verification

- [ ] Every behavior change has an appropriate automated test or documented exception.
- [ ] Relevant negative and boundary cases are covered.
- [ ] Focused checks pass.
- [ ] `./.ai/tools/verify.sh` was executed.
- [ ] Every skipped or unavailable mandatory check is reported as incomplete.

## Security and operations

- [ ] Security, privacy, and trust-boundary implications were assessed.
- [ ] Logging, metrics, tracing, alerts, and runbooks were updated where needed.
- [ ] Rollback or recovery is understood for risky changes.

## Documentation and review

- [ ] Human-facing documentation matches current behavior.
- [ ] Agent context and architecture documents are current.
- [ ] Obsolete documentation was removed.
- [ ] Independent review found no unresolved `P0` or `P1` issue.
- [ ] Residual risks and next steps are concise and explicit.
