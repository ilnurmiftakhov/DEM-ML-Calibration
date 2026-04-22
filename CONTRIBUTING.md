# Contributing

Thank you for your interest in this repository.

This project is currently maintained as a **research-first pilot repository**. Contributions are welcome, but they should preserve reproducibility, source traceability, and honest reporting of limitations.

## Scope of contributions

Useful contributions include:
- bug fixes in experiment scripts;
- reproducibility improvements;
- documentation improvements;
- cleaner environment/setup instructions;
- additional validation utilities;
- safer data-handling and packaging improvements.

Contributions that change scientific claims, metrics, figures, or conclusions should be accompanied by:
- the exact code changes;
- regenerated artifacts where relevant;
- a short explanation of what changed and why.

## Before opening a pull request

Please check that:
1. scripts still run from the repository root;
2. paths are relative and reproducible;
3. no manuscript drafts are added to Git;
4. no temporary Office files, caches, or local environments are committed;
5. scientific claims remain consistent with the actual outputs.

## Branch and commit guidance

- use focused branches or small PRs;
- keep commits atomic;
- prefer descriptive commit messages, for example:
  - `Fix path handling in experiment scripts`
  - `Update README and setup instructions`
  - `Add bootstrap summary export`

## Data and manuscript policy

Please do **not** commit:
- article drafts;
- editorial submission materials;
- private or restricted dataset derivatives unless explicitly approved.

See `LICENSE`, `.gitignore`, and repository notes for current policy.

## Reporting issues

When reporting a bug, please include:
- the command that was run;
- the environment (OS, Python version);
- the observed error;
- the expected behavior;
- if relevant, the affected file or artifact.

## Review standard

This repository favors:
- evidence over appearance;
- reproducibility over convenience;
- explicit limitations over overstated claims.

If a change improves polish but weakens auditability, reproducibility, or honesty of interpretation, it is unlikely to be accepted.
