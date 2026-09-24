I have a React.js codebase that uses `craco.config.cjs` for its build/test configuration. I need unit tests written for this codebase using the testing setup defined in that config.

Before writing tests, inspect `craco.config.cjs` to identify the test runner and any Jest overrides, module resolution aliases, or transform settings configured there — the tests must run correctly under this exact configuration, not a generic Create React App or vanilla Jest setup.

I'll provide the source files to be tested. For each component or module:

- Follow the testing library conventions already used elsewhere in the codebase (e.g., React Testing Library, Enzyme, or whatever is present) — check existing test files first and match their patterns, imports, and file naming conventions.
- Cover the core rendering behavior, props handling, and any user interactions (clicks, form input, state changes) exposed by the component.
- Include tests for conditional rendering branches and edge cases (empty props, error states, loading states) where the component's logic has them.
- Mock external dependencies (API calls, context providers, routers) rather than letting tests hit real network or global state.
- Place each test file alongside its source file or in the existing `__tests__` directory structure, matching whatever convention the codebase already follows.

Do not restructure or refactor the source components to make them more testable unless a change is strictly required to write a valid test — flag any such case explicitly rather than making the change silently.

If `craco.config.cjs` or any source files needed to determine testing conventions are missing from what I've shared, ask me for them before proceeding.
