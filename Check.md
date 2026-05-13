You are a senior DevOps and Python engineer. I have two repositories uploaded/attached. Your task is to work through both in sequence, resolving dependency and test issues as described below.

**Repo 1 — Fix and test:**
- Run the full `pytest` test suite on Repo 1.
- Identify any failing tests and trace failures back to dependency or configuration issues.
- Resolve all issues using the packages and versions specified in `requirements.txt` as the source of truth.
- Re-run `pytest` after fixes and confirm all tests pass.

**Repo 2 — Update packages and test:**
- Switch to the specified branch in Repo 2.
- Update the `resource` package to match exactly how it is defined/pinned in Repo 1's `main` branch.
- Update the `foi-shared-utils` package to point to the branch in Repo 1 (use a direct branch reference link, e.g., a VCS dependency pointing to Repo 1's branch URL).
- Run the full `pytest` test suite on Repo 2 after these updates.
- Resolve any failing tests and confirm all tests pass.

For each repo, clearly document: what was broken, what changes you made, and the final passing test output. If a dependency conflict cannot be resolved cleanly, explain the conflict and the best available resolution path.
