I need you to compare two Git branches for Checkmarx path traversal findings and fix the inconsistencies between them, without changing any behavior. The two branches are the ones I specified above, and I refer to one of them as `renew`. Each branch has its own Checkmarx XML report; use them as the source of truth for what is flagged, active, or marked non-exploitable.

**Hardest constraint: zero behavior change.** For every fix you propose, the function's output and the resulting path must be identical to what `renew` produces today, including whether the path is relative or absolute. Path state must be preserved exactly. A fix that satisfies Checkmarx but alters a returned path, even trivially (normalization, a trailing slash, resolution to absolute), is a failure. Verify each fix by comparing the original `renew` behavior to the new behavior on the same inputs, and show that comparison.

**Part 1: Cross-branch discrepancies**
1. Parse both XML reports and filter to path traversal findings only.
2. Locate code that is essentially the same in both branches and has Checkmarx-recognized sanitization or validation in both.
3. For each such pair where one branch's report marks the finding non-exploitable (or not flagged) and the other's reports it active, determine why the results differ despite validation in both. Look at where the sanitization sits relative to the sink, how the data flows from source to sink, and any structural differences in the surrounding code that affect how Checkmarx's data-flow analysis reads it.
4. Once the cause is understood, propose a fix for the branch where the finding is active. You may move the sanitization to match the structure of the branch where it's clean. Keep the same validation logic. Only its position or structure may change, and only if that helps Checkmarx recognize it.

**Part 2: Unsanitized findings in `renew`**
For path traversal findings flagged in `renew` that have no attempted validation or sanitization at all, sanitize them using the existing functions in the project's `path_validation.py` scripts (find them in the codebase and read them before use). Do not write new sanitizers when an existing one fits. For each, compare the original output and behavior to the post-sanitization behavior and confirm the output is unchanged. If an existing `path_validation.py` function would alter the output for legitimate inputs, say so and propose an alternative that preserves it.

**What to report**
For each finding, give the file and line, which branch(es) it affects, the root cause of the discrepancy (Part 1) or the missing sanitization (Part 2), the exact diff, and the behavior-equivalence check showing identical output and path state. List separately any finding where you could not guarantee zero behavior change, with the reason, rather than applying a risky fix.
