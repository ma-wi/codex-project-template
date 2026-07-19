# Security and dependency rules

Apply when authentication, authorization, input handling, files, processes, networks, persistence, secrets, or dependencies are involved.

- Follow `.ai/policies/SECURITY_GUIDELINES.md` and `.ai/policies/DEPENDENCY_POLICY.md`.
- Treat every new or upgraded package as a supply-chain change.
- Require a lockfile, fixed source, justification, license review, vulnerability scan, and provenance assessment.
- Reject denied, unnecessary, unmaintained, suspicious, or unexplained packages.
- Record residual risks and time-bounded exceptions.
