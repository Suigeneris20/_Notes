You are a senior application security engineer who builds and maintains developer-facing security tooling, with deep expertise in Checkmarx SAST triage and false-positive analysis. Your task is to consolidate the separate Checkmarx skills we have built in this conversation into one organization-wide master skill, with a thorough README, that anyone in the company can clone and run against a repository or branch.

**Source material**

Use the separate per-vulnerability-type skills we developed earlier in this repo/project as the single source of truth. For each one, carry over everything it contains, including the most recent refinements: the caveats about accepted input and output types, the full set of reasons a finding can be a false positive, detection logic, and any sanitizer, validator, or framework-specific handling we established. If any earlier skill is missing from this conversation or its details are unclear, say so explicitly at the top of your response and flag it as a gap. Never invent vulnerability types, caveats, or false-positive reasons that we did not work on.

**What to build**

1. **One master Checkmarx skill** that unifies all per-vulnerability-type skills under a single entry point, keeping each type's logic intact and easy to locate.

2. **Vulnerability type selection.** The user can either (a) state the vulnerability type directly, or (b) provide an entire repo or branch and have the skill deduce which vulnerability issues are present, limited strictly to the types we have worked on. When deducing, the skill should show what it found and which type each finding maps to before analysing. When a finding falls outside the supported types, the skill should say so plainly instead of guessing.

3. **False-positive document workflow.** Whenever the skill automatically writes up a finding as a false positive:
   - If no false-positive document has been started in this session or repo, ask the user whether they want one started.
   - If one already exists, ask whether they want to add this finding to it.
   - The skill does not re-explain what the document is; it points to the docs README, where that is defined.

4. **A painstaking, all-encompassing README** in `docs/` (or the repo's equivalent docs location), written for people with no prior context. It should be clear, thorough, and easy to follow, and cover at minimum:
   - What the skill is, who it is for, and what problem it solves
   - Prerequisites and installation, including cloning the repo where the skill lives
   - Step-by-step usage: running against a whole repo, a single branch, or a specific vulnerability type, with copy-pasteable examples
   - The full list of supported vulnerability types, with a short description of each
   - Accepted input types and output types per vulnerability type, including the caveats we established
   - The complete catalogue of false-positive reasons per vulnerability type
   - **What a false-positive document is and exactly what it contains** (purpose, structure, each field and its meaning, when entries are added, and a worked example entry), since the skill's prompts point users here
   - How the interactive prompts work (vulnerability type selection and false-positive document start/append)
   - Limitations, known edge cases, and troubleshooting
   - How to extend the skill with a new vulnerability type or update an existing one

**Delivery requirements**

- The skill must be shareable across the organization: self-contained, consistently structured, and usable by someone who has only cloned the repo and read the README.
- Usage must stay simple: clone, point the skill at a repo or branch, and run it, with no complicated setup.
- Present the complete file and folder structure first, then the full contents of every file (the master skill file(s) and the README), ready to commit as-is.
- Write for a mixed audience of developers and security staff: plain language first, technical detail after.
