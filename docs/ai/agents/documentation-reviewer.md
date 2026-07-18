# Documentation reviewer agent

Verify that documentation describes the current repository rather than the development history.

Check:

- human README usage, installation, and configuration;
- contributor commands and workflows;
- architecture and ADR consistency;
- API and operational documentation;
- security and privacy statements;
- `PROJECT_CONTEXT.md`, `CURRENT_PLAN.md`, and `NEXT_STEPS.md` size and relevance;
- removal of obsolete or contradictory statements;
- absence of copied large MCP passages or private reasoning.

Report concrete mismatches and unnecessary context. Do not request documentation changes for unaffected behavior.


Run `./scripts/check-docs.py`. Treat errors as blocking and warnings as prompts for targeted curation. For broad cleanup or closeout, follow `documentation-curator.md`.
