You are a senior software engineer specializing in security remediation and regression testing. Your task is to generate unit tests that prove Checkmarx path-traversal fixes preserve the original application behavior, without altering the fixes themselves.

**Critical constraint:** paths and parameters in these tests must NOT be fully mocked — construct them using the actual configuration values so the tests exercise real PROD and UAT path resolution logic, exactly as the application does at runtime.

I have access to two branches:
- `<MAIN_BRANCH>` — the original code, pre-fix
- `<CHECKMARX_BRANCH>` — contains the Checkmarx fixes for path traversal vulnerabilities

Execute the following:

1. **Diff analysis:** Compare `<MAIN_BRANCH>` against `<CHECKMARX_BRANCH>` and identify the exact lines, functions, and logic changed to remediate the path traversal issues. Summarize what changed and why it's security-relevant.

2. **Test branch setup:** Create a new branch from the same revision as `<MAIN_BRANCH>`, prior to the Checkmarx changes.

3. **Targeted test generation:** Write unit tests covering the specific functions and code paths identified in step 1 — not the whole module, just the affected logic. Tests must use real path/parameter construction (per the constraint above) for both PROD and UAT configurations, not synthetic or fully mocked values.

4. **Baseline capture:** Run these tests against `<MAIN_BRANCH>` and confirm they pass, establishing the pre-fix behavioral baseline. Report the results.

5. **Fix validation:** Merge or apply `<CHECKMARX_BRANCH>` into the test branch and re-run the identical tests. Confirm all tests still pass — this proves the security fix eliminates the vulnerability while preserving the original functional behavior.

Report any test that fails at either stage, including which specific line or function caused the failure and why. Do not modify the Checkmarx fix logic to make tests pass — if a test fails after the fix is applied, treat it as a genuine functional regression and report it as such.
