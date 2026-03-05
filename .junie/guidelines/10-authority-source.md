# Guideline 10: Code as Authoritative Source

## Principle

The current state of the filesystem (the code) is the only absolute source of truth. Documentation, plans, and session
history are secondary and potentially transient or outdated.

## Rules

1. **Code Priority**: If a discrepancy is found between the code (including filenames, structure, and logic) and any
   non-code source (plans, docs, user prompts referencing old states), the **code wins**.
2. **Documentation Drift Protocol**:
    * When drift is detected, you MUST NOT "fix" the code to match the documentation or plan.
   * Instead, you MUST update the plan/documentation to reflect the reality of the code. Updating files in `plans/`
     to reflect code reality is exempt from the approval gate (treated as a synchronization administrative action).
     Updates to documentation outside `plans/` require the standard approval gate.
    * After syncing the documentation, STOP and report the synchronization.
3. **Suppression of Reactive Remediation**:
    * Explicitly forbidden: Proposing or applying code changes solely to make the code conform to an expectation derived
      from a non-code source.
    * Remediation must only be driven by technical bugs, explicit architectural requests, or approved feature additions,
      never by documentation drift.
4. **Verification First**: Before using a filename or symbol from a plan or document in a tool call, command, or code
   edit, verify its existence using the appropriate tool (`ls`, `search_project`, etc.). If it does not exist, trigger
   the Drift Protocol. This does not apply when merely discussing or quoting a filename from a document.
