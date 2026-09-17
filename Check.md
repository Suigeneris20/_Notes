You are a senior application security engineer with expertise in remediating SAST findings while preserving traceability for scanner verification.

Search the current repository for all instances of `path_validation.py` (I expect roughly 36 duplicates, but confirm the actual count and locations) and consolidate them into a single shared security utilities location. The hard constraint: Checkmarx must still be able to trace the fix path from source to taint to sink after consolidation. If the unified function is called in a way that breaks Checkmarx's data-flow tracing (e.g., the sanitization happens too far from the sink, or is abstracted behind a wrapper Checkmarx can't follow), the remediation will not register as fixed even though the code is safe — so the consolidated function's placement and call pattern must keep the taint path intact.

Before making changes:

1. Locate every copy of `path_validation.py`, and diff them against each other to confirm they're functionally identical (or note any meaningful divergences — different callers may have introduced subtly different validation logic, and those differences must be preserved or deliberately reconciled, not silently dropped).
2. Identify the correct shared location for the unified utility based on the existing project structure and import conventions (e.g., a `common/security/` or `utils/security/` module, matching however this codebase already organizes cross-cutting utilities).
3. Check whether the project already has an existing Checkmarx suppression, custom query, or sanitizer annotation that references the old `path_validation.py` locations — these will need to be updated to point at the new consolidated location, or Checkmarx will re-flag the callers as unresolved findings.

Then:

- Replace all duplicate copies with imports from the single consolidated module.
- Update every caller to use the new import path.
- Ensure the validation function's signature and call site keep the taint flowing directly from the tainted input to the sanitizer to the sink, without intermediate abstraction that would obscure the trace for Checkmarx.
- Flag any caller where the surrounding code structure makes it unclear whether Checkmarx's taint engine will still resolve the fix, so I can review those manually.

Do not alter the actual validation logic itself unless you find a genuine bug or an inconsistency between duplicates — the goal is unification and traceability, not a rewrite of the security logic.
