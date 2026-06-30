You are a senior Python engineer. Analyze the argparse-based CLI parser in this codebase and improve my existing argument parser to match or exceed its capabilities.

**Your task has two parts:**

1. **Parse and understand the reference argparse implementation** in the specified branch — identify every argument, subcommand, flag, type coercion, default value, help string, mutually exclusive group, and any custom `Action` or `type` callables it defines.

2. **Audit my existing parser** against that reference — identify gaps, missing arguments, weak validation, missing defaults, poor help text, or structural differences — then rewrite my parser to be at feature-parity or better, following the same patterns and conventions used in the reference branch.

**Constraints:**
- Preserve any arguments my current parser has that aren't in the reference — don't remove working functionality
- Match the code style and conventions of the surrounding codebase (naming, structure, how subparsers are organized)
- Do not refactor anything outside the parser itself unless a change there is strictly required
- If the reference branch uses utility functions or shared constants to build the parser, follow that same approach rather than inlining everything

Once you've made the changes, provide a diff or clearly annotated before/after showing exactly what was added, changed, or restructured and why each change was made.
