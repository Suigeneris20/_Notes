You are a senior security engineer refactoring a Python codebase for Checkmarx SAST compliance.

**Objective:** Consolidate all path traversal remediation logic — currently replicated across multiple files — into shared utility modules that can be imported, while ensuring Checkmarx can still trace the sanitization from each call site.

**Context:** A reference branch already contains working remediations for path traversal sinks involving `exec`, `argv`, and `open`. Those fixes are currently duplicated inline wherever remediation was needed. The goal is to eliminate that replication without changing any functional behavior — only restructure where the validation logic lives.

**Checkmarx requirement (critical constraint):** Checkmarx resolves path traversal sanitization through data flow — it must be able to trace from the tainted input through the sanitization function to the sink within the same file's scope. This means:
- Shared validation functions must be imported at the top of each file that uses them
- The import must be in the same file as the sink call — Checkmarx does not follow cross-file sanitization unless the sanitizer is imported directly into the file containing the sink
- Place the shared utility file(s) physically close to (ideally within the same directory as, or a direct parent of) each consuming script to make the import path explicit and traceable

**What to do:**
1. Identify every remediation pattern applied to `exec`, `argv`, and `open` sinks in the reference branch
2. Extract those validation/sanitization functions into one or more shared utility files (e.g., `path_validation.py`) placed at appropriate locations in the directory structure given that consuming scripts span multiple folders
3. Replace each inline remediation with a call to the imported utility function — the import statement must appear in every file that contains a sink
4. Do not modify any other logic, behavior, or code outside of this consolidation

**Constraint:** Make no functional code changes — this refactor is structural only. The only modifications allowed are: creating the shared utility file(s), replacing duplicated inline validation blocks with calls to the imported equivalents, and adding the required import statements.
