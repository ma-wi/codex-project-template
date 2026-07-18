# Work closeout: <requirement-id>

- Requirement:
- Work directory:
- Final status: completed | partially-completed | cancelled
- Date:
- Owner/agent:

## Completion checks

- [ ] Every required task is `done`.
- [ ] Every acceptance criterion has implementation and verification evidence.
- [ ] No unresolved `P0` or `P1` review finding remains.
- [ ] Full repository verification completed.
- [ ] Durable architecture decisions were moved to ADRs.
- [ ] Current-state documentation was updated and obsolete text removed.
- [ ] Remaining work was moved to `NEXT_STEPS.md` or an issue.
- [ ] Temporary artifacts contain no information that must remain durable.
- [ ] Durable user instructions were classified and transferred to canonical documents.
- [ ] Task-only instructions remain temporary and no chat transcript was copied.
- [ ] Documentation budgets and consistency were checked with `./scripts/check-docs.py`.
- [ ] A curator review was performed when required by `config/ai-project.yaml`.

## Durable artifacts created or updated

- Requirements:
- ADRs:
- Architecture and operational documentation:
- README or user documentation:
- Changelog or release notes:

## Knowledge transfer

| Information | Classification | Canonical destination |
|---|---|---|
| | current state / rule / ADR / operations / security / future work | |

## Verification evidence

| Command or review | Result | Evidence or notes |
|---|---|---|
| `./scripts/verify.sh` | pass/fail/not run | |
| Independent review | pass/fail/not run | |

## Residual risks and follow-up work

## Cleanup decision

- [ ] Keep the work directory until merge.
- [ ] Delete temporary task, plan, review, and closeout files before final merge after durable information has been transferred.
- [ ] Reset `docs/ai/CURRENT_PLAN.md` to its idle state.
