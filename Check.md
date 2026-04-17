You are an expert Git engineer. I need you to provide the exact shell commands to:

1. Fetch and check out the latest `main` branch
2. Switch back to my current branch
3. Merge `main` into my current branch
4. Resolve all merge conflicts **without changing any existing code** — meaning conflicts should always be resolved in favor of my current branch's version (using `ours` strategy or manual conflict resolution that keeps my branch's code intact)

Provide the precise sequence of Git commands to accomplish this, including how to handle conflict resolution automatically where possible (e.g., `git merge -X ours` or equivalent), and how to verify the merge completed cleanly. If there are edge cases or caveats I should be aware of (e.g., binary files, deleted files, rename conflicts), note them briefly.
