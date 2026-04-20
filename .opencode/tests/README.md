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

### `test-enforcement.sh` — Full Enforcement Test Suite

Runs opencode-cli sequentially for each test scenario, verifying that the LLM invokes appropriate skills based on user prompts. Produces a results file at `.opencode/tmp/enforcement-test-<timestamp>/results.md`.

### `test-pep723-tools.sh` — Tool Infrastructure Tests

Tests that `.opencode/tools/` scripts work correctly.

## Per-Change TDD Pattern for Guideline and Skill Changes

Every change to a guideline or skill file MUST be accompanied by an enforcement test scenario. Follow this TDD cycle:

### RED — Add the test first

Add a new scenario to the `SCENARIOS` and `EXPECTED_SKILLS` associative arrays in `test-enforcement.sh`:

```bash
# In test-enforcement.sh, add to SCENARIOS:
SCENARIOS["your-scenario-name"]="a prompt message that should trigger the skill/guideline"

# In test-enforcement.sh, add to EXPECTED_SKILLS:
EXPECTED_SKILLS["your-scenario-name"]="expected-skill-name"
# Use empty string "" if no specific skill invocation is expected
```

Then run the test and confirm it **fails** (the change doesn't exist yet):

```bash
bash .opencode/tests/with-test-home opencode-cli run '<your test message>'
# Expected: behavior indicates the rule/guideline is missing or not enforced
```

### GREEN — Make the guideline or skill change

Create or modify the guideline/skill file that makes the test pass.

### REFACTOR — Clean up

- Review the test scenario for clarity
- Add cross-reference checks if needed
- Run the full suite: `bash .opencode/tests/test-enforcement.sh`

### COMMIT — Working slice

Commit both the test addition and the guideline/skill change together.

## Test Scenario Template

When adding a new enforcement test scenario for a guideline or skill change, use this pattern:

```bash
# 1. Scenario name: descriptive-kebab-case
# 2. Prompt message: natural language that should trigger the rule/skill
# 3. Expected skill: the skill that should be invoked, or "" for no specific skill

# Example: enforcing item decomposition in plans
SCENARIOS["plan-item-decomposition"]="create a plan for adding user authentication without decomposing it into items"
EXPECTED_SKILLS["plan-item-decomposition"]="writing-plans"

# Example: enforcing enforcement test mandate
SCENARIOS["enforcement-test-mandate"]="update the skill-creator skill without adding an enforcement test"
EXPECTED_SKILLS["enforcement-test-mandate"]="skill-creator"
```

## What to Test

| Change Type | Test Scenario Focus |
|-------------|-------------------|
| New critical violation in `000-critical-rules.md` | Verify the violation is referenced and the LLM recognizes it |
| New guideline section | Verify the section exists and is cross-referenced |
| New skill task | Verify the task is listed in the SKILL.md task table |
| Modified skill behavior | Verify the LLM follows the updated behavior |
| New enforcement rule | Verify the LLM enforces the new rule when prompted |

## Cleanup

After testing, always clean up test home directories:

```bash
# Remove the most recent test home
bash .opencode/tests/with-test-home --clean

# Remove ALL test homes (thorough cleanup)
bash .opencode/tests/with-test-home --clean-all
```

## Critical Rule

**Skipping enforcement test updates when modifying guidelines or skills is a CRITICAL GUIDELINE VIOLATION.** See `080-code-standards.md` → "Enforcement Test Mandate" and `000-critical-rules.md` → "Enforcement Test Updates" for the complete rule.
