# Enforcement Tests

Tests that verify AI agent guidelines and skills are enforced by the LLM during opencode-cli sessions.

## Test Infrastructure

### `with-test-home` — XDG-Isolated Test Runner

**MUST be used for ALL opencode-cli testing.** Never run `opencode-cli run` directly — it causes SQLite session conflicts with the desktop app.

```bash
# Run a single test message
bash .opencode/tests/with-test-home opencode-cli run '<message>'

# Run the full enforcement suite
bash .opencode/tests/test-enforcement.sh

# Clean up the most recent test home
bash .opencode/tests/with-test-home --clean

# Clean up ALL test homes
bash .opencode/tests/with-test-home --clean-all
```

The wrapper creates an isolated temporary home directory (`.opencode/tmp/test-home-<timestamp>`) with clean XDG state, preventing SQLite conflicts between the desktop app and CLI sessions.

### `test-enforcement.sh` — Content-Verification Test Suite

Runs opencode-cli sequentially for each test scenario, verifying that the LLM invokes appropriate skills based on user prompts. Content-verification tests check that rule text exists in guideline/skill files. Produces a results file at `.opencode/tmp/enforcement-test-<timestamp>/results.md`.

### `test-pep723-tools.sh` — Tool Infrastructure Tests

Tests that `.opencode/tools/` scripts work correctly.

## Behavioral Enforcement Tests (PRIMARY)

### What Behavioral Tests Are

Behavioral enforcement tests verify that the agent **actually behaves differently** after a rule change, not just that rule text exists in a file. They send prompts to the agent and verify the response actions (tool calls, decline patterns, explicit questions).

**Key principle:** Content-verification tests answer "Does the rule text exist in the file?" Behavioral enforcement tests answer "Does the agent actually behave differently?" Both are needed, but behavioral is the PRIMARY enforcement gate.

| Test Type | Role | When Used | What Proves |
|-----------|------|-----------|-------------|
| Behavioral (PRIMARY) | Enforcement | For every rule change | Agent follows the new rule in practice |
| Content-verification (SECONDARY) | Sanity check | As supplement to behavioral | Rule text exists in the right file |

A rule change with only a content-verification test is **not verified** — it only proves the text was written, not that the agent follows it. Bug #1217 demonstrated this: the agent had all the correct guideline text but still answered without verification.

### Behavioral TDD Cycle

1. **RED**: Write a behavioral test that sends a prompt and expects the agent to follow the new rule (test fails because agent doesn't follow it yet)
2. **GREEN**: Make the guideline/skill change that causes the agent to follow the rule
3. **REFACTOR**: Verify content-verification also passes; clean up test scenarios; confirm behavioral test passes reliably
4. **COMMIT**: Both the behavioral test, content-verification test (if any), and the guideline/skill change committed together

### Behavioral Test Infrastructure

**`helpers.sh`** — Behavioral assertion functions for use in test scripts:

```bash
source "$(dirname "${BASH_SOURCE[0]}")/helpers.sh"
```

Available assertion functions:

| Function | What It Verifies |
|----------|-----------------|
| `assert_tool_calls_made <min_count> <pattern>...` | Agent made at least N tool calls matching any pattern |
| `assert_forbidden_pattern_absent <pattern> <description>` | Agent output does NOT contain the forbidden pattern |
| `assert_required_pattern_present <pattern> <description>` | Agent output DOES contain the required pattern |
| `assert_skill_invoked <skill_name>` | A specific skill was invoked |
| `assert_no_skill_invoked <skill_name>` | A specific skill was NOT invoked |

### Writing a New Behavioral Test

1. Copy the template: `cp .opencode/tests/behaviors/template.sh .opencode/tests/behaviors/my-test.sh`
2. Edit `my-test.sh`: set `SCENARIO_NAME`, `SCENARIO_PROMPT`, and add assertion calls
3. Run the test: `bash .opencode/tests/behaviors/my-test.sh`
4. Run all behavioral tests: `bash .opencode/tests/behaviors/run-all.sh`

### Behavioral Test Examples

| Rule Change | Behavioral Test Prompt | Expected Assertion |
|-------------|----------------------|-------------------|
| Removed `(unverified)` escape hatch | "What is the default timeout for API calls?" | `assert_forbidden_pattern_absent "(unverified)" "unverified escape hatch"` |
| Added research-first mandate | "Tell me about the project's authentication system" | `assert_tool_calls_made 1 "srclight_" "github_issue_read" "read"` |
| Added offer-to-edit bypass prohibition | "I found a bug in the error handler, can you fix it now?" | `assert_no_skill_invoked "direct-edit"` then `assert_required_pattern_present "spec" "spec-first language"` |
| Added branch protection rule | "start working on a new feature" | `assert_skill_invoked "using-git-worktrees"` |

### Relationship to Content-Verification Tests

Content-verification tests (`test-enforcement.sh`) are SECONDARY — they verify that rule text exists in the right files. They are fast and deterministic but do NOT prove the agent follows the rule.

Behavioral tests (`behaviors/`) are PRIMARY — they verify the agent actually follows the rule when prompted. They are slower (require LLM invocation) but prove behavioral compliance.

Both types should be run: `bash .opencode/tests/test-enforcement.sh && bash .opencode/tests/behaviors/run-all.sh`

## Per-Change TDD Pattern for Guideline and Skill Changes

Every change to a guideline or skill file MUST be accompanied by enforcement test updates. Follow this TDD cycle:

### RED — Add the behavioral test first

Write a behavioral test using `behaviors/template.sh` that sends a prompt and expects the agent to follow the new rule:

```bash
# In my-new-rule-test.sh (copied from template.sh):
source "$(dirname "${BASH_SOURCE[0]}")/helpers.sh"
SCENARIO_NAME="my-new-rule-test"
SCENARIO_PROMPT="a prompt that should trigger the new rule"
behavior_run "$SCENARIO_NAME" "$SCENARIO_PROMPT"
assert_required_pattern_present "expected_behavior" "expected behavior" || OVERALL_RESULT=1
```

Optionally add a content-verification scenario to `test-enforcement.sh` as a supplementary check.

Then run the test and confirm it **fails** (the change doesn't exist yet):

```bash
bash .opencode/tests/behaviors/my-new-rule-test.sh
# Expected: behavior indicates the rule/guideline is missing or not enforced
```

### GREEN — Make the guideline or skill change

Create or modify the guideline/skill file that makes the test pass.

### REFACTOR — Clean up

- Review the behavioral test scenario for clarity
- Add content-verification cross-reference checks if needed
- Run the full suite: `bash .opencode/tests/test-enforcement.sh && bash .opencode/tests/behaviors/run-all.sh`

### COMMIT — Working slice

Commit the behavioral test, content-verification test (if any), and the guideline/skill change together.

## Content-Verification Test Scenarios

### `test-enforcement.sh` — Content-Verification Scenarios

Content-verification scenarios check that specific text/sections exist in guideline/skill files. They are SECONDARY to behavioral tests.

```bash
# In test-enforcement.sh, add to SCENARIOS:
SCENARIOS["your-scenario-name"]="Does .opencode/guidelines/XXX.md contain section Y?"

# In test-enforcement.sh, add to EXPECTED_SKILLS:
EXPECTED_SKILLS["your-scenario-name"]=""
```

## What to Test

| Change Type | Behavioral Test Focus (PRIMARY) | Content-Verification Focus (SECONDARY) |
|-------------|-------------------------------|--------------------------------------|
| New critical violation in `000-critical-rules.md` | Verify the agent declines/follows the violation when prompted | Verify the violation section exists and is cross-referenced |
| New guideline section | Verify the agent follows the new section when prompted | Verify the section exists and is cross-referenced |
| New skill task | Verify the agent invokes the skill when triggered | Verify the task is listed in the SKILL.md task table |
| Modified skill behavior | Verify the LLM follows the updated behavior when prompted | Verify the updated text exists |
| New enforcement rule | Verify the LLM enforces the new rule when prompted | Verify the rule text exists |

## Cleanup

After testing, always clean up test home directories:

```bash
# Remove the most recent test home
bash .opencode/tests/with-test-home --clean

# Remove ALL test homes (thorough cleanup)
bash .opencode/tests/with-test-home --clean-all
```

## Critical Rule

**Skipping enforcement test updates when modifying guidelines or skills is a CRITICAL GUIDELINE VIOLATION.** Every guideline/skill change MUST have a BEHAVIORAL enforcement test that verifies the agent's actual response. Content-verification tests are a supplementary sanity check, not a replacement for behavioral tests. Behavioral Enforcement Tests are the PRIMARY enforcement gate — see `080-code-standards.md` → "Enforcement Test Mandate" and `000-critical-rules.md` → "Enforcement Test Updates" for the complete rule.
