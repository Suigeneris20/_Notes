You have access to the attached log file and the specified branch of this repository. Your task is a fix-and-test loop: resolve every error present in the log, then run the full unit test suite across the entire repo, and keep iterating until all tests pass with zero failures.

**Phase 1 — Fix the logged errors:**
Read the attached log carefully. Identify every error, exception, and failure it contains. Trace each one to its root cause in the codebase and apply the minimal fix that resolves it without touching unrelated logic.

**Phase 2 — Run the full test suite:**
After applying fixes, run all unit tests across the entire repo. Do not limit the run to the files you touched — run everything. Capture the full output.

**Phase 3 — Iterate until clean:**
If any tests fail, diagnose each failure and apply the necessary fixes. Re-run the full suite. Repeat this loop until every test passes. Do not stop at "most tests pass" — the exit condition is a fully green test run.

**Constraints:**
- Work only on the specified branch — do not switch branches or create new ones
- Keep each fix minimal and targeted; do not refactor code unrelated to a failing test or logged error
- Preserve all existing interfaces, API contracts, and public-facing behavior unless a logged error directly requires changing them
- If a fix for one error causes a previously passing test to break, treat that regression as a new failure and resolve it before finishing

When done, summarize every change made, the root cause it addressed, and confirm the final test run result.
