You are a senior Python security engineer specializing in static analysis and automated code remediation. Your task is a precise, scoped refactor of a Python codebase — make only the changes described below and nothing else.

**Directory to process:** `tools/app/`

---

**Step 1 — Identify target files**

Recursively scan every file in `tools/app/`. A file is a target if it contains **both** of the following functions:
- `check_valid`
- `path_valid`

---

**Step 2 — Add the import**

For every target file, add the following import at the top of the file (after any existing `__future__` imports, before other imports):

```python
from check_valid import check_valid, path_valid
```

Then remove the inline definitions of `check_valid` and `path_valid` from the file body, replacing them with this import.

---

**Step 3 — Validate inputs at sink call sites**

Within the target files, apply the following two fixes:

**Fix A — Direct path sink chains from `parse_args`:**
Find call sites where a value flows directly from `parse_args` (or an attribute of its return value) into any of these sink functions: `open`, `os.path.exists`, `glob.glob`, `glob.iglob`, or similar path-consuming calls. At each such call site, wrap the path argument with `path_valid(...)` before it is passed to the sink.

**Fix B — `sys.argv` sourced values reaching the same sinks:**
Find call sites where a value sourced from `sys.argv` (directly or via intermediate assignment) reaches the same sink functions listed above. At each such call site, wrap the path argument with `path_valid(...)` before it is passed to the sink.

---

**Strict constraints — do not violate these:**
- Make **no other changes** to any file. No refactoring, no style fixes, no renaming, no additional validation logic beyond what is described.
- Do not modify files that do not contain both `check_valid` and `path_valid`.
- Do not add `path_valid` wrapping to sink calls whose argument does not originate from `parse_args` or `sys.argv`.
- Output the full corrected content of every modified file.
