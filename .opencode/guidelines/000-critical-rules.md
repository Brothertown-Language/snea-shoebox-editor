# CRITICAL RULES — Zero Tolerance Violations

**See AGENTS.md for the authoritative list of critical rules.**
**See `.opencode/guidelines/` for detailed rules.**

This file provides critical rules that must never be violated. Sections with full detail in dedicated guidelines are referenced here with one-line pointers — the referenced guideline contains the complete rule, enforcement matrix, and examples.

## Critical Violation: Worktree Bypass — Using stash+checkout Instead of Worktrees

**⚠️ Using `stash + checkout -b` instead of worktrees for ANY feature branch creation is a CRITICAL GUIDELINE VIOLATION.**

Worktrees are ALWAYS mandatory for feature branch creation. **See `using-git-worktrees` skill for the complete worktree creation procedure. See `060-tool-usage.md` §1-2 for tool priority hierarchy and path resolution rules.** **AUTHORITY: `060-tool-usage.md` §1-2** (this line is a reference only)

- 🚫 FORBIDDEN: `git checkout -b`, `stash + checkout`, operating in main working directory, ignoring `WORKTREE_FATAL=1`
- ✅ REQUIRED: `using-git-worktrees` skill for every feature branch; HALT if `WORKTREE_FATAL=1` or `WORKTREE_PATH` empty

## Critical Violation: Skipping Git Pre-Check Before ANY Work

**⚠️ Working on files without checking git state is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Starting work without creating a worktree first; operating in main working directory; creating/editing files on `main` or `dev`
- ✅ REQUIRED: See `git-workflow` skill `--task pre-work` for mandatory worktree creation and environment verification

## Critical Violation: Relative File Paths in Worktree Context

**⚠️ Using relative paths with `read`/`edit`/`write`/`glob`/`grep` tools when `WORKTREE_PATH` is set is a CRITICAL GUIDELINE VIOLATION.**

**See `060-tool-usage.md` §2 "Path Rules (ZERO TOLERANCE)" for the complete tool-by-tool table showing wrong vs correct path resolution, and the `using-git-worktrees` skill → "Tool Usage Compliance" section for worktree-specific guidance.** **AUTHORITY: `060-tool-usage.md` §2** (this line is a reference only)

- 🚫 FORBIDDEN: Relative paths with file operation tools when `WORKTREE_PATH` is set; assuming tools respect `workdir`
- ✅ REQUIRED: Prefix ALL paths with `WORKTREE_PATH` when in worktree context

## Critical Violation: Sub-Agents Ignoring Worktree Context

**⚠️ Sub-agents that modify the main repo instead of the worktree are a CRITICAL GUIDELINE VIOLATION.**

When a main agent is operating in a worktree and dispatches a sub-agent, the sub-agent MUST receive `WORKTREE_PATH` in its dispatch context and use it as the base directory for ALL file operations and git commands.

- 🚫 FORBIDDEN: Spawning sub-agents without `WORKTREE_PATH` when operating in a worktree; sub-agents that stage/commit to the main repo's working directory; skills that perform git or file operations without a "Worktree Mode" section
- ✅ REQUIRED: Pass `WORKTREE_PATH` in ALL sub-agent dispatch prompts when set; sub-agents verify `git rev-parse --show-toplevel` matches `WORKTREE_PATH` before mutating state; all new skills MUST include worktree awareness per `skill-creator` skill requirements

## Critical Violation: Implementing Without Verifying Against Live Documentation

**⚠️ Implementing code without verifying API signatures, environment variables, or function parameters against live documentation is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Using unverified APIs, guessed env vars, outdated patterns, or memory-based signatures
- ✅ REQUIRED: Verify API signatures from official docs, confirm env vars from config, use `srclight_get_signature` for code signatures

## Critical Violation: Schema/API/Code Verification — Claiming Knowledge Without Verification

**⚠️ Asserting config schema compliance, API signatures, or code implementation details without verifying against live documentation or live source is a CRITICAL GUIDELINE VIOLATION.**

**See `065-verification-honesty.md` → "Proactive Verification" section for the complete rule, evidence requirements, examples, and when proactive verification applies.** **AUTHORITY: `065-verification-honesty.md` Proactive Verification** (this line is a reference only)

- 🚫 FORBIDDEN: Asserting config compliance without fetching and verifying the actual schema
- 🚫 FORBIDDEN: Using API signatures from training data without verifying against live documentation or `srclight_get_signature`
- 🚫 FORBIDDEN: Claiming code behavior without checking via `srclight_get_symbol`, `read`, or `srclight_get_signature`
- 🚫 FORBIDDEN: Writing specs or code that reference schema fields, API parameters, or function signatures from memory
- ✅ REQUIRED: Fetch and verify config schemas before asserting compliance
- ✅ REQUIRED: Verify API signatures via `srclight_get_signature` or official documentation before using them
- ✅ REQUIRED: Verify code implementation details via `srclight_get_symbol`, `read`, or `srclight_get_signature` before claiming behavior
- ✅ REQUIRED: Tag any assertion that could not be verified as `(unverified)`

## Critical Violation: Verification Dishonesty — Reporting Memory as Verified

**⚠️ Reporting unverified information as verified, or using memory recall instead of actual verification, is a CRITICAL GUIDELINE VIOLATION.**

**See `065-verification-honesty.md` for the complete rule, evidence requirements, single exchange window exception, and relationship to other guidelines.** **AUTHORITY: `065-verification-honesty.md`** (this line is a reference only)

- 🚫 FORBIDDEN: Reporting from memory without re-verification; claiming "I checked earlier" without current tool call; training knowledge as fact; omitting tool call evidence
- ✅ REQUIRED: Use a tool/command for every verification; show evidence; tag unverified recollections as "(unverified)"

## Critical Violation: Acting on Resources Without Reading All Comments

**⚠️ Acting on a GitHub/GitBucket resource without reading ALL comments is a CRITICAL GUIDELINE VIOLATION.**

**See `067-context-completeness.md` for the complete rule, evidence requirements, staleness rule, single exchange window exception, and reading requirements per resource type.** **AUTHORITY: `067-context-completeness.md`** (this line is a reference only)

- 🚫 FORBIDDEN: Acting after reading only the issue body; reviewing PRs without reading comments; assuming "no new comments"; caching comment state
- ✅ REQUIRED: Read ALL comments before any action; show evidence of having read them; re-read before significant actions; use `github_issue_read` with `method=get_comments`

## Critical Violation: Skipping Post-Implementation Verification Skills

**⚠️ Failing to invoke `verification-before-completion` and `finishing-a-development-branch` after implementation is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Claiming complete without invoking verification skills; manually executing skill steps; skipping verification because "changes look correct"
- ✅ REQUIRED: See `verification-before-completion` skill `--task verify` for evidence requirements; `finishing-a-development-branch` skill `--task checklist` for branch readiness; `git-workflow` skill `--task review-prep` for post-implementation workflow

## Critical Violation: Skipping review-prep After Implementation

**⚠️ Failing to invoke `review-prep` after implementation is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Marking complete without commit/push/URL; skipping review-prep for any reason; proceeding without URL in chat
- ✅ REQUIRED: See `git-workflow` skill `--task review-prep` for mandatory commit, push, compare URL, and HALT protocol

## Critical Violation: Wrong Chat Output at Halt Points

**⚠️ Producing casual summaries at halt points instead of the mandatory format (exec summary → outcome → URL → byline) is a CRITICAL GUIDELINE VIOLATION.**

**URL Label Context:**

| Context | Label | URL Format |
| -- | -- | -- |
| Pre-PR (after push, before PR creation) | **Compare URL** | `compare/dev...<branch-name>` |
| Post-PR (PR has been created) | **PR URL** | `pull/<PR-number>` |

Using "Compare URL" after a PR has been created is a format violation — the label MUST be "PR URL" with the `pull/N` format. Using "PR URL" before a PR exists is also a format violation — the label MUST be "Compare URL" with the `compare/dev...` format.

The format applies to ALL halt points where implementation is reported complete:

- **review-prep** after implementation
- **Sub-agent result reports** from divide-and-conquer dispatch
- **Phase boundary halts** (merge gates between phases)
- **Approval-gate post-implementation** reports
- **Batch orchestration** reports (assemble-batch Step 6)
- **Completion task** reports (approval-gate completion)

**Mandatory format:**

```
**Summary:**

<1-2 sentences describing impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

<Compare URL or Issue URL>

🤖 <AgentName> (<ModelID>) <status>
```

- 🚫 FORBIDDEN: Producing casual one-liner summaries at halt points; omitting any element (summary, outcome, URL, byline); wrong ordering (URL before summary, byline before URL); reporting missing elements after the fact instead of auto-fixing before output is sent
- ✅ REQUIRED: Verify chat output format before sending at every halt point; auto-fix missing or misordered elements before output is sent; summary first, outcome after summary, URL before byline, byline last

**See `git-workflow` skill → "Chat Output Format (CRITICAL)" for complete format requirements and examples. See `approval-gate/tasks/post-implementation.md` Step 4.5, `approval-gate/tasks/completion.md`, `divide-and-conquer/tasks/assemble-batch.md` Step 6, `finishing-a-development-branch/tasks/checklist.md` §Chat Output Format, and `git-workflow/tasks/review-prep.md` §Live Verification for the verification checkpoints.**

## Critical Violation: Wrong PR Body Format

**⚠️ Writing implementation details instead of executive summary in PR bodies is a CRITICAL GUIDELINE VIOLATION.** PR bodies use Summary/Outcome/Fixes format.

**See `git-workflow` skill → `pr-creation` task → "PR Body Requirements" for complete format specification.**

## Critical Violation: Uncommitted/Unpushed Changes After Implementation

**⚠️ Marking implementation complete WITHOUT committing and pushing is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Marking complete with uncommitted changes; skipping commit/push because "changes are small"
- ✅ REQUIRED: See `finishing-a-development-branch` skill `--task checklist` for complete commit/push verification

## Critical Violation: Wrong Compare URL Base Branch

**⚠️ Using `main` as base branch in compare URLs for feature branches is a CRITICAL GUIDELINE VIOLATION.**

Feature branches target `dev`. Compare URLs: `compare/dev...<branch-name>`. Only release PRs use `compare/main...dev`.

## Critical Violation: Fabricating URLs — ZERO TOLERANCE

**⚠️ Generating URLs from memory, guesswork, or hardcoded patterns is a CRITICAL GUIDELINE VIOLATION.** All URLs must be constructed from session-enforcement plugin output. No exceptions.

- 🚫 FORBIDDEN: Hard-coding domains; using "known correct" URLs from previous sessions; guessing from git remotes; caching URL bases across sessions
- ✅ REQUIRED: Extract `GITBUCKET_HTML_URL`/`GITBUCKET_URL` from session init; construct all URLs from those values; HALT if session init missing

## Critical Violation: Inferring GitHub Owner from File Paths/Usernames

**⚠️ Inferring GitHub owner from file paths or usernames is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Inferring owner from file paths, `$USER`, `git config user.name`, cached values; making GitHub MCP calls without session init values
- ✅ REQUIRED: Use `GIT_OWNER` and `GIT_REPO` from session init for EVERY GitHub MCP call

## Critical Violation: Missing AI Co-Authored Attribution

**⚠️ Failing to include AI co-authored attribution is a CRITICAL GUIDELINE VIOLATION.** Applies to original AI-authored content, NOT copy-pasted content.

- **Requires attribution**: Python docstrings, READMEs, new repos, original docs
- **Exempt**: Standard licenses, copy-pasted code, auto-generated files, framework boilerplate, minor edits
- **Format**: `Co-authored with AI: <AI-Name> (<model-id>)`

**See `080-code-standards.md` for complete attribution requirements (file types, formats, exceptions).** **AUTHORITY: `080-code-standards.md`** (this line is a reference only)

## Critical Violation: Offer-to-Edit Bypass — Offering to Modify Files Without Spec

**⚠️ Offering to modify files without a spec is a CRITICAL GUIDELINE VIOLATION.**

When the agent identifies a problem and the fix is clear, the ONLY permitted next action is creating a spec or reporting the finding. Never offer to edit, update, modify, or fix a file directly.

| Pattern | Correct Action |
|---------|---------------|
| "Want me to update X?" | Create a spec for the update, HALT |
| "Shall I fix this?" | Create a bug report or fix spec, HALT |
| "I can change X to Y" | Create a spec for the change, HALT |
| "Ready to implement?" | Create a spec first, then HALT |

**Why this matters:** The offer-to-edit pattern is a rationalization bypass. The agent reasons: "I'm not *doing* the edit, I'm just *offering* — so I'm not violating the rule." But the offer normalizes direct edits and creates social pressure to authorize without a spec. The spec-first workflow exists precisely to prevent this.

## Critical Violation: Hardcoded Identity Values in Skills and Guidelines

**⚠️ Hardcoding agent names, model IDs, developer names, developer emails, org names, repo names, or platform names in skill files, guideline files, task files, or any AI agent configuration is a CRITICAL GUIDELINE VIOLATION.**

All identity values MUST use placeholder tokens that are resolved at runtime from session init output. Hardcoded values become stale when models, agents, orgs, or repos change.

- 🚫 FORBIDDEN: `<specific-agent-name>` (e.g., `OpenCode`, `OpenCode Desktop`, `Claude`) in skill files, guidelines, or task files
- 🚫 FORBIDDEN: `<specific-model-id>` (e.g., `ollama-cloud/glm-5`, `claude-3-5-sonnet`) in skill files, guidelines, or task files
- 🚫 FORBIDDEN: `michael-conrad`, `muksihs`, or any specific developer name/email in skill files, guidelines, or task files
- 🚫 FORBIDDEN: `Brothertown-Language`, `snea-shoebox-editor`, or any specific org/repo name in skill files, guidelines, or task files
- ✅ REQUIRED: Use `<AI-Name>`, `<model-id>`, `<AgentName>`, `<ModelID>`, `DEV_NAME`, `DEV_EMAIL`, `GIT_OWNER`, `GIT_REPO` placeholders everywhere
- ✅ REQUIRED: Skill-creator MUST validate that no hardcoded identity values appear in generated skill files
- ✅ REQUIRED: Spec-auditor MUST flag hardcoded identity values as STRUCTURE-VIOLATION auto-fix findings

**Applies to:** SKILL.md files, task/*.md files, guideline files, agent configuration files, code comments that serve as templates or examples.

**Exempt from placeholders (concrete values are OK):** Python source code runtime strings, test fixtures, historical changelog entries, repository URLs in examples that use `<GIT_OWNER>/<GIT_REPO>` pattern.

**See `080-code-standards.md` for the complete placeholder reference and `skill-creator/SKILL.md` for the validation gate.** **AUTHORITY: `080-code-standards.md`** (this line is a reference only)

## Critical Violation: Implementation Without Spec — Expanding the Definition

**⚠️ "Implementation" includes more than writing source code.** The spec-first rule applies to ALL file modifications that alter behavior, configuration, or enforcement.

The following are ALL implementation actions that require an approved spec:

| Action | Requires Spec? | Why |
|--------|---------------|-----|
| Writing Python code | ✅ Yes | Classic implementation |
| Editing skill files (SKILL.md, task/*.md) | ✅ Yes | Alters agent enforcement behavior |
| Editing guideline files | ✅ Yes | Alters agent constraints |
| Editing configuration (pyproject.toml, .pre-commit-config.yaml) | ✅ Yes | Alters build/test behavior |
| Editing TypeScript plugins (session-enforcement.ts) | ✅ Yes | Alters runtime enforcement |
| Editing test files | ✅ Yes | Alters test suite behavior |
| Creating new files of any type | ✅ Yes | Adds new behavior or content |
| Fixing a typo in documentation | ❌ No | No behavioral change |
| Formatting code (ruff format) | ❌ No | No behavioral change |
| Spec-auditor auto-fix on GitHub Issue | ❌ No* | Non-substantive; see audit auto-fix exemption below |

**\* Audit Auto-Fix Exemption:** Spec-auditor auto-fixes applied to GitHub Issues are NOT implementation actions when ALL of the following conditions are met:

- The audit was deliberately invoked (user-triggered via `spec-auditor --issue N` or pipeline-triggered)
- Findings are classified as `auto-fix` by spec-auditor's three-tier model
- Fix is applied to a GitHub Issue body (not source code, not skill files, not guideline files)
- Fix is non-substantive (structure violations, missing boilerplate, boilerplate titles, numbering, trace links, approach differences, inline context replacement, concern separation fixes)
- **`conditional` fixes require separate authorization before application** (they are NOT auto-applied without explicit "approved"/"go")
- **`flag-for-review` findings are reported in the executive summary but NOT applied**

When any condition is NOT met, the action reverts to requiring an approved spec per the standard "Implementation Without Spec" rule.

**See `010-approval-gate.md` → "Audit Auto-Fix Exemption" for the complete exemption section and `spec-auditor` skill → "Auto-Fix Model" for the three-tier classification.** **AUTHORITY: `010-approval-gate.md` Audit Auto-Fix Exemption** (this line is a reference only)

**🚫 FORBIDDEN patterns (all require spec):**
- "It's just a skill file" → Skill files alter agent enforcement. Spec required.
- "It's just a guideline" → Guidelines alter agent constraints. Spec required.
- "It's just a config change" → Config changes alter behavior. Spec required.
- "It's a small fix" → Size doesn't matter. If it changes behavior, spec required.

**See `010-approval-gate.md` for the complete authorization workflow.** **AUTHORITY: `010-approval-gate.md`** (this line is a reference only)

## Critical Violation: Missing Progress Reports

**⚠️ Failing to report progress in chat after implementation is a CRITICAL GUIDELINE VIOLATION.**

Progress executive summaries go to **chat ONLY**, not GitHub Issue comments. Issue comments are for **substantive, stakeholder-meaningful information** only.

Chat output order (mandatory): 1) Executive summary, 2) URL (if exists), 3) AI byline LAST — `🤖 <AgentName> (<ModelID>) <status>`

**See `github-comments` skill for Issue comment requirements and the complete channel routing table.**

## Critical Violation: Ignoring Issue Comments

**⚠️ Failing to respond to user comments on GitHub Issues is a CRITICAL GUIDELINE VIOLATION.**

**MANDATORY: Read issue comments and respond publicly. See `github-comments` skill → "Responding to User Comments (MANDATORY)".**

## Critical Violation: Sub-issue Structure Bypass — Multi-task Plans

**⚠️ Implementing a multi-task plan without sub-issues is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Implementing phases without sub-issue structure; assuming markdown checkboxes = tracking; creating step-level sub-issues
- ✅ REQUIRED: Sub-issues at PHASE level under the plan (not the spec); each linked via `github_sub_issue_write method=add`; single-task plans exempt; auto-create as pre-implementation setup
- ✅ REQUIRED: Plan is the parent of implementation sub-issues; spec references plan via body linked reference, NOT GitHub sub-issue link

**See `github-sub-issues` skill for complete workflow including single-task exemption, auto-create workflow, and database ID requirement. Sub-issue verification is consolidated into `approval-gate --task verify-authorization` Step 5 as the single readiness check.**

## Critical Violation: Stopping After Single Phase in Multi-Task Plan

**⚠️ Halting after completing a single phase of a multi-task plan is a CRITICAL GUIDELINE VIOLATION.** Plan approval cascades authorization to ALL sub-issues under the plan. Complete ALL phases, report ONCE, HALT ONCE.

**See `approval-gate` skill → "Multi-Task Plan Authorization" for complete cascade workflow and enforcement matrix.**

## Critical Violation: Sub-issue Closure Timing — ZERO TOLERANCE

**⚠️ Closing sub-issues before PR merge is a CRITICAL GUIDELINE VIOLATION.** Sub-issues are children of the plan, not the spec.

🚫 FORBIDDEN: Closing sub-issues after implementation but before PR merge; closing without verifying PR merge via GitHub API

**See `git-workflow` skill `--task cleanup` for complete post-merge verification and closure workflow.**

## Critical Violation: Scope Creep — NEVER Do Things Outside the Spec

**⚠️ Implementing changes not explicitly called for in the spec is a CRITICAL GUIDELINE VIOLATION.** The spec defines EXACTLY what to implement.

🚫 FORBIDDEN: Helper functions, improving nearby code, refactoring adjacent things, fixing similar issues, any change not in the spec

If you think something ELSE should be changed: 1) STOP, 2) Comment on the issue, 3) Wait for explicit approval.

## Critical Violation: Spec Without Investigation

**⚠️ Creating a spec without completed investigation is a CRITICAL GUIDELINE VIOLATION.**

🚫 FORBIDDEN: Specs from vague requirements; skipping codebase analysis; finalizing without edge cases; proceeding without success criteria

**The concrete minimum standard is the code inspection checklist in `015-pre-spec-inspection.md`** — all six items (trace call paths, verify imports, detect dead code, verify format/protocol assumptions, confirm architectural layer, check for existing alternatives) MUST be addressed before proposing any approach. Incomplete inspection = this critical violation.

**See `brainstorming` skill for investigation requirements and completion criteria. See `015-pre-spec-inspection.md` for the mandatory checklist and evidence requirements.** **AUTHORITY: `015-pre-spec-inspection.md`** (this line is a reference only)

## Critical Violation: Implementing Stale or Superseded Specs

**⚠️ Implementing a stale or superseded spec without revision is a CRITICAL GUIDELINE VIOLATION.**

**See `github-issue-creation` skill `--task pre-creation` for the complete superseded/stale spec check procedure.**

- If superseding issue exists: SILENTLY HALT, report conflict, wait for direction
- If stale: REVISE spec, report revision, HALT for approval — never implement stale without revision

## Critical Violation: Main Agent Implements Directly

**⚠️ The main agent implementing files directly instead of dispatching to sub-agents is a CRITICAL GUIDELINE VIOLATION.**

**See `divide-and-conquer` skill `--task assemble-batch` for the complete sub-agent dispatch workflow.**

- 🚫 FORBIDDEN: Main agent editing implementation files directly during batch orchestration
- 🚫 FORBIDDEN: Bypassing assemble-batch for single-issue dispatch
- 🚫 FORBIDDEN: Code-path divergence between single and batch issue handling
- ✅ REQUIRED: All implementation dispatches through `assemble-batch` — single issue is a single-item batch
- ✅ REQUIRED: Main agent only orchestrates — never edits implementation files
- ✅ REQUIRED: Context window stays clean for orchestration decisions

## Auditor Skills Enforcement

**⚠️ MANDATORY: Run `spec-auditor` when auditing specs. NO SKIPPING.**

Trigger words: "audit this spec", "review this issue", "revisit this task", "check this [SPEC]", "validate the spec"

**See `spec-auditor` skill for the complete orchestration model, auto-fix classification, baseline subtasks, conditional subtasks, and invocation commands.**

| Trigger | Action |
| -- | -- |
| Spec created | REQUIRED: `spec-auditor --issue N` |
| "Audit/review/revisit this spec" | REQUIRED: `spec-auditor --issue N` |
| Before implementation approval | REQUIRED: Verify no critical issues |
| Guideline change proposed | Optional: `guideline-auditor` |

**Auto-fix model (v3):** Spec-auditor classifies all findings into three tiers and acts on them:
- **Auto-fix:** Safe, mechanical fixes applied directly (structure violations, missing boilerplate, boilerplate titles, approach differences, concern separation)
- **Conditional:** Applied after safety check (scope creep, context overflow)
- **Flag-for-review:** Reported in executive summary only (ambiguous findings, conflicts)

**Executive summary (v3):** After every audit, a structured executive summary MUST be posted to chat with: (a) changes made, (b) findings not acted on with reasons, (c) issue URL. See `spec-auditor` skill → `Chat Executive Summary` for format.

## Critical Violation: Creating PRs Without Explicit Instruction

**⚠️ Creating a PR without EXPLICIT developer instruction is a CRITICAL GUIDELINE VIOLATION.** PRs require "create a PR", "make a PR", "push and create PR", "let's get a PR up", "PR" (bare), or "PR #NNN".

**See `pr-creation-workflow` skill for the full PR timing workflow including authorization boundary.**

## Critical Violation: Bug Reports Without Fix Spec

**⚠️ Bug reports must have a fix spec sub-issue before closure is a CRITICAL GUIDELINE VIOLATION.** Fix specs follow the plan-bridge hierarchy: spec → plan → sub-issues.

- 🚫 FORBIDDEN: Closing a bug report without a linked fix spec sub-issue; treating bug reports as complete without fix spec
- ✅ REQUIRED: Use `issue-review --task analyze-and-spec` to create fix spec sub-issues for bug reports; verify fix spec exists via `approval-gate --task verify-fix-spec` before closure

**See `issue-review` skill → `analyze-and-spec` task for the complete root cause analysis and fix spec creation workflow, and `approval-gate` skill → `verify-fix-spec` task for verification.**

## Critical Violation: Bug Discovery Does NOT Authorize Bug Fixing

**⚠️ Finding a bug during analysis does NOT authorize fixing it.** Bug discovery is a reporting action, NOT an implementation authorization.

**See `approval-gate` skill for the complete discovery protocol and authorization matrix.**

- 🚫 FORBIDDEN: Editing source code after discovering a bug; creating branches without approved spec; treating discovery as authorization
- ✅ REQUIRED: Create bug report issue (permitted without auth); invoke `issue-review --task analyze-and-spec` for root cause analysis; perform read-only analysis; HALT and wait for authorization

## Critical Violation: Conflating Issue References with Authorization Cascade

**⚠️ Treating issue references as sub-issue relationships that trigger authorization cascade is a CRITICAL GUIDELINE VIOLATION.** In the plan-bridge hierarchy, the spec references the plan via body text (linked reference), NOT via GitHub sub-issue link. Only plan → sub-issue links trigger cascade.

- 🚫 FORBIDDEN: Cascading authorization based on mentions in body/comments; assuming `#NNN` creates authorization links; treating spec's body reference to a plan as a sub-issue link
- ✅ REQUIRED: Only formal sub-issue links via `github_sub_issue_write` trigger cascade; verify with `github_issue_read(method=get_sub_issues)` on the **plan**, not the spec

**See `approval-gate` skill → "Reference ≠ Authorization Cascade" for the complete verification procedure.**

## Critical Violation: Ignoring Spec-to-Plan Approval Cascade

**⚠️ Requiring manual plan approval when a spec is approved and a faithful plan already exists is a CRITICAL GUIDELINE VIOLATION.**

The spec-to-plan approval cascade means: when a spec is approved and a plan already exists that is faithful to the spec, the plan is automatically approved. Manual plan approval is only required when no plan exists at the time of spec approval (the standard two-gate flow: spec approval → plan creation → plan approval → implementation).

- 🚫 FORBIDDEN: Requiring manual plan approval when a faithful plan already exists at the time of spec approval
- 🚫 FORBIDDEN: Treating spec approval as only authorizing plan creation when a faithful plan already exists
- 🚫 FORBIDDEN: Bypassing the two-gate model when no plan exists (cascade does NOT apply — normal flow required)
- ✅ REQUIRED: Auto-approve faithful existing plans when their linked spec is approved
- ✅ REQUIRED: Verify plan fidelity before cascading (plan must faithfully represent the approved spec)
- ✅ REQUIRED: Spec revision still revokes plan approval per existing "Revision Revokes Approval" rules

**Edge cases:** Plan not faithful → fidelity audit catches deviations, plan must be revised and re-approved. Spec revised → revokes all linked plan approvals (existing behavior). No plan exists → normal two-gate flow, no cascade. Multiple plans → most recent approved plan takes precedence, older plans superseded.

**See `010-approval-gate.md` → "Spec-to-Plan Approval Cascade" for the complete cascade rules and edge case documentation.** **AUTHORITY: `010-approval-gate.md` Spec-to-Plan Approval Cascade** (this line is a reference only)

## Critical Violation: Confirmation ≠ Authorization

**⚠️ User confirmation of an observation does NOT constitute implementation authorization.**

- Only "approved", "go", "#NNN approved" authorize implementation
- "Yes, that's correct" = confirmation of observation, NOT authorization

**See `approval-gate` skill → "Confirmation ≠ Authorization" for the complete enforcement table.**

**See `020-go-prohibitions.md` §1 "Discussion Conclusion Patterns" for examples of non-authorization discussion conclusions.** **AUTHORITY: `020-go-prohibitions.md` §1** (this line is a reference only)

## Critical Violation: Closing Issues Before PR Merge

**⚠️ Closing issues BEFORE the PR is merged is a CRITICAL GUIDELINE VIOLATION.** In the plan-bridge hierarchy, close sub-issues under the plan first, then the plan, then the spec.

🚫 FORBIDDEN: Closing after implementation; closing when PR created but not merged; closing parents while children open; closing without "merge confirmed"

**See `git-workflow` skill `--task cleanup` for complete post-merge verification.**

## Critical Violation: Skipping PR for Documentation/Guideline Changes

**⚠️ Documentation and guideline changes are NOT exempt from PR workflow.** ALL file modifications require full PR workflow. The only exceptions: ZERO files modified, or already-implemented specs (verified by `verify-already-implemented` task).

## Critical Violation: Parent/Child Issue Closure

**⚠️ Closing a parent issue while child issues remain open is a CRITICAL GUIDELINE VIOLATION.** Only close the child corresponding to the merged PR. Parent stays open until ALL children are closed. In the plan-bridge hierarchy, the plan (not the spec) is the parent of implementation sub-issues.

**See `git-workflow` skill `--task cleanup` for the complete parent/child closure workflow.**

## Critical Violation: Deleting Branches/Stashes Improperly

**⚠️ Improper branch deletion is a CRITICAL GUIDELINE VIOLATION.** Merged branches: DELETE IMMEDIATELY. Unmerged branches with work: PRESERVE. Stashes: PRESERVE until asked.

- 🚫 FORBIDDEN: `git branch -D` on unmerged without request; `git stash drop` without request; keeping merged branches
- Merged PR → DELETE IMMEDIATELY | Unmerged → PRESERVE | Stashes → PRESERVE | `main` → NEVER DELETE

## Critical Violation: Blind Conflict Resolution

**⚠️ Resolving git conflicts using "ours"/"theirs" heuristics without classifying conflict tier is a CRITICAL GUIDELINE VIOLATION.**

**See `conflict-resolution` skill for the complete procedural workflow including classification, notification, and verification.**

Three tiers: **Tier 1 (Trivial)**: whitespace/formatting → auto-resolve, silent. **Tier 2 (Textual but safe)**: same intent, different text → auto-resolve, note in chat. **Tier 3 (Intent conflict)**: different goals or spec compliance at risk → HALT, flag for developer review.

## Critical: Engineering Mindset Required

**⚠️ All work must be approached with proper engineering discipline.** See `engineering-approach` skill for complete requirements. **AUTHORITY: `engineering-approach` skill** (this line is a reference only)

1. Understand Before Solving — Read all relevant code before proposing changes
2. Design Before Implementing — Document approach and obtain approval before coding
3. Verify Before Declaring Complete — Run tests, check edge cases, validate success criteria
4. Communicate Changes — Post comments when substantive changes occur (NOT when creating issues, NOT for status updates)

No feature creep: implement ONLY what is in the approved spec. No unapproved work: wait for explicit "approved" or "go".

## Critical Violation: Skipping Completion Guarantee on Workflow Halt

**⚠️ Halting a skill workflow without invoking `--task completion` is a CRITICAL GUIDELINE VIOLATION.** When a state-modifying skill halts at any point — including error, failure, or early termination — the completion subtask MUST be invoked before halting.

- 🚫 FORBIDDEN: Halting mid-workflow without invoking `--task completion`; skipping completion because "nothing was done"; assuming cleanup happens automatically
- ✅ REQUIRED: Invoke `--task completion` on the current skill before halting; completion tasks are idempotent and safe to invoke multiple times

**See per-skill `tasks/completion.md` files and `.opencode/skills/completion-core/completion-core.md` for the shared completion operations.**

## Critical Violation: Silent Agent Termination

**⚠️ Agents that produce no output before stopping are a CRITICAL GUIDELINE VIOLATION.** If the agent halts, it MUST produce a status message explaining what was completed, what was attempted, and why the halt occurred.

- 🚫 FORBIDDEN: Producing zero output before stopping; silently failing without error message; context overflow without reporting the overflow; tool failure without reporting the failure; ending a session with no summary of work done
- ✅ REQUIRED: Every HALT MUST be preceded by a status message; every failure MUST be reported with the specific error; every context overflow MUST be reported with the specific cause; every completed task MUST produce an executive summary

**See `020-go-prohibitions.md` for the complete halt requirements and `finishing-a-development-branch` skill for completion guarantees.** **AUTHORITY: `020-go-prohibitions.md`** (this line is a reference only)

## Critical Violation: Skipping Interdependency Analysis for Batch Approvals

**⚠️ Processing multiple approved issues without interdependency analysis is a CRITICAL GUIDELINE VIOLATION.**

**See `approval-gate` skill → `pre-implementation-analysis` task for the complete procedure, classification heuristics, and output format.**

- 🚫 FORBIDDEN: Processing issues one-by-one without analysis; assuming independence without checking; hiding analysis in reasoning
- ✅ REQUIRED: Invoke `pre-implementation-analysis` for all approvals (single or batch); expand sub-issues; classify each issue; build dependency graph; present analysis in chat; execute in dependency order

## Critical Violation: Treating Branch Stacking as Optional

**⚠️ Bypassing stacking discipline without justification is a CRITICAL GUIDELINE VIOLATION. Stacking is a prerequisite for code correctness, not a preference.**

- 🚫 FORBIDDEN: Treating stacking as a "default preference" that can be overridden for convenience
- 🚫 FORBIDDEN: Interpreting "independent issues" as "must be parallel" — independence ≠ parallelism
- 🚫 FORBIDDEN: Dispatching sub-agents in parallel when stacking is the appropriate approach
- 🚫 FORBIDDEN: Choosing parallel execution because it "saves time" without verifying circumstances genuinely allow it
- ✅ REQUIRED: Sequential branch stacking as the prerequisite execution model
- ✅ REQUIRED: Explicit documented justification in batch state if parallel execution is chosen (opportunistic only)
- ✅ REQUIRED: Stack branches via `git merge <prior-branch>` into dependent branches before implementation
- ✅ REQUIRED: When in doubt, stack — parallel execution is never the starting assumption

## Critical Violation: Stale Todowrite State After Task Completion

**⚠️ Leaving stale or uncleared todowrite state after task completion is a CRITICAL GUIDELINE VIOLATION.**

When the `todowrite` tool is used during a session, the agent MUST maintain the full lifecycle: create items with correct status, update status as work progresses, and clear all items before halting.

- 🚫 FORBIDDEN: Leaving `pending` items after task completes; abandoning `in_progress` items without transitioning to `completed`; halting without calling `todowrite(todos=[])`; ignoring stale state from previous tasks
- ✅ REQUIRED: Transition each item to `in_progress` when work begins and `completed` when done; call `todowrite(todos=[])` to clear state before HALT; verify no stale items remain at session end

**See `060-tool-usage.md` §7 for the complete todowrite lifecycle rules (CREATE/UPDATE/CLEAR).** **AUTHORITY: `060-tool-usage.md` §7** (this line is a reference only)

## Critical Violation: Pushing Agent Intelligence Decisions to the User

**⚠️ Asking the user to make structural classification decisions that the agent should resolve autonomously is a CRITICAL GUIDELINE VIOLATION.**

Structural decisions — single-task vs multi-task classification, phase decomposition, scope sizing — are agent intelligence concerns. The agent must resolve them autonomously based on request analysis and codebase context.

- 🚫 FORBIDDEN: "Should this be a single-task spec or broken into phases?" — the agent decides
- 🚫 FORBIDDEN: "Is this a small change or a big one?" — the agent assesses
- 🚫 FORBIDDEN: "Do you want this as one spec or multiple?" — the agent classifies
- 🚫 FORBIDDEN: Any question where the answer is determinable from context, codebase, or request analysis
- ✅ REQUIRED: Classify autonomously and state the classification as part of the design proposal
- ✅ REQUIRED: Only ask when multiple valid structures exist with genuinely ambiguous trade-offs (e.g., 3+ subsystems with unclear boundaries)

**See `brainstorming` skill → `explore` task → "Autonomous Structural Classification" for the complete criteria.**

## Critical Violation: Process Gaps Are Bugs — Completed Issues Not Auto-Closed

**⚠️ Failing to follow a mandatory workflow step is a systemic failure, not an individual oversight.** Process gaps must be treated as bugs requiring guideline/skill fixes.

- 🚫 FORBIDDEN: "I just didn't do it" / "I forgot" / "I skipped it" as explanations for missed workflow steps
- 🚫 FORBIDDEN: Leaving issues open after their implementation is verified complete via merged PR
- 🚫 FORBIDDEN: Treating process gaps as acceptable human error rather than systemic bugs
- ✅ REQUIRED: When a process gap is discovered (e.g., completed issues not auto-closed, verification steps skipped), create a fix spec to prevent recurrence
- ✅ REQUIRED: Fix the guideline/skill to close the gap — the process must enforce itself, not rely on agent memory or diligence
- ✅ REQUIRED: Issues verified as already-implemented via merged PR MUST be auto-closed with a comment referencing the PR

**Why this matters:** If a mandatory step can be skipped by accident, the workflow is defective — not the agent. The correct response to a process gap is to fix the process (add enforcement to guidelines/skills), not to accept the gap as inevitable. "I forgot" means the process lacks a verification gate or checklist item that would catch the omission.

**See `approval-gate` skill → `verify-already-implemented` task → "Auto-Close Procedure" for the post-merge issue closure workflow. See `finishing-a-development-branch` skill → `checklist` task for issue-closure verification steps.**

## Critical Violation: Silent Halt Without Prompt — No Spec/Plan Search Before Stopping

**⚠️ Halting silently when no spec/plan exists for an implementation request — without first searching GitHub Issues for candidates and presenting them — is a CRITICAL GUIDELINE VIOLATION.**

When an agent receives an implementation instruction but cannot find an associated spec or plan, it must actively search for existing candidates before halting. A silent halt with no search and no presentation of options is a process gap that treats missing documentation as the user's problem rather than an actionable finding.

- 🚫 FORBIDDEN: Halting silently without searching GitHub Issues; presenting no candidates when implementation authorization lacks a matching spec/plan; offering only "create a new spec" without checking for existing specs first
- ✅ REQUIRED: Search GitHub Issues for candidate specs/plans using label filters (`[SPEC]`, `[PLAN]`, `[SPEC-FIX]`) and keyword matching against the request target; present all candidates with URLs; offer create-or-select before halting; flag as FAILURE if no candidates found
- ✅ REQUIRED: When no candidate exists, the agent MUST present the failure state ("No existing spec/plan found for [topic]") before offering to create one

**Why this matters:** The current Q/A mode halt is passive — it stops work but doesn't help the user find existing tracking. Active search turns "no spec found" from a dead end into a decision point: "here are N existing issues that may match, which one (if any) did you mean?" This reduces duplicate spec creation and connects implementation requests to existing tracking.

**See `020-go-prohibitions.md` §1 "NEVER DO" and "ALWAYS DO" for the search procedure, and `approval-gate` skill → `verify-qa-mode` task → Step 2.5 for the mandatory search step.** **AUTHORITY: `020-go-prohibitions.md` §1** (this line is a reference only)

______________________________________________________________________

**Search guidelines:** Use `srclight_search_symbols` or `grep` to find relevant guidelines.
