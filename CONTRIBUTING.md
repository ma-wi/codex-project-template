# Contributing

## Local setup

Document project-specific prerequisites and setup commands here.

```bash
cp scripts/project.env.example scripts/project.env
chmod +x scripts/*.sh
./scripts/verify.sh
```

## Change workflow

1. Start from an accepted requirement with testable acceptance criteria.
2. Update `docs/ai/CURRENT_PLAN.md` for non-trivial work.
3. Keep the change focused on the accepted scope.
4. Add or update tests with the implementation.
5. Run focused checks while developing.
6. Run `./scripts/verify.sh` before requesting review.
7. Update affected human and agent documentation.
8. Request an independent review.

## Pull requests

A pull request should explain:

- the problem and chosen solution;
- acceptance criteria covered;
- meaningful design decisions and alternatives;
- verification commands and results;
- compatibility, migration, security, and operational implications;
- known limitations and follow-up work.

Do not combine unrelated cleanup with a functional change.

## Commit guidance

Prefer small, coherent commits that keep the repository buildable. Do not include secrets, generated local state, IDE-specific private settings, or unrelated formatting churn.
