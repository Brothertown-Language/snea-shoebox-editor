# Task: report

## Purpose

Report findings from plan fidelity comparison. All findings are reported, NOT auto-applied. This replaces the v1 `auto-fix` task.

## Key v2 Change

Previous version (`auto-fix`) would apply simple discrepancies automatically. This version (`report`) presents all findings to the agent for decision-making.

**Why report-only:**
- Auto-fixes ignore context
- A missing file reference might not need adding (context determines relevance)
- A different approach might be intentional
- The agent has full context; the auditor doesn't

## Procedure

1. **Receive comparison results** from the `compare` task
2. **Classify each finding** by severity and type
3. **For significant gaps**, check if brainstorming should be recommended
4. **Format all findings** using the standard report format
5. **Report findings** to chat (NOT as GitHub Issue comment)
6. **Create audit log** in `./tmp/audit-fidelity-YYYYMMDD.md`

## Finding Format

```
Finding: [MISSING_PHASE|EXTRA_PHASE|MISSING_STEP|EXTRA_STEP|APPROACH_DIFFERENCE|MISSING_EDGE_CASE|MISSING_FILE_REF|ORDERING_DIFFERENCE|SCOPE_EXPANSION|VAGUE_PROBLEM] - [summary]
Location: [phase/step where found]
Context: [why this matters for implementation fidelity]
Recommendation: [add step/phase OR investigate approach OR trigger brainstorming]
Severity: [HIGH|MEDIUM|LOW]
```

## Brainstorming Recommendation

When significant gaps are found (3+ HIGH-severity findings or any VAGUE_PROBLEM finding):

- Recommend `/skill brainstorming` for the specific area of uncertainty
- This is a v2 improvement: instead of just flagging, actively recommend deeper exploration
- The agent decides whether to follow the recommendation

## GitHub Comment Format

```
## Plan Fidelity Audit

**Summary:** [1-2 sentences describing findings and impact]

**Outcome:** [What the agent should decide based on findings]

### Findings

- [Finding 1 — severity]
- [Finding 2 — severity]

### Recommendations

- [Specific recommendations for action]

---

🤖 <AgentName> (<ModelId>) 📝 updated
```

## Audit Log Requirement

After the audit session, create `./tmp/audit-fidelity-YYYYMMDD.md` with all findings and retain in `./tmp/` for session reference. Do NOT post as GitHub Issue comment — audit findings are internal agent guidance.

Co-authored with AI: <AgentName> (<ModelId>)

## Live Verification: Report Finding Claims (MANDATORY)

**Each reported finding MUST be verified against actual source content. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Finding references correct phase" | Verify the phase exists in the Plan issue | `github_issue_read(method=get)` → search for phase name | MISSING-TRACEABILITY |
| "Severity is accurate" | Verify severity matches finding impact | Re-assess finding against spec/plan content | STRUCTURE-VIOLATION |
| "Recommendation is actionable" | Verify recommendation targets actual finding | Compare recommendation with finding description | CONFLICTING |
| "Audit log was created" | Verify audit log file exists | `glob(pattern="./tmp/audit-fidelity-*.md")` | MISSING-ELEMENT |

**Evidence artifact:** Tool call results or file existence checks confirming each claim.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Phase referenced but not found in Plan | MISSING-TRACEABILITY | flag-for-review | Verify phase name, may be renamed |
| Severity mismatched with actual impact | STRUCTURE-VIOLATION | auto-fix | Update severity to match impact |
| Audit log not created | MISSING-ELEMENT | auto-fix | Create audit log now |
| Finding claim without evidence | VERIFICATION-GAP | conditional | Re-verify with tool calls |