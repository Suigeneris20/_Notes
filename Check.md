# Prompt for AI Agent: Targeted Unit Test Generation & Validation

## Task Overview
You have access to two branches: `<MAIN_BRANCH>` (the original code) and `<CHECKMARX_BRANCH>` (which contains fixes for Checkmarx vulnerabilities, specifically involving path modifications). Your goal is to write targeted unit tests for the original code and use them to verify that the Checkmarx fixes resolve the vulnerabilities without altering the application's core behavior.

## Execution Steps

1. **Analyze the Diff:**
   Compare `<MAIN_BRANCH>` to `<CHECKMARX_BRANCH>` to identify the exact code lines, functions, and logic that were modified to fix the Checkmarx path traversal issues.

2. **Establish the Test Branch:**
   Create a new branch starting from the exact same revision as `<MAIN_BRANCH>` before the Checkmarx changes were applied.

3. **Generate Targeted Tests:**
   Write robust unit tests specifically covering the unmodified code lines and functions identified in step 1.

4. **Implement Real Path Configurations:**
   When building these tests, ensure that paths and parameters are not fully mocked. You must use the original configurations to construct paths exactly as they operate in PROD and UAT modes.

5. **Capture the Baseline:**
   Run these new unit tests against the original codebase (`<MAIN_BRANCH>`) and capture the results to ensure they successfully pass and establish a behavioral baseline.

6. **Validate the Security Fixes:**
   Apply the Checkmarx changes (or merge `<CHECKMARX_BRANCH>` into the test branch) and run the identical unit tests again. Confirm that all tests still pass, proving the security fixes retain the exact functionality of the original branch.
   
