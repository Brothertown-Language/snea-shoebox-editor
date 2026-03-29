# GitHub Workflow: Issue-First Strategy

## The "Issue-First" Strategy

### 1. GitHub Issues as Authority
When GitHub MCP tools are available, **GitHub Issues** are the authoritative source for spec tracking.

- **Primary Mechanism**: Issues with Sub-issues (Task Lists) for hierarchy
- **Status Tracking**: STATUS field in issue body (e.g., `STATUS: 1.2`)
- **Hierarchy**: Parent `[SPEC]` issues linked to child `[Task]` issues via sub-issues

**Note**: GitHub Projects V2 boards can optionally be created via GitHub UI for visualization, but are NOT required for the workflow. MCP tools do not support Project V2 creation.

### 2. Spec Tracking: GitHub Issues & Sub-Issues
**GitHub Issues are the authoritative tracking mechanism.**

- **Parent Spec Issue**: Represents the complete specification (e.g., `[SPEC] Feature Name`).
- **Child Task Issues**: Each implementation phase or complex task MUST be its own issue, linked to the parent via **GitHub Task Lists (Sub-issues)**.
- **⚠️ MANDATORY SUB-ISSUES**: All implementation tasks MUST be their own GitHub Issues, linked via `github_sub_issue_write method=add`. Inline markdown checklists (e.g., `- [ ] Task description`) in the parent issue body are **PROHIBITED** for task tracking — each task MUST be a separate issue.

**See `.opencode/skills/github-sub-issues/SKILL.md` for complete workflow including:**
- Single-task vs multi-task exemption
- Auto-create workflow
- Database ID requirement
- Phase-level vs step-level structure

- **Archive**: When complete, close the GitHub Issue. No archive file is needed — GitHub Issues persist history.

---

## ⚠️ MUST-APPROVE: New Specs Require Approval

**When creating a new spec issue:**
1. **ALWAYS apply `needs-approval` label** to the issue
2. **SILENTLY HALT** and wait for explicit `"approved"`, `"go"`, or `"approved: N.M"` from the developer. Do NOT prompt for this.
3. **DO NOT implement** until the `needs-approval` label is removed or overridden by explicit authorization.

**Before implementing any phase:**
1. Check that the spec issue does NOT have `needs-approval` label
2. If `needs-approval` is present, SILENTLY HALT and wait for authorization.
3. Only proceed after developer says `"approved"` or `"go"`

**Exception**: `revise` commands allow the agent to **post comments** explaining spec changes. Comments preserve history, issue body edits destroy it. If structural changes are needed (new phases, reordered steps), post a comment describing the change — do NOT edit the issue body except for STATUS fields. `revise` NEVER authorizes code changes.

---

## 3. Issue Structure for Issue-First

### Title Format (Mandatory Hierarchy)
To ensure clear hierarchy in flat list views:
- `[SPEC] Feature Name` — Primary specification.
- `[SPEC-FIX] Bug Description` — Bug fix for existing functionality.
- `[Task: SPEC-name] Task description` — Implementation task belonging to a specific spec.
- `[Task: #123] Descriptive title` — Task belonging to a parent issue #123. Title must describe WHAT is being done, not just phase type.

### ⚠️ TASK TRACKING REQUIREMENT
Every implementation task MUST be:
1. A **separate GitHub Issue** (not inline checklist in parent)
2. Linked to parent via `github_sub_issue_write method=add`
3. Using **database ID** for `sub_issue_id` (NOT issue number)

---

## 4. Status Updates & Labels
- **Status Updates**: Add comments to track progress: "☑ Task #123 complete".
- **Labels**:
    - `enhancement`, `bug`, `refactor` — Category
    - `needs-approval` — Awaiting developer authorization (Agent must HALT without prompting)
    - `in-progress` — Currently implementing
    - `blocked` — Waiting on external factors

---

## 5. Progress Comments (MANDATORY)

**Every implementation step MUST be documented with a comment on the associated issue.**

**See `.opencode/skills/github-comments/SKILL.md` for complete progress comment requirements.**

### Quick Reference

**Post progress comments after EACH task completion:**
- Executive summary describing impact and stakeholder value
- NO file lists (redundant with git)
- NO "Next" field (dialog prompts prohibited)

**Post progress comments after ANY file change:**
- Brief narrative describing impact
- Focus on why the change matters

### Executive Summary Format

**Intermediate task (multi-task spec):**
```
AI: <AgentName> <ModelID> ✅ Task Complete: <task-name>

**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>
```

**Final task or single-task spec:**
```
AI: <AgentName> <ModelID> ✅ Task Complete: <task-name>

**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

All tasks complete from this specification.
```

**⚠️ FAILURE TO POST PROGRESS COMMENTS IS A CRITICAL GUIDELINE VIOLATION.**

---

## 5.5. Assignee Requirement (MANDATORY)

**All issues created or managed by AI agents MUST have assignees.**

### Requirements

1. **New issues**: Assign the requesting user (from session init `GIT_USER_NAME`/`GIT_USER_EMAIL`)
2. **Spec issues**: Assign the spec author and relevant stakeholders
3. **Bug reports**: Assign the code area owner or project maintainer
4. **If unclear who to assign**: Use the default from session init or project maintainer

### Rationale

Assignees ensure:
- Stakeholders receive notifications
- Clear ownership for follow-up
- Issues don't become orphaned

### Implementation

When using `github_issue_write method="create"`:
```python
github_issue_write(
    method="create",
    owner=owner,
    repo=repo,
    title="Issue Title",
    body="Issue body",
    assignees=["username"]  # REQUIRED - never empty
)
```

**⚠️ FAILURE TO ASSIGN ISSUES IS A CRITICAL GUIDELINE VIOLATION.**

---

## 6. Responding to Issue Comments (MANDATORY)

**When a user comments on an issue, ALWAYS respond via GitHub issue comment - NOT just internal analysis.**

Users communicating via GitHub Issues are:
- Not in your local context - they can't see your internal reasoning
- Expecting a reply where they asked the question
- Not mind readers - they need explicit responses

### Required Actions

1. **Read the comment** via `github_issue_read method=get_comments`
2. **Respond publicly** via `github_add_issue_comment`
3. **Conversational, not bureaucratic**:
   - Answer questions directly
   - State findings clearly
   - Ask for authorization simply: "Ready when you are" or just ask the question
   - **NEVER** use phrases like "Awaiting authorization to implement"

### Example

```
User asks in issue #203: "how do these keys seem?"

BAD: "Awaiting authorization to implement."

GOOD: "The keys look correct. Ready when you are."
```

**⚠️ NEVER analyze issue comments silently without posting a response.**

---