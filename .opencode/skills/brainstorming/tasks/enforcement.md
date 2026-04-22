# Task: enforcement

Enforcement rules and messages for the brainstorming skill. Ensures brainstorming is not skipped before spec creation.

## What Skills MUST Check

1. **Before spec creation:**

   - Has exploration been invoked?
   - Is exploration output present?
   - Has problem understanding been explored?

2. **Enforcement matrix (expanded with protocol-compliance):**

   | State | Check | Action |
   | -- | -- | -- |
   | Exploration NOT invoked | Skill not loaded | INVOKE brainstorming |
   | Exploration invoked, no turns | Skill loaded but no interactive Q&A turns recorded | HALT — require at least one Q&A exchange |
   | Exploration invoked, batch-dump detected | Agent produced findings without developer interaction | HALT — require developer confirmation of each item |
   | Exploration invoked, partial protocol | Agent asked one question then ignored the answer | HALT — require per-item developer confirmation before proceeding |
   | Exploration invoked, protocol followed | Interactive Q&A with developer confirmation for key items | PROCEED to spec creation |

3. **What does NOT bypass exploration:**

   - "skip brainstorming" → NOT allowed
   - "I already know what I want" → Still require brief exploration (problem understanding at minimum)
   - User impatience → Document partial exploration, ask to proceed

## Batch-Dump Detection Heuristics

Define verifiable signals that the agent skipped the conversational protocol:

| Signal | Detection | Classification |
| -- | -- | -- |
| Multiple findings in one message | Agent produced >1 discovery per message without interleaving developer responses | batch-dump |
| No developer response between findings | Agent output has consecutive findings with no developer message between them | batch-dump |
| Dimensions exposed as structured output | "Dimensions Explored" or numbered dimension list in output | protocol violation (dimensions are internal-only per `explore.md`) |
| Pre-determined question list | Questions do not reference or build on prior developer answers | protocol violation |
| Single question then ignored answer | Agent asked one question but proceeded with a pre-determined path regardless of the answer | partial protocol application |

**Detection rule:** If the exploration record contains two or more consecutive agent messages (findings, conclusions, or design proposals) without an intervening developer response, the enforcement gate MUST classify this as batch-dump and HALT.

## Enforcement Messages

**Missing exploration:**

```
Exploration required before spec creation.

This ensures thorough requirements investigation before planning.

To invoke: Say '/skill brainstorming' or describe your feature to start exploration.
```

**Incomplete exploration:**

```
Exploration incomplete. Problem understanding must be explored at minimum.

Please complete exploration before proceeding to spec creation.
```

**Batch-dump detected (protocol violation):**

```
Protocol violation: Exploration produced findings without interactive discussion.

The brainstorming skill requires one-question-at-a-time interactive Q&A with the
developer. Batch-dumping findings without developer input violates the exploration
protocol.

Required: Re-engage the developer with one question at a time, and obtain
confirmation for each significant discovery before including it in the spec.
```

**Partial protocol application:**

```
Protocol violation: Exploration asked questions but did not follow the
developer's answers.

The brainstorming skill requires that each question builds on the developer's
prior response. Asking one question then proceeding with a pre-determined
list regardless of the answer violates the exploration protocol.

Required: Restart the Q&A cycle, letting each question follow from the
developer's actual answer.
```

## Investigation Completion Criteria

Before creating a spec, investigation MUST be complete. This is a hard gate, not optional.

| Requirement | Evidence |
| -- | -- |
| Problem understood | Clearly stated problem, context, stakeholders |
| Codebase explored | Existing patterns, reusable components identified |
| Alternatives considered | At least 2 approaches for significant decisions |
| Risks identified | Risk assessment with mitigation strategies |
| Success criteria defined | Testable, measurable completion criteria |
| Protocol compliance verified | Interactive Q&A turns documented; no batch-dump; each significant finding has developer confirmation |
| No batch-dump patterns | No consecutive agent messages without interleaving developer responses in the exploration record |
| Dimensions kept internal | No "Dimensions Explored" or structured dimension output in exploration artifacts |

### Permissible Investigation Activities

| Activity | Allowed? | Notes |
| -- | -- | -- |
| Read production code | YES | Read-only exploration |
| Read production data | YES | Read-only analysis |
| Create test scripts in `./tmp/` | YES | Isolated from production |
| Run test scripts in `./tmp/` | YES | No production impact |
| Run static analysis | YES | Code verification |
| Modify production code | NO | Requires approved spec |
| Modify production data | NO | Requires approved spec |
| Run code against production DB | NO | Requires explicit user authorization |

## Adversarial Verification of Process Flags (MANDATORY)

**🚫 CRITICAL: STATUS markers and process-completion flags MUST be verified against actual state, not trusted from claims in issue comments or chat. This extends `065-verification-honesty.md` to brainstorming process flags.**

### Verification Table

| Process Flag | Verification Action | Tool Call | Problem Class |
|-------------|-------------------|-----------|---------------|
| "Exploration complete" | Verify all investigation checklist items have evidence artifacts (not just assertions) | Check that tool-call artifacts exist for each of the 6 checklist items | VERIFICATION-GAP |
| "Code inspection done" | Verify actual tool calls were made for call paths, imports, dead code, formats, layers, alternatives | `srclight_get_callers`, `srclight_get_symbol`, etc. — confirm in artifacts | MISSING-ELEMENT |
| "Problem understood" | Verify a clear problem statement exists in the spec or exploration notes | `github_issue_read(method=get, issue_number=N)` → check body for problem section | STRUCTURE-VIOLATION |
| "Alternatives considered" | Verify at least 2 approaches were documented for significant decisions | `github_issue_read(method=get, issue_number=N)` → check for approach comparison | MISSING-ELEMENT |
| "Risks identified" | Verify risk assessment with mitigation is documented | `github_issue_read(method=get, issue_number=N)` → check for risk section | MISSING-ELEMENT |
| "User approved design" | Verify approval comment exists from a developer (not bot/agent) on the issue | `github_issue_read(method=get_comments)` → filter by author_association | CONFLICTING |
| "STATUS marker value" | Compare claimed STATUS against actual issue content maturity | `github_issue_read(method=get)` → parse STATUS from body | STRUCTURE-VIOLATION |
| "Protocol compliance verified" | Verify exploration involved interactive Q&A (not batch-dump); check for consecutive agent-only messages | Chat/exploration record review — confirm developer responses interleave agent messages | CONFLICTING |
| "Developer confirmed findings" | Verify each significant discovery has a developer acknowledgment before being included | Chat/exploration record review — confirm per-item confirmation | VERIFICATION-GAP |
| "Min interactive turns met" | Verify at least 2 Q&A exchanges occurred before proceeding to approaches | Chat/exploration record review — count developer-agent exchanges | VERIFICATION-GAP |

### Evidence Artifacts

Every process-flag verification MUST produce an evidence artifact — a tool call result demonstrating the verification was performed. Assertions without artifacts are VERIFICATION-GAP findings.

**Evidence format:**

```
Check: [what was verified]
Tool: [tool call and parameters]
Result: [actual state found]
Classification: [STRUCTURE-VIOLATION|MISSING-ELEMENT|CONFLICTING|VERIFICATION-GAP|MISSING-TRACEABILITY]
Action: [auto-fix|conditional|flag-for-review]
```

### Classification on Failure

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Checklist items claimed without tool-call evidence | VERIFICATION-GAP | conditional | Complete the tool calls before proceeding |
| Problem statement missing from issue | STRUCTURE-VIOLATION | auto-fix | Add problem statement to issue body |
| No alternatives documented for significant decision | MISSING-ELEMENT | conditional | Document alternatives before proceeding |
| Approval from non-developer (bot/agent) | CONFLICTING | flag-for-review | HALT — requires real developer authorization |
| STATUS marker claims maturity but content is incomplete | STRUCTURE-VIOLATION | auto-fix | Update STATUS to reflect actual maturity |
| Consecutive agent messages without developer response | CONFLICTING | flag-for-review | HALT — batch-dump detected, re-engage developer interactively |
| Significant findings lack developer confirmation | VERIFICATION-GAP | conditional | Re-present each finding for developer confirmation before proceeding |
| Fewer than 2 Q&A exchanges before proceeding | VERIFICATION-GAP | conditional | Continue Q&A until minimum turns met |

**These verifications are MANDATORY before transitioning out of brainstorming. Skipping them is a CRITICAL GUIDELINE VIOLATION.**
