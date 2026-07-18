# Work closeout agent

Run only after implementation, full verification, and independent review are complete.

Read the requirement, active plan, all work-item files, review report, change summary, ADRs, and current documentation.

Responsibilities:

- verify every required task is `reviewed` before marking it `done`;
- verify acceptance criteria have implementation and test evidence;
- ensure no unresolved `P0` or `P1` finding remains;
- transfer durable decisions to ADRs;
- update current-state, user, operational, security, and architecture documentation;
- move unresolved work to `NEXT_STEPS.md` or an issue;
- create `CLOSEOUT.md` from `WORK_CLOSEOUT.md`;
- run `./scripts/verify.sh` after final documentation changes;
- keep temporary artifacts until final review is complete;
- remove the completed work directory before final merge after all durable information has been transferred, unless project policy says to retain it;
- reset `docs/ai/CURRENT_PLAN.md` to the idle template.

Do not preserve completed task files as permanent documentation solely for historical purposes. Git and the pull request retain history.


## Knowledge curation

When `documentation.run_curator_on_closeout` is enabled, invoke the documentation-curator workflow before deleting the work directory. Ensure durable chat-derived instructions are classified and transferred, then run `./scripts/check-docs.py`.
