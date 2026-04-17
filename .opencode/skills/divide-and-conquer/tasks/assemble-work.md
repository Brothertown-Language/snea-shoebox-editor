# Task: assemble-work

Migrated from `implementation-workflow` task work-orchestrate.

## Purpose

Orchestrate work execution by dispatching sub-agents for each approved issue, using branch-per-issue with merge-based dependency resolution. This task makes the main agent a pure orchestrator that never edits implementation files directly.

## Entry Criteria

- Approval-gate has verified authorization for one or more issues
- `pre-implementation-analysis` has expanded sub-issues and produced the flat item list
- Worktree is created and ready

## Exit Criteria

- All issues in the work set have been implemented via sub-agents in separate branches
- Each sub-agent ran verification + finishing before returning
- All feature branches squash-merged into a single work branch
- Compare URL generated, executive summary in chat
- HALT after review-prep (no PR creation without explicit instruction)

## Procedure

### Step 1: Verify Gate Evidence Audit and Determine Execution Order

**🚫 CRITICAL PREREQUISITE: Before determining execution order, verify the Gate Evidence Audit Table exists in the work state file (`.opencode/tmp/work-*.md`).**

- Read the work state file from `pre-implementation-analysis` (`.opencode/tmp/work-*.md`)
- **If the Gate Evidence Audit Table is missing** AND any issues were classified as "already-implemented" during screening: HALT and return to `pre-implementation-analysis` Step 0.5 to complete the audit. The table is a mandatory structural artifact — its absence means Gate 1 and Gate 2 evidence was not verified.
- **If the Gate Evidence Audit Table exists** AND has ❌ entries for any issue: those issues were already downgraded during pre-implementation-analysis. Verify the downgraded classifications are reflected in the execution plan. If not, return to `pre-implementation-analysis`.
- **If NO issues were classified as "already-implemented":** The Gate Evidence Audit Table is not required. Proceed normally.

- For multi-issue: use dependency order from `pre-implementation-analysis`
- For single issue: treat as work-of-1 — no special casing, no shortcuts
- Determine complexity level for each issue (simple/moderate/complex)

**Work-of-1.** There is no separate code path. The `assemble-work` task handles single-issue dispatch as the default. This eliminates forked execution paths.

### Step 2: Create Feature Branches and Worktrees

For each issue in the work set:

1. Create a worktree with feature branch using `using-git-worktrees --task create-worktree`
2. `BASE_BRANCH` defaults to `dev` for the first/only issue in the work set
3. For dependent issues: `BASE_BRANCH` is set to the prior issue's feature branch (the merged branch, not the work branch)
4. Record each issue's branch name and worktree path

### Step 3: Execute Issues in Dependency Order

For each issue in execution order:

**Checkpoint (MANDATORY):** Before dispatching the next sub-agent, verify NO `question` tool calls have been made. If any were made, remove them and proceed autonomously. Structural decisions (single-task vs multi-task, execution order, scope sizing) are agent intelligence concerns that the agent must resolve autonomously.

1. **Before sub-agent dispatch**, if this issue depends on a prior issue:

   - Merge the prior issue's feature branch into this issue's feature branch:
     ```bash
     git merge <prior-issue-branch> -m "Merge <prior-issue-branch> into <current-branch> — dependency chain (#<prior>, #<current>)"
     ```
   - If merge produces conflicts:
     - Tiers 1-2 (trivial/formatting): Auto-resolve per `conflict-resolution` skill
     - Tier 3 (intent conflict): HALT and flag for developer review

   2. **Build dispatch context** with AI-composed intent-and-context metadata and phase progress:

     Sub-issues contain phase context in their body (enriched during creation via `create-sub-issue`). When composing dispatch context, reference the sub-issue body for phase-specific context rather than re-reading the Plan body. The sub-issue body should already include: why the phase exists, what it must accomplish, how to verify completion, edge cases, and dependencies. If the sub-issue body is insufficient (only contains `**Parent Plan:** #M`), fall back to reading the Plan body for the relevant phase section.

     **Phase progress composition:** Before each sub-agent dispatch, compose the `phase_progress` section from:
     - The Plan STATUS marker (which phases are marked complete) — read from the plan issue body or sub-issue STATUS markers
     - Prior sub-agent results — the `completed_phases`, `concern_boundaries_crossed`, and `verification_evidence` fields returned by preceding sub-agents
     - The orchestrator's own judgment about concern boundaries — when a new sub-agent's work crosses into a different architectural concern (e.g., from data layer to UI layer, from orchestration to enforcement), name the transition in `concern_boundaries_crossed`

     Phase progress is prose-driven: state what information must travel, trust the orchestrator to decide how to encode it. Completed phases should be named by the concern they address (e.g., "dispatch context schema" rather than "Phase 1"), concern boundaries should describe the architectural transition point, and verification evidence should summarize what was confirmed.

     ```yaml
      work_set:
        authorized_issues: [#A, #B, #C]
        completed_issues: [<completed>]
     issue: #<current>
     sub_issue_body: "<phase prose from sub-issue body, not just parent reference>"
     spec: "<full spec body from GitHub Issue>"
     authorization: "User approved #A, #B, #C on <date>"
      prior_context: "<AI-composed intent and context from prior issues>"
      decision_log_reference: "<URL or reference to the Decision Log on the Plan issue — the sub-agent can retrieve full decision history from this reference>"
      phase_progress:
       completed_phases: "<prose listing of completed phases by concern name, accumulated from prior sub-agent results and Plan STATUS>"
       concern_boundaries_crossed: "<prose description of architectural concern transitions between the prior sub-agent's work and this sub-agent's work>"
       verification_evidence: "<prose summary of what was verified in prior phases and the outcomes>"
     dependency_branches: ["spec/<prior-branch>"]
     env_vars:
         worktree.path: ".worktrees/spec-<name>"
         branch: "spec/<name>"
        github.owner: "<from-session>"
        github.repo: "<from-session>"
        dev.name: "<from-session>"
        dev.email: "<from-session>"
     ```

3. **Spawn sub-agent** via `task(subagent_type="general", prompt=...)`

4. **Sub-agent responsibilities:**

   - Load spec + session context + prior context
   - Run `divide-and-conquer` skill for the specific issue
   - Make WIP commits as needed
   - Run `verification-before-completion --task verify`
   - Run `finishing-a-development-branch --task checklist`
   - Return structured result: `{status, files_changed, summary}`

 5. **Collect result** from sub-agent

  6. **Sub-Agent Completion Checkpoint** — after collecting each result, perform the completion checkpoint per `dispatch` task Step 4:

     - If sub-agent returned a structured result: check `status` field and handle accordingly
     - If sub-agent returned **NO result** (timeout, crash, empty): this is **ABNORMAL TERMINATION**
       - Run `git status` in the worktree
       - Clean tree → didn't start → re-dispatch
       - Uncommitted changes + all deliverables → UNDO + re-dispatch by default; manual commit+push only if narrow exception applies (≤50 lines, single file, fully correct, no remaining dispatches — see SKILL.md Recovery Mode)
       - Uncommitted changes + partial deliverables → `git checkout .` + re-dispatch reduced scope
       - Uncommitted changes + wrong changes → `git checkout .` + re-dispatch full scope
     - Report abnormal termination to chat (see format in SKILL.md "Sub-Agent Completion Checkpoint")
     - The orchestrator decides recovery action autonomously per "Pushing Agent Intelligence Decisions to the User" (`000-critical-rules.md`)
     - **Do NOT proceed to the next sub-agent until abnormal termination recovery is complete.** Recovery must fully resolve (re-dispatch succeeded or manual commit+push verified) before advancing.

 7. **Compose prior_context and phase_progress** for the next issue based on what was implemented:

     prior_context (intent and context):
     - Design decisions made
     - Edge cases handled
     - Assumptions that later issues depend on
     - Interfaces exposed that later issues should use
     - NOT a change summary (that's in git) — intent and context only

     phase_progress (accumulated from sub-agent result + Plan STATUS):
     - completed_phases: append the just-completed phase concern name to the running list
     - concern_boundaries_crossed: if the next issue's concern differs from the just-completed issue's concern, note the transition
     - verification_evidence: append what was verified and the outcome

     Both prior_context and phase_progress are prose-driven. The orchestrator composes them intelligently — no fixed template, no rigid schema.

 8. **Append the sub-agent's decision_log_entry to the Decision Log on the Plan issue.** After collecting each sub-agent's result, post their `decision_log_entry` as a dedicated GitHub Issue comment on the Plan issue. The Decision Log persists design decisions across phase boundaries and session restarts.

   **Decision Log storage:** Use a dedicated GitHub Issue comment on the Plan issue, NOT the Plan body. Rationale:
   - Append-only — new decisions are added without editing existing content
   - Lightweight — appending a comment doesn't require re-editing the entire Plan body
   - Survives session restarts — comments persist on the GitHub Issue independently of any agent session
   - Doesn't bloat the Plan body — the Plan body stays focused on phase structure and STATUS markers
   - Sequential — comments are naturally ordered chronologically

   The orchestrator posts the decision log entry after each sub-agent returns. If posting fails, log the failure and continue — the Decision Log is a durability enhancement, not a blocking gate. The `decision_log_entry` is also returned in the sub-agent result for immediate use by subsequent dispatches within the same session.

 9. **Mark prior issue's branch as frozen** — no rebasing, amending, or force-pushing

 10. **Handle failures:**

   - If sub-agent fails: record failure
   - For independent issues: continue to next issue
   - For must-precede chains: skip dependent issues, report both

### Step 4: Work Assembly

After ALL issues in the work set complete:

1. **Create a work branch** (name chosen by agent at creation time, e.g., `work/<short-name>` or `spec/<short-name>`):

   ```bash
   git checkout dev
   git checkout -b <work-branch-name>
   ```

2. **Squash-merge each feature branch** into the work branch, one commit per issue:

   ```bash
   git merge --squash spec/issue-a
   git commit -m "Implement #A: <description>"

   git merge --squash spec/issue-b
   git commit -m "Implement #B: <description> (#A dependency)"
   ```

3. **Commit message format:**

   - MUST include issue number for GitHub auto-linking
   - Dependents reference their dependencies
   - Example: `Implement #703: add reprocessing logic (#698 dependency)`

### Step 5: Post-Work Review-Prep

1. **Verify all results** — check git log for all expected commits
2. **Run git-workflow --task review-prep** for the work branch
3. **Collect compare URL**

### Step 5.5: Pre-PR Checklist (MANDATORY before any PR creation)

Before creating ANY pull request, verify:

1. Work state file exists at `.opencode/tmp/work-*.md`
2. All feature branches listed in work state have been squash-merged into the work branch
3. The work branch has exactly one squash-merge commit per issue
4. Working tree is clean (no uncommitted changes)

If any check fails:

- If work state file missing → the agent skipped pre-implementation-analysis; HALT
- If squash-merges missing → complete Step 4 (Work Assembly) first
- If working tree dirty → commit or stash changes first

**🚫 CRITICAL: Individual PR creation for work-approved issues is FORBIDDEN. All issues in a work set MUST be squash-merged into a single work branch, then ONE PR created from that branch.**

### Step 6: Report and HALT

**Chat output:**

```markdown
**Summary:**

Implemented <N> issues via branch-per-issue work orchestration.

**Outcome:**

- #A: <summary> ✅
- #B: <summary> ✅
- #C: <summary> ⚠️ (partial — see details)

Compare URL: https://github.com/<owner>/<repo>/compare/dev...<work-branch>

**If a PR has been created for this work set, use "PR URL" label with the `pull/<N>` format instead of "Compare URL":**

```
PR URL: https://github.com/<owner>/<repo>/pull/<PR-number>
```

**NEVER use the wrong label for the wrong URL format.** Label-format mismatch (e.g., "Compare URL" with `pull/N` URL, or "PR URL" with `compare/dev...` URL) is a critical violation.

🤖 <AgentName> (<ModelId>) <status>
```

**Chat Output Format Verification (MANDATORY — Zero Tolerance)**

Before sending the chat report, verify ALL elements are present and correctly ordered:

- [ ] Executive summary present as **first** element (before any URL)
- [ ] Outcome line present after summary
- [ ] URL present IF relevant (after outcome, before byline) — required when branches pushed (compare URL), **omitted** when no branches pushed; **after PR creation**: compare URL becomes PR URL, label changes from "Compare URL" to "PR URL"; label and URL format MUST match context — mismatch is a critical violation
- [ ] AI byline present as **LAST** element (after URL, or after outcome when no URL)
- [ ] No URL before executive summary
- [ ] No byline before URL/outcome

**Evidence requirement:** Each checkpoint verification MUST produce a tool-call artifact (e.g., verification of composed message content) confirming the element is present or correctly absent. Verbal assertion without tool-call evidence is insufficient.

**URL applicability:**

| Scenario | URL Required? | Label | URL Format |
| -- | -- | -- | -- |
| Branches pushed, no PR yet | ✅ Yes | Compare URL | `compare/dev...<work-branch>` |
| PR already created | ✅ Yes | PR URL | `pull/<PR-number>` |
| No branches pushed | ❌ No | (omit) | Omit URL element entirely |

**Auto-fix on failure:** If any element is missing or misordered, fix the output before sending. Missing elements are MISSING-ELEMENT (auto-fix). Missing URL when required → generate URL. URL included when not applicable → STRUCTURE-VIOLATION, remove URL and reorder. Wrong ordering is STRUCTURE-VIOLATION (auto-fix). Elements are auto-fixed before output is sent — NOT reported after the fact.

**Issue comments:**
Post completion comment on each issue ONLY if substantive (per `issue-operations` skill `comment` task Substantive Comment Gate). Skip comment for non-substantive completions.

**HALT condition:**

- Do NOT create PR
- Do NOT close issues
- Wait for explicit "create a PR" instruction

## Intent-and-Context Metadata

`prior_context` replaces the old `prior_results` field. It is:

- **AI-composed**: The orchestrating agent intelligently composes the metadata based on the relationship between issues
- **No fixed template**: Format is flexible prose, not a structured form
- **Focus on intent**: Design decisions, edge case handling, assumptions, non-obvious constraints, interfaces that later issues depend on
- **NOT a change summary**: What changed is in git; why it changed is in prior_context

**What to include in prior_context:**

- Key design decisions made during implementation
- Non-obvious constraints discovered (e.g., "API returns 404 for missing items, not 403")
- Interfaces exposed that dependents should use
- Edge cases handled and how
- Assumptions that downstream code relies on

**What NOT to include:**

- List of files changed (available via `git diff`)
- Diff contents (available via `git log -p`)
- Verbatim spec text (sub-agent reads the spec directly)

## Frozen Branches

Once a prior issue's branch is merged into a dependent branch, it is **frozen**:

- No rebasing, amending, or force-pushing the frozen branch
- If a backtrack is needed:
  - Minor fix: Fix on the frozen branch, then each dependent branch re-merges
  - Major change: Full review of all dependent implementations, potential discard-and-restart
  - AI agent assesses scope based on blast radius
  - Always requires explicit developer authorization before proceeding

## Edge Cases

### Sub-Agent Failure

```
assemble-work:
    → Dispatch sub-agent for #B
        → Sub-agent fails (error/timeout)
        → Record failure
    → If #B has dependents (#C requires #B): skip #C, report both
    → If #C is independent: continue with #C
    → After all possible issues complete:
        → Report failures clearly
        → HALT with partial results if any issues succeeded
```

### Sub-Agent Discovers Bug

```
assemble-work:
    → Dispatch sub-agent for #B
        → Sub-agent discovers bug per bug-discovery protocol
        → Sub-agent reports bug as finding (read-only)
        → Sub-agent HALTs implementation for #B
        → Records: "#B halted — bug discovered at <location>"
    → Continue to next independent issue
    → Report bug in work summary
```

### Tier 3 Conflict During Dependency Merge

- HALT immediately
- Report the conflict and which two branches are involved
- Do NOT attempt to resolve intent conflicts automatically
- Wait for developer review per `conflict-resolution` skill

### Session Restart Mid-Work

- Use `git log --oneline` on the work branch to determine completed issues
- Each squash-merged commit in the work branch corresponds to one completed issue
- Resume from the first incomplete issue by checking which issue numbers appear in commit messages
- Feature branches still contain the individual issue work for reference

### Parallel-Safe Issues (No Dependencies) — Opportunistic Only

- Even independent issues SHOULD be stacked sequentially. Parallel execution is opportunistic — it depends on circumstances genuinely allowing it (no shared files, no logical coupling, no hidden dependencies).
- "Independent" in a work context means "no declared dependency," not "safe to run in parallel." Stacking catches hidden dependencies automatically.
- If parallel execution is chosen for an independent issue, document the justification in the work state file with explicit reasoning (why stacking was bypassed, what makes the issue genuinely independent).

## Mandatory Rules

01. **Main agent NEVER edits implementation files** — only orchestrates
02. **Every sub-agent runs verification + finishing** — no skipping
03. **One branch per issue** — each issue gets its own feature branch, never shared
04. **Dependency resolution via git merge** — later issues merge prior branches, not branch-from-prior
05. **Frozen branches after merge** — no rebasing or amending a merged branch
06. **No HALTs between issues** — all issues complete before single HALT
07. **Single work PR** — squash-merge each feature branch into work branch, then one PR
08. **Intent-and-context metadata** — AI-composed, no fixed template, focus on why not what
09. **Conflict resolution tiers** — auto-resolve 1-2, HALT on tier 3 during dependency merges
10. **Always work mode** — single issue = work-of-1, no special-case path
11. **Decision Log persistence** — after each sub-agent returns, append `decision_log_entry` as a dedicated GitHub Issue comment on the Plan issue. Decision Log uses comments (not body edits) for lightweight, append-only, session-surviving persistence

Co-authored with AI: <AgentName> (<ModelId>)

## Live Verification: Work State Claims (MANDATORY)

**Each work state claim MUST be verified against actual git and GitHub state. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Work state file exists" | Verify work state file in `./tmp/` | `glob(pattern="./tmp/work-*.md")` | MISSING-ELEMENT |
| "All sub-agents returned" | Verify result contracts collected | Check for all expected result contracts | VERIFICATION-GAP |
| "Branch merged into work branch" | Verify merge commit exists | `git log --oneline work-branch` → check merge messages | VERIFICATION-GAP |
| "Decision log persisted" | Verify comment on Plan issue | `github_issue_read(method=get_comments)` → search for decision log | MISSING-ELEMENT |
| "Authorization carries forward" | Verify work state contains auth context | Read work state file for auth section | STRUCTURE-VIOLATION |

**Evidence artifact:** Tool call results confirming work state accuracy.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Work state file missing | MISSING-ELEMENT | auto-fix | Create or locate work state file |
| Sub-agent result missing | VERIFICATION-GAP | conditional | Wait for or re-dispatch sub-agent |
| Merge not in work branch | VERIFICATION-GAP | conditional | Re-merge feature branch |
| Decision log not persisted | MISSING-ELEMENT | auto-fix | Post decision log comment now |
| Auth context missing from work state | STRUCTURE-VIOLATION | conditional | Re-read auth from approval-gate |