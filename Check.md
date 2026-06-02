You are a senior DevOps and Ansible automation engineer specializing in CI/CD pipeline integration and Python dependency management.

I have a repository with a branch containing an `ansible/` folder and a `pipeline.yaml` CI/CD configuration. I need you to audit and fix the dependency wiring so that the SACCR package installed during the Ansible playbook execution (`main.yaml`) is explicitly the same artifact uploaded/published in `pipeline.yaml` — not a version resolved from a public index or cache — to eliminate a `cannot import` error at runtime.

**Your task:**

1. Examine `pipeline.yaml` to identify where the SACCR/shared-utils package is built, uploaded, or published as an artifact (the exact package name, version, path, or artifact reference).
2. Examine `ansible/main.yaml` to locate where the SACCR package is installed (e.g., via `pip install`, `requirements.txt`, or an Ansible `pip` module task).
3. Examine `requirements.txt` (inside the ansible folder or at the repo root) to check how `shared-utils` or SACCR is currently referenced.
4. Identify the mismatch causing the `cannot import` error — this is likely the package being resolved from PyPI or a wrong path instead of the pipeline-uploaded artifact.
5. Provide the exact, corrected changes needed across `pipeline.yaml`, `ansible/main.yaml`, and `requirements.txt` so that the Ansible playbook installs the specific shared-utils/SACCR artifact produced by the pipeline — using the correct artifact path, URL, or `--find-links` / `--extra-index-url` reference.

Show all file changes as diffs or clearly marked code blocks with file paths. Explain in one sentence per change why it resolves the `cannot import` error.
