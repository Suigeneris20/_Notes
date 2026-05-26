You are a senior DevOps engineer and Python infrastructure specialist with deep expertise in Ansible, virtualenv management, and Python dependency resolution.

I have a failing Ansible playbook in a specific repository branch. The play fails with a **"Could not find a version that satisfies the requirement..."** pip error. I need you to fix it end-to-end.

**Your task:**

1. Examine the repository and the relevant branch to understand the current playbook structure, the failing task(s), and the pip dependency definitions causing the error
2. Rewrite or patch the failing play to:
   - Create a Python 3.12 virtual environment (using `ansible.builtin.pip` with `virtualenv_python: python3.12` or the appropriate `community.general` module, whichever fits the existing codebase conventions)
   - Resolve the dependency conflict — identify the incompatible package version(s) and pin or adjust them so the install succeeds under Python 3.12
   - `pip install` all required dependencies, including the specific problem package, into that virtual environment
   - Activate the virtual environment for all subsequent plays/tasks by setting `ansible_python_interpreter` to the venv's Python binary (either as a `set_fact`, in `vars`, or via inventory — use whatever pattern is consistent with the existing playbook)
3. Ensure the fix handles idempotency (re-running the play doesn't break a working environment) and surfaces clear error messages if the venv creation or install fails

When presenting the fix, show the corrected task(s) inline with clear comments explaining what changed and why. If the root cause is a package version incompatibility, explicitly name the conflicting versions and the resolved pinning you chose.
