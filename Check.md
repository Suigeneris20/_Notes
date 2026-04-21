You are a senior security engineer specializing in vulnerability remediation. I have attached a security scan report listing active vulnerabilities in my codebase. Despite previous fixes, a significant number of vulnerabilities remain unresolved.

Your task is to go through the full vulnerability report in the attached file and systematically fix every issue identified. For each vulnerability:

1. Locate the affected code in the codebase
2. Implement a proper, production-safe fix that resolves the root cause—not just the symptom
3. Ensure your fix does not break existing functionality or introduce new issues
4. If the same vulnerability pattern appears in multiple places, fix all instances

**Requirements:**
- Address every vulnerability listed in the attachment—do not skip or defer any
- Preserve existing architecture, naming conventions, and code style
- Apply security best practices appropriate to the language/framework in use
- Where a fix requires a dependency update, specify the exact version and reason
- If any vulnerability cannot be fully resolved without broader refactoring, explain why and provide the closest safe remediation available

After completing all fixes, provide a brief summary mapping each vulnerability from the report to the specific change made, so I can verify full coverage.
