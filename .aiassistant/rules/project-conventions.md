# Project conventions

- Treat `AGENTS.md` as the binding instruction file for coding agents.
- Read `.ai/project.yaml` before substantial work.
- For behavioral or multi-file changes, follow `.ai/policies/WORKFLOW.md`.
- Keep active plans and independently verifiable tasks in the temporary work directory referenced by `.ai/CURRENT_PLAN.md`.
- Do not invent commands, architecture, or conventions when the repository defines them.
- Keep changes scoped, tested, secure, and documented.
- Run `./.ai/tools/verify.sh` before claiming completion.
- Never expose secrets, credentials, production data, or private keys.
- The production-access prohibition in `AGENTS.md` is absolute: never access production or run anything that targets or may affect it; treat ambiguous targets as production and stop.
