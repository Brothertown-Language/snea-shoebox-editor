# CRITICAL RULES — Zero Tolerance Violations

**See AGENTS.md for the authoritative list of critical rules.**
**See `.opencode/guidelines/` for detailed rules.**

This file provides critical rules that must never be violated. Sections with full detail in dedicated guidelines are referenced here with one-line pointers — the referenced guideline contains the complete rule, enforcement matrix, and examples.

## Mandate Tiering

Not all "zero tolerance" rules carry the same weight. This document classifies rules into two tiers based on what is at stake when they are violated:

### Tier 1 — Non-Yielding Mandates (Safety-Critical)

These mandates protect the integrity of the codebase and repository. They **NEVER yield to developer authorization** — even if a developer says "approved" or "go", the agent MUST still comply with these rules.

| Mandate | Why Non-Yielding |
| -- | -- |
| Worktree required before file edits | Prevents corruption of main/dev working directory |
| No commits to `main` or `dev` | Branch protection is a repository integrity concern |
| Human-only merge | Agents must never merge PRs |
| No `/tmp/` usage — `./tmp/` only | Prevents system-level temp file leakage |
| Path rules in worktree context | Prevents silent file operation errors across worktrees |
| Sub-agents must receive `worktree.path` | Prevents sub-agents from mutating main repo |
| Human-only branch deletion | Unmerged branches must never be force-deleted by agents |
| Agents must never self-authorize | Authorization comes from developers, never from agent reasoning |

**"Zero tolerance" language in this file applies ABSOLUTELY to Tier 1 mandates.** There is no waiver, no override, no emergency bypass.

### Tier 2 — Authorization-Waivable Mandates (Process)

These mandates ensure disciplined workflow (spec-first, plan-before-implementation). They **CAN be waived by explicit developer authorization** ("approved" or "go") because the developer is accepting the risk of skipping process steps.

| Mandate | What Waiver Means |
| -- | -- |
| Spec before code | Developer authorization means "you may begin the process" — for complex work, still create a spec/plan; for clearly simple work (docs, runbooks, minor config), the developer's explicit authorization IS the process |
| Plan before implementation | Same as above — authorization authorizes the work, not necessarily every intermediate artifact |
| `needs-approval` label present | Explicit auth overrides this label per `010-approval-gate.md` |
| Sub-issue structure for multi-task plans | When developer authorizes a multi-task plan, sub-issue creation is auto-setup, not a separate gate |

**For Tier 2 mandates, developer authorization does NOT mean "skip the process entirely"** — it means "you may begin." For complex work (new features, behavioral changes), the spec/plan workflow still produces value even when authorization exists. For clearly simple work (documentation, runbooks, minor configuration edits), the developer's explicit authorization IS sufficient process — no separate spec/plan is required.

### Interaction Rule

When developer authorization conflicts with a mandate:

| Scenario | Resolution |
| -- | -- |
| Developer authorization + Tier 2 process mandate | Developer authorization wins — the work is authorized |
| Developer authorization + Tier 1 safety mandate | Safety mandate wins — must use worktree, must not commit to main/dev |
| No developer authorization + any mandate | Mandate holds — HALT and wait |

**See `010-approval-gate.md` → "Mandate Tiering Interaction" for the complete interaction semantics and examples.**

## Critical Violation: Worktree Bypass — Using stash+checkout Instead of Worktrees

**⚠️ Using `stash + checkout -b` instead of worktrees for ANY feature branch creation is a CRITICAL GUIDELINE VIOLATION.**

Worktrees are ALWAYS mandatory for feature branch creation. **See `using-git-worktrees` skill for the complete worktree creation procedure. See `060-tool-usage.md` §1-2 for tool priority hierarchy and path resolution rules.** **AUTHORITY: `060-tool-usage.md` §1-2** (this line is a reference only)

- 🚫 FORBIDDEN: `git checkout -b`, `stash + checkout`, operating in main working directory, ignoring `worktree.fatal=1`
- ✅ REQUIRED: `using-git-worktrees` skill for every feature branch; HALT if `worktree.fatal=1` or `worktree.path` empty

## Critical Violation: Skipping Git Pre-Check Before ANY Work

**⚠️ Working on files without checking git state is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Starting work without creating a worktree first; operating in main working directory; creating/editing files on `main` or `dev`
- ✅ REQUIRED: See `git-workflow` skill `--task pre-work` for mandatory worktree creation and environment verification

## Critical Violation: Relative File Paths in Worktree Context

**⚠️ Using relative paths with `read`/`edit`/`write`/`glob`/`grep` tools when `worktree.path` is set is a CRITICAL GUIDELINE VIOLATION.**

**See `060-tool-usage.md` §2 "Path Rules (ZERO TOLERANCE)" for the complete tool-by-tool table showing wrong vs correct path resolution, and the `using-git-worktrees` skill → "Tool Usage Compliance" section for worktree-specific guidance.** **AUTHORITY: `060-tool-usage.md` §2** (this line is a reference only)

- 🚫 FORBIDDEN: Relative paths with file operation tools when `worktree.path` is set; assuming tools respect `workdir`
- ✅ REQUIRED: Prefix ALL paths with `worktree.path` when in worktree context

## Critical Violation: Sub-Agents Ignoring Worktree Context

**⚠️ Sub-agents that modify the main repo instead of the worktree are a CRITICAL GUIDELINE VIOLATION.**

When a main agent is operating in a worktree and dispatches a sub-agent, the sub-agent MUST receive `worktree.path` in its dispatch context and use it as the base directory for ALL file operations and git commands.

- 🚫 FORBIDDEN: Spawning sub-agents without `worktree.path` when operating in a worktree; sub-agents that stage/commit to the main repo's working directory; skills that perform git or file operations without a "Worktree Mode" section
- ✅ REQUIRED: Pass `worktree.path` in ALL sub-agent dispatch prompts when set; sub-agents verify `git rev-parse --show-toplevel` matches `worktree.path` before mutating state; all new skills MUST include worktree awareness per `skill-creator` skill requirements

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

## Critical Violation: Skipping verification-enforcement During Content Generation

**⚠️ Generating content without invoking verification-enforcement is a CRITICAL GUIDELINE VIOLATION.**

**See `verification-enforcement` skill for the complete procedural workflow including section-based sub-agent dispatch, evidence artifact collection, unverified marker resolution, and escalation procedure.** **AUTHORITY: `verification-enforcement` skill** (this line is a reference only)

Content generation — producing specs, plans, runbooks, documentation, or correspondence (including emails and stakeholder communications) — must pass through the verification-enforcement gate before and after generation. This gate ensures that every factual claim in generated content is backed by evidence artifacts collected from live sources. Skipping the gate means content ships with unverified claims, which is the generative equivalent of reporting memory as verified. Correspondence and email drafting are not exempt from this gate — they are content-generating workflows that make factual claims about system state, project status, or completed actions, and those claims require the same live-source verification as specs and plans.

- 🚫 FORBIDDEN: Generating content without invoking `verification-enforcement --task verify` first; skipping the `revisit` task after generation; accepting sub-agent output without evidence artifacts; removing `⚠️ UNVERIFIED` markers without verification; treating verification-enforcement as optional for "small" content; treating email/correspondence drafting as exempt from the verification gate; claiming a task is "complete" or "done" in correspondence without live-verification tool calls confirming the claimed state
- ✅ REQUIRED: Invoke `verification-enforcement --task verify` before content generation (including emails and correspondence); invoke `verification-enforcement --task revisit` after self-review; require evidence artifacts for all factual claims; escalate unresolvable claims to the developer; verify claimed states against live data before asserting them in correspondence

## Critical Violation: Plan ≠ Execution — Treating Documentation as Evidence of Completion

**⚠️ Treating the existence of a runbook, plan, or set of instructions as evidence that the instructions were executed is a CRITICAL GUIDELINE VIOLATION.**

**See `verification-enforcement` skill → "Plan ≠ Execution Evidence Rule" for the complete rule, anti-pattern table, and evidence requirements.** **AUTHORITY: `verification-enforcement` skill Plan ≠ Execution Evidence Rule** (this line is a reference only)

A plan describes what should be done. Execution evidence confirms what was done. These are fundamentally different sources. Conflating them leads to correspondence hallucination — claiming tasks are complete based on the existence of instructions rather than live verification of the resulting state.

- 🚫 FORBIDDEN: Citing a runbook, checklist, or procedure document as evidence that a task was completed; asserting "DNS updated" because correction steps exist in a runbook; claiming "deployment complete" because CI configuration is present; writing "done" or "complete" in correspondence without live-verification tool calls confirming the claimed state
- ✅ REQUIRED: Verify claimed states against live data before asserting them in any content; use `dig`, `curl`, CLI queries, or other live-verification tools to confirm system state; collect evidence artifacts from live sources, not from procedural documentation; treat "there is a plan for X" and "X was executed" as distinct claims requiring distinct evidence

## Critical Violation: Acting on Resources Without Reading All Comments

**⚠️ Acting on a GitHub/GitBucket resource without reading ALL comments is a CRITICAL GUIDELINE VIOLATION.**

**See `067-context-completeness.md` for the complete rule, evidence requirements, staleness rule, single exchange window exception, and reading requirements per resource type.** **AUTHORITY: `067-context-completeness.md`** (this line is a reference only)

- 🚫 FORBIDDEN: Acting after reading only the issue body; reviewing PRs without reading comments; assuming "no new comments"; caching comment state
- ✅ REQUIRED: Read ALL comments before any action; show evidence of having read them; re-read before significant actions; use `github_issue_read` with `method=get_comments`

## Critical Violation: Skipping Post-Implementation Verification Skills

**⚠️ Failing to invoke `verification-before-completion` and `finishing-a-development-branch` after implementation is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Claiming complete without invoking verification skills; manually executing skill steps; skipping verification because "changes look correct"
- ✅ REQUIRED: See `verification-before-completion` skill `--task verify` for evidence requirements; `finishing-a-development-branch` skill `--task checklist` for branch readiness; `git-workflow` skill `--task review-prep` for post-implementation workflow; `git-workflow --task cleanup` Step 3.5 for dev sync verification gate before any branch deletion, worktree removal, or issue closure
- **`git-workflow --task cleanup` Step 3.5** — Dev sync verification gate before any branch deletion, worktree removal, or issue closure. Local dev HEAD MUST match origin/dev HEAD before proceeding.

## Critical Violation: Skipping review-prep After Implementation

**⚠️ Failing to invoke `review-prep` after implementation is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Marking complete without commit/push/URL; skipping review-prep for any reason; proceeding without URL in chat
- ✅ REQUIRED: See `git-workflow` skill `--task review-prep` for mandatory commit, push, compare URL, and HALT protocol

## Critical Violation: Skipping Post-Merge Cleanup

**⚠️ Failing to invoke `git-workflow --task cleanup` after confirming PR merge is a CRITICAL GUIDELINE VIOLATION.** The cleanup task is the sole mechanism for deleting merged branches, closing issues, and syncing the local dev branch. Skipping it leaves stale branches and open issues.

- 🚫 FORBIDDEN: Assuming cleanup is optional after PR merge; manually closing issues without running cleanup; leaving merged branches undeleted; skipping cleanup because "the work is done"
- ✅ REQUIRED: Invoke `git-workflow --task cleanup` after every confirmed PR merge; verify branch deletion and issue closure via cleanup task result; ensure local dev HEAD matches origin/dev before proceeding
- ✅ REQUIRED: `git-workflow --task cleanup` Step 2.7 performs hierarchical issue closure — this is the ONLY authorized closure mechanism when PRs merge to `dev` (GitHub autoclose is inert for non-main targets)

**See `git-workflow` skill → `cleanup` task for the complete post-merge workflow.** **AUTHORITY: `git-workflow/tasks/cleanup.md`**

## Critical Violation: Wrong Chat Output at Halt Points

**⚠️ Producing casual summaries at halt points instead of the mandatory format (exec summary → outcome → URL → byline) is a CRITICAL GUIDELINE VIOLATION.**

**URL Label Context:**

| Context | Label | URL Format |
| -- | -- | -- |
| Pre-PR (after push, before PR creation) | **Compare URL** | `compare/dev...<branch-name>` |
| Post-PR (PR has been created) | **PR URL** | `pull/<PR-number>` |

Using "Compare URL" after a PR has been created is a format violation — the label MUST be "PR URL" with the `pull/N` format. Using "PR URL" before a PR exists is also a format violation — the label MUST be "Compare URL" with the `compare/dev...` format. A **label-format mismatch** (e.g., "Compare URL" label paired with a `pull/N` URL, or "PR URL" label paired with a `compare/dev...` URL) is a critical violation regardless of context — the label and URL format MUST always correspond.

**URL Applicability:**

| Scenario | URL Required? | Action |
| -- | -- | -- |
| Branch pushed, compare URL generated | ✅ Yes | Include URL between outcome and byline |
| Issue URL available | ✅ Yes | Include issue URL between outcome and byline |
| No branch pushed, no URL exists | ❌ No | Omit URL element entirely; byline follows outcome directly |
| PR already created | ✅ Yes | Use PR URL label with `pull/<N>` format |

The URL element is CONDITIONAL: required when a branch has been pushed or an issue/PR URL exists, **omitted entirely when no relevant URL exists**. Including a URL when none is applicable is a STRUCTURE-VIOLATION (auto-fix: remove URL, reorder to summary → outcome → byline).

The format applies to ALL halt points where implementation is reported complete:

- **review-prep** after implementation
- **Sub-agent result reports** from divide-and-conquer dispatch
- **Phase boundary halts** (merge gates between phases)
- **Approval-gate post-implementation** reports
- **Work orchestration** reports (assemble-work Step 6)
- **Completion task** reports (approval-gate completion)
- **Any completion message** where the agent reports work done and halts

**Mandatory format (with URL):**

```
**Summary:**

<1-2 sentences describing impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

<Compare URL or Issue URL>

🤖 <AgentName> (<ModelId>) <status-icon> <status>
```

**Mandatory format (without URL — when no relevant URL exists):**

```
**Summary:**

<1-2 sentences describing impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

🤖 <AgentName> (<ModelId>) <status-icon> <status>
```

- 🚫 FORBIDDEN: Producing casual one-liner summaries at halt points; omitting any required element (summary, outcome, byline); wrong ordering (URL before summary, byline before URL); reporting missing elements after the fact instead of auto-fixing before output is sent; including a URL when no relevant URL exists; label-format mismatch (e.g., "Compare URL" with `pull/N` URL or "PR URL" with `compare/dev...` URL)
- ✅ REQUIRED: Verify chat output format before sending at every halt point; auto-fix missing or misordered elements before output is sent; summary first, outcome after summary, URL if relevant (omit if not), byline last; label and URL format MUST match context (pre-PR → "Compare URL" + `compare/dev...`; post-PR → "PR URL" + `pull/N`); each verification checkpoint MUST produce a tool-call artifact as evidence

**See `git-workflow` skill → "Chat Output Format (CRITICAL)" for complete format requirements and examples. See `approval-gate/tasks/post-implementation.md` Step 4.5, `approval-gate/tasks/completion.md`, `divide-and-conquer/tasks/assemble-work.md` Step 6, `finishing-a-development-branch/tasks/checklist.md` §Chat Output Format, and `git-workflow/tasks/review-prep.md` §Live Verification for the verification checkpoints.**

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
- ✅ REQUIRED: Extract `<gitbucket.html_url>` from session init; construct all URLs from that value; HALT if session init missing

## Critical Violation: Inferring GitHub Owner from File Paths/Usernames

**⚠️ Inferring GitHub owner from file paths or usernames is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Inferring owner from file paths, `$USER`, `git config user.name`, cached values; making GitHub MCP calls without session init values
- ✅ REQUIRED: Use `github.owner` and `github.repo` from session init for EVERY GitHub MCP call

## Critical Violation: Missing AI Co-Authored Attribution

**⚠️ Failing to include AI co-authored attribution is a CRITICAL GUIDELINE VIOLATION.** Applies to original AI-authored content, NOT copy-pasted content.

- **Requires attribution**: Python docstrings, READMEs, new repos, original docs
- **Exempt**: Standard licenses, copy-pasted code, auto-generated files, framework boilerplate, minor edits
- **Format**: `Co-authored with AI: <AgentName> (<ModelId>)`

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

## Critical Violation: Enforcement Test Updates — Guideline and Skill Changes Without Test Scenarios

**⚠️ Modifying guideline files or skill files without adding or updating corresponding enforcement test scenarios is a CRITICAL GUIDELINE VIOLATION.**

Guideline files (`.opencode/guidelines/*.md`) and skill files (`.opencode/skills/*/SKILL.md`, `.opencode/skills/*/tasks/*.md`) are enforcement-critical documents. A guideline without a test is a suggestion, not a rule. A skill without a test is documentation, not enforcement.

- 🚫 FORBIDDEN: Adding a critical violation section without an enforcement test that checks for it
- 🚫 FORBIDDEN: Adding a verification step to a skill without an enforcement test that validates it
- 🚫 FORBIDDEN: Creating a new guideline without an enforcement test that confirms its key sections exist
- 🚫 FORBIDDEN: Modifying a guideline or skill without updating the corresponding enforcement test
- 🚫 FORBIDDEN: Running `opencode-cli run` directly without the `with-test-home` wrapper
- ✅ REQUIRED: Every guideline/skill change comes with an enforcement test scenario
- ✅ REQUIRED: Add the test scenario FIRST (RED), then make the change (GREEN) — TDD for rules
- ✅ REQUIRED: Run `bash .opencode/tests/test-enforcement.sh` to verify
- ✅ REQUIRED: Use `bash .opencode/tests/with-test-home opencode-cli run '<message>'` for all opencode-cli testing
- ✅ REQUIRED: Clean up test homes after testing: `bash .opencode/tests/with-test-home --clean-all`

**See `080-code-standards.md` → "Enforcement Test Mandate" for the complete per-change TDD pattern. See `.opencode/tests/README.md` for the enforcement test template and usage guide.**

## Critical Violation: Hardcoded Identity Values in Skills and Guidelines

**⚠️ Hardcoding agent names, model IDs, developer names, developer emails, org names, repo names, or platform names in skill files, guideline files, task files, or any AI agent configuration is a CRITICAL GUIDELINE VIOLATION.**

All identity values MUST use placeholder tokens that are resolved at runtime from session init output. Hardcoded values become stale when models, agents, orgs, or repos change.

- 🚫 FORBIDDEN: `<specific-agent-name>` (e.g., `OpenCode`, `OpenCode Desktop`, `Claude`) in skill files, guidelines, or task files
- 🚫 FORBIDDEN: `<specific-model-id>` (e.g., `ollama-cloud/glm-5`, `claude-3-5-sonnet`) in skill files, guidelines, or task files
- 🚫 FORBIDDEN: `example-developer`, `example-dev-alias`, or any specific developer name/email in skill files, guidelines, or task files
- 🚫 FORBIDDEN: `example-org`, `example-repo`, or any specific org/repo name in skill files, guidelines, or task files
- ✅ REQUIRED: Use `<AgentName>`, `<ModelId>`, `<dev.name>`, `<dev.email>`, `<github.owner>`, `<github.repo>`, `<gitbucket.html_url>` placeholders everywhere
- ✅ REQUIRED: Skill-creator MUST validate that no hardcoded identity values appear in generated skill files
- ✅ REQUIRED: Spec-auditor MUST flag hardcoded identity values as STRUCTURE-VIOLATION auto-fix findings

**Applies to:** SKILL.md files, task/*.md files, guideline files, agent configuration files, code comments that serve as templates or examples.

**Exempt from placeholders (concrete values are OK):** Python source code runtime strings, test fixtures, historical changelog entries, repository URLs in examples that use `<github.owner>/<github.repo>` pattern.

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

Chat output order (mandatory): 1) Executive summary, 2) URL (if exists), 3) AI byline LAST — `🤖 <AgentName> (<ModelId>) <status-icon> <status>`

**See `issue-operations` skill for Issue comment requirements and the complete channel routing table.**

## Critical Violation: Ignoring Issue Comments

**⚠️ Failing to respond to user comments on GitHub Issues is a CRITICAL GUIDELINE VIOLATION.**

**MANDATORY: Read issue comments and respond publicly. See `issue-operations` skill → `comment` task → "Responding to User Comments (MANDATORY)".**

## Critical Violation: Sub-issue Structure Bypass — Multi-task Plans

**⚠️ Implementing a multi-task plan without sub-issues is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Implementing phases without sub-issue structure; assuming markdown checkboxes = tracking; creating step-level sub-issues
- ✅ REQUIRED: Sub-issues at PHASE level under the plan (not the spec); each linked via `github_sub_issue_write method=add`; auto-create as pre-implementation setup

**See `issue-operations` skill → `link-sub-issue` task for complete workflow including auto-create workflow and database ID requirement. Sub-issue verification is consolidated into `approval-gate --task verify-authorization` Step 5 as the single readiness check.**

## Critical Violation: Monolithic Implementation — Skipping Item Decomposition

**⚠️ Implementing multiple items in a single branch/commit without decomposition, or skipping the top-down → bottom-up → per-item TDD cycle, is a CRITICAL GUIDELINE VIOLATION.**

**See `091-incremental-build.md` for the complete discipline rules, scope classification, and per-item TDD cycle.** **AUTHORITY: `091-incremental-build.md`**

- 🚫 FORBIDDEN: Implementing multiple items in a single massive branch/commit without item-level decomposition
- 🚫 FORBIDDEN: Writing code before writing the enforcement test for that change (code-first pattern)
- 🚫 FORBIDDEN: Skipping item enumeration and dependency ordering in plans
- 🚫 FORBIDDEN: Batching items that should be separate into one implementation pass
- 🚫 FORBIDDEN: Merging changes where the enforcement test for those changes doesn't pass
- ✅ REQUIRED: Follow top-down decomposition → bottom-up design → per-item TDD cycle for ALL scopes
- ✅ REQUIRED: Each item has its own enforcement test (RED phase comes before GREEN phase)
- ✅ REQUIRED: Plans include item enumeration, dependency ordering, and acceptance criteria per item
- ✅ REQUIRED: Approval gate Step 4.5 verifies item decomposition exists before implementation proceeds

## Critical Violation: Stopping After Single Phase in Multi-Task Plan

**⚠️ Halting after completing a single phase of a multi-task plan is a CRITICAL GUIDELINE VIOLATION.** Plan approval cascades authorization to ALL sub-issues under the plan. Complete ALL phases, report ONCE, HALT ONCE.

**See `approval-gate` skill → "Multi-Task Plan Authorization" for complete cascade workflow and enforcement matrix.**

## Critical Violation: Sub-issue Closure Timing — ZERO TOLERANCE

**⚠️ Closing sub-issues before PR merge is a CRITICAL GUIDELINE VIOLATION.** Sub-issues are children of the plan, not the spec.

🚫 FORBIDDEN: Closing sub-issues after implementation but before PR merge; closing without verifying PR merge via GitHub API

**See `git-workflow` skill `--task cleanup` for complete post-merge verification and closure workflow.**

## Critical Violation: Assuming Closed Issues Are Verified — ZERO TOLERANCE

**⚠️ Assuming an issue is fully implemented or resolved based solely on its closed state — without verifying a merged PR and success criteria — is a CRITICAL GUIDELINE VIOLATION.** A closed GitHub issue does NOT guarantee the work was completed, merged, or verified.

- 🚫 FORBIDDEN: Skipping verification because an issue is "closed"
- 🚫 FORBIDDEN: Trusting `state: "closed"` as evidence of implementation without merged PR proof
- 🚫 FORBIDDEN: Classifying issues as "already implemented" based on closed state alone
- 🚫 FORBIDDEN: Autoclosing parent issues when sub-issues are closed without merged PR evidence
- 🚫 FORBIDDEN: Bypassing bug fix spec verification because the bug report is closed
- ✅ REQUIRED: Verify closed issues have merged PR evidence via `github_pull_request_read` before treating them as resolved
- ✅ REQUIRED: Check `state_reason` — `"not_planned"` means intentionally skipped, `"duplicate"` requires verifying the target, `"completed"` requires merged PR evidence
- ✅ REQUIRED: Use `approval-gate --task verify-closed-issue` to verify legitimate closure before skipping, autoclosing, or excluding from implementation
- ✅ REQUIRED: Use `approval-gate --task reconcile-issue-graph` to act on findings — auto-close verified-complete tickets, reopen verified-incomplete tickets

**See `approval-gate --task reconcile-issue-graph` for reconciliation after graph traversal. See `approval-gate --task verify-closed-issue` for the complete verification procedure. See `git-workflow` skill `--task cleanup` for pre-closure sub-issue verification gate.**

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

**See `issue-operations` skill `--task pre-creation` for the complete superseded/stale spec check procedure.**

- If superseding issue exists: SILENTLY HALT, report conflict, wait for direction
- If stale: REVISE spec, report revision, HALT for approval — never implement stale without revision

## Critical Violation: Main Agent Implements Directly

**⚠️ The main agent implementing files directly instead of dispatching to sub-agents is a CRITICAL GUIDELINE VIOLATION.**

**See `divide-and-conquer` skill `--task assemble-work` for the complete sub-agent dispatch workflow.**

- 🚫 FORBIDDEN: Main agent editing implementation files directly during work orchestration
- 🚫 FORBIDDEN: Bypassing assemble-work for single-issue dispatch
- 🚫 FORBIDDEN: Code-path divergence between single and work-order issue handling
- ✅ REQUIRED: All implementation dispatches through `assemble-work` — single issue is a work-of-1
- ✅ REQUIRED: Main agent only orchestrates — never edits implementation files
- ✅ REQUIRED: Context window stays clean for orchestration decisions

## Critical Violation: Bypassing Mandatory Skill Invocations During Implementation

**⚠️ Skipping mandatory skill invocations (git-workflow pre-work, divide-and-conquer, verification-before-completion) during the implementation workflow is a CRITICAL GUIDELINE VIOLATION.**

The approval-gate dispatch chain defines a mandatory sequence after plan approval:

1. `git-workflow --task pre-work` — Create worktree, set `worktree.path`, verify branch state
2. `divide-and-conquer --task assemble-work` — Dispatch sub-agents for implementation
3. `verification-before-completion` — Verify success criteria before marking complete
4. `finishing-a-development-branch --task checklist` — Final branch readiness check
5. `git-workflow --task review-prep` — Push branch, generate compare URL

**Each step is MANDATORY. Skipping any step is a CRITICAL VIOLATION.**

- 🚫 FORBIDDEN: Creating a worktree manually instead of invoking `git-workflow --task pre-work`
- 🚫 FORBIDDEN: Implementing files directly as the main agent instead of dispatching via `divide-and-conquer`
- 🚫 FORBIDDEN: Skipping `verification-before-completion` and claiming task completion without evidence
- 🚫 FORBIDDEN: Pushing changes without invoking `finishing-a-development-branch --task checklist`
- 🚫 FORBIDDEN: Generating compare URL without invoking `git-workflow --task review-prep`
- ✅ REQUIRED: Follow the approval-gate dispatch chain in order after plan approval
- ✅ REQUIRED: Invoke each mandatory skill in sequence
- ✅ REQUIRED: Verify `worktree.path` is set before any file modification
- ✅ REQUIRED: Use `divide-and-conquer` to dispatch sub-agents for all file modifications on multi-task plans

**See `approval-gate/SKILL.md` → "Dispatch Order" for the complete mandatory sequence. See `using-git-worktrees` skill → `create-worktree` task for worktree creation procedure.**

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

## Critical Violation: Symptom-Only Fix-Specs — Patches Without Root Cause Analysis

**⚠️ Creating fix-specs that address only the observed symptom without identifying and targeting the root cause is a CRITICAL GUIDELINE VIOLATION.**

Fix-specs exist to ensure bugs are fixed at their source, not patched at their surface. A symptom-only fix-spec proposes changes that mask the bug's effects without eliminating its cause — the bug will recur or manifest differently.

**See `issue-review` skill → `analyze-and-spec` task for the complete root cause analysis and fix spec creation workflow.** **AUTHORITY: `issue-review/tasks/analyze-and-spec.md`**

| Anti-Pattern | Root Cause Fix | Symptom-Only Patch (FORBIDDEN) |
| -- | -- | -- |
| Process gap: "just add the missing close call" | Add enforcement rule + enforcement test mandate | Add one line of code that closes the issue |
| Data corruption: query returns wrong results | Fix the query logic producing bad data | Filter out wrong results in the UI |
| State mismatch: stale cache serves old values | Invalidate cache on state change | Increase cache timeout |
| Missing validation: invalid input causes crash | Add input validation at the entry point | Catch the exception and return empty result |
| Missing step: workflow skips cleanup | Add mandatory cleanup step to the workflow | Close the issue manually without fixing the workflow |

- 🚫 FORBIDDEN: Creating fix-specs that patch symptoms without root cause analysis; closing bug reports with "add close call" patches that don't prevent recurrence; proposing tactical fixes that mask effects instead of eliminating causes
- ✅ REQUIRED: Use `issue-review --task analyze-and-spec` for root cause analysis before creating any fix spec; every fix spec MUST include a "Root Cause" section identifying the underlying cause; the "Fix Approach" section MUST target the root cause, not just the symptom; if root cause is unclear, HALT and request developer input per the smart checkpoint in `analyze-and-spec`

**Why this matters:** The entire purpose of the fix-spec workflow is to prevent recurring bugs. A symptom-only fix is the opposite — it closes the issue while leaving the root cause active, guaranteeing the bug will resurface. The `analyze-and-spec` task enforces root cause analysis as MANDATORY before any fix spec creation.

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

### Post-Dispatch Output Guarantee

After EVERY `task(subagent_type="general")` dispatch, the agent MUST produce output — never transition directly from dispatch to halt without output.

| After Dispatch | Agent MUST |
|----------------|-----------|
| Sub-agent returned valid result | Report result or proceed to next step (existing behavior, no change) |
| Sub-agent returned empty result | FALLBACK to inline execution + report warning in chat |
| Sub-agent returned error | FALLBACK to inline execution + report error in chat |
| Inline fallback also failed | Report double-failure + invoke `--task completion` + HALT with status message + byline |

| Violation Pattern | Classification |
|-------------------|----------------|
| Empty sub-agent result → zero output → silent halt | Critical: Silent Agent Termination |
| Empty sub-agent result → fallback attempt → status message in chat | Acceptable: self-corrected |
| Empty sub-agent result → inline succeeds → chain continues | Acceptable: self-corrected |
| Error sub-agent result → zero output → silent halt | Critical: Silent Agent Termination |

**This guarantee supplements the existing Silent Agent Termination rule by specifying the post-dispatch scenario explicitly.** The existing rule covers general halts; this adds the specific case where the agent dispatches a sub-agent, gets an empty result, and has no code path to recovery or reporting.

**See `020-go-prohibitions.md` for the complete halt requirements and `finishing-a-development-branch` skill for completion guarantees.** **AUTHORITY: `020-go-prohibitions.md`** (this line is a reference only)

## Critical Violation: Skipping Interdependency Analysis for Batch Approvals

**⚠️ Processing multiple approved issues without interdependency analysis is a CRITICAL GUIDELINE VIOLATION.**

**See `approval-gate` skill → `pre-implementation-analysis` task for the complete procedure, classification heuristics, and output format.**

- 🚫 FORBIDDEN: Processing issues one-by-one without analysis; assuming independence without checking; hiding analysis in reasoning
- ✅ REQUIRED: Invoke `pre-implementation-analysis` for all approvals (single or authorization set); expand sub-issues; classify each issue; build dependency graph; present analysis in chat; execute in dependency order

## Critical Violation: Treating Branch Stacking as Optional

**⚠️ Bypassing stacking discipline without justification is a CRITICAL GUIDELINE VIOLATION. Stacking is a prerequisite for code correctness, not a preference.**

- 🚫 FORBIDDEN: Treating stacking as a "default preference" that can be overridden for convenience
- 🚫 FORBIDDEN: Interpreting "independent issues" as "must be parallel" — independence ≠ parallelism
- 🚫 FORBIDDEN: Dispatching sub-agents in parallel when stacking is the appropriate approach
- 🚫 FORBIDDEN: Choosing parallel execution because it "saves time" without verifying circumstances genuinely allow it
- ✅ REQUIRED: Sequential branch stacking as the prerequisite execution model
- ✅ REQUIRED: Explicit documented justification in work state if parallel execution is chosen (opportunistic only)
- ✅ REQUIRED: Stack branches via `git merge <prior-branch>` into dependent branches before implementation
- ✅ REQUIRED: When in doubt, stack — parallel execution is never the starting assumption

## Critical Violation: Pipeline-Scoped Authorization with Hard HALT at Scope Boundary

**⚠️ Proceeding past the scope horizon specified in the authorization phrase is a CRITICAL GUIDELINE VIOLATION.**

When a user says "approved #N to PR" (or any pipeline-scoped phrase), authorization extends ONLY to the pipeline stage specified. Everything below is gap-filled and auto-approved; everything above is unauthorized.

- 🚫 FORBIDDEN: Proceeding past `halt_at` without re-authorization
- 🚫 FORBIDDEN: Creating a PR when `halt_at < pr_created`
- 🚫 FORBIDDEN: Implementing when `halt_at == plan_created`
- 🚫 FORBIDDEN: Treating pipeline scope as a "soft suggestion" rather than a hard wall
- ✅ REQUIRED: Parse authorization text for scope qualifiers (regex-based, priority order)
- ✅ REQUIRED: HALT at the specified pipeline stage and report completion
- ✅ REQUIRED: Pass `authorization_scope`, `halt_at`, and `pr_strategy` through the entire dispatch chain

**See `approval-gate` skill → "Authorization Scope Model" for the complete scope values, verb-prefix parsing table, and gap-fill actions.** **AUTHORITY: `approval-gate` skill Authorization Scope Model**

## Critical Violation: Unified Dispatch Path — No Single-Task Exemption

**⚠️ Bypassing the unified dispatch path for single-issue work is a CRITICAL GUIDELINE VIOLATION.**

Every authorization follows the same pipeline regardless of issue count: `verify-authorization → pre-implementation-analysis → divide-and-conquer/assemble-work → verification-before-completion → finishing-a-development-branch → git-workflow/review-prep`. There is no single-task exemption or separate code path.

- 🚫 FORBIDDEN: Skipping `divide-and-conquer/assemble-work` for single issues
- 🚫 FORBIDDEN: Implementing directly as the main agent for single issues
- 🚫 FORBIDDEN: Creating individual PRs for single issues in a work set (PR strategy is scope-dependent, not count-dependent)
- 🚫 FORBIDDEN: Bypassing any dispatch chain step for "small" or "simple" work
- ✅ REQUIRED: Dispatch single issues through `assemble-work` as work-of-1 (single sub-agent)
- ✅ REQUIRED: Use `authorization_scope` and `pr_strategy` to determine PR behavior, not issue count
- ✅ REQUIRED: Follow the complete dispatch chain for every authorization

**See `approval-gate` skill → "Unified Dispatch Path (Work-of-1)" and `divide-and-conquer` skill → `assemble-work` task for the complete dispatch procedure.**

## Simple Work Dispatch Path (Tier 2 Waiver)

When ALL of the following conditions are met:
- Developer has given explicit authorization (approved/go)
- Work is "clearly simple" (see classification table below)
- No spec or plan is required (Tier 2 waiver applies)
- File modifications ARE needed (Tier 1 worktree mandate applies)

The agent follows this REDUCED dispatch path:

1. `git-workflow --task pre-work` — Create worktree (Tier 1, MANDATORY)
2. Direct implementation in worktree — No sub-agent dispatch needed for single-file changes
3. `verification-before-completion` — Verify success criteria exist and pass
4. `finishing-a-development-branch --task checklist` — Branch readiness check
5. `git-workflow --task review-prep` — Push, generate compare URL, HALT

Steps SKIPPED for simple work:
- `verify-authorization` (Tier 2 waiver replaces this — authorization IS the process)
- `pre-implementation-analysis` (no plan to analyze)
- `divide-and-conquer/assemble-work` (single implementer, single concern)
- `verification-before-completion` can be simplified for documentation-only changes

### Classification: "Clearly Simple Work"

Work qualifies as "clearly simple" when ALL criteria are met:

| Criterion | Qualifies | Does Not Qualify |
|-----------|-----------|------------------|
| File count | ≤2 files | 3+ files |
| Behavioral change | None (docs, config, runbooks) | Any behavioral change |
| Architectural impact | None | Any impact on architecture |
| Existing code interaction | None (new files, minor edits) | Modified function signatures, APIs |
| Risk level | Zero rollback risk | Data loss, security, deployment risk |

When work does NOT qualify as "clearly simple", the full dispatch path applies regardless of developer authorization.

### Key Principle

"Simple" describes the PROCESS burden (no spec/plan needed), NOT the SAFETY mechanism. Worktrees protect repository integrity regardless of task complexity. The reduced dispatch path still enforces all Tier 1 mandates — it only skips Tier 2 process steps that are waived by developer authorization.

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
- 🚫 FORBIDDEN: "How should we handle this partially-implemented issue?" — scope-reduce and continue
- 🚫 FORBIDDEN: "Should we re-plan?" — yes, if authorization says "re-plan as needed"
- 🚫 FORBIDDEN: "How should we close this already-implemented issue?" — via verify-already-implemented or via referenced spec-fix
- 🚫 FORBIDDEN: "Should this be standard scope or for_implementation?" — the verb-prefix parsing table resolves this
- 🚫 FORBIDDEN: "What scope of authorization?" — the verb-prefix table is deterministic
- 🚫 FORBIDDEN: "Is this approved to PR or just to implementation?" — parse the phrase, don't ask
- 🚫 FORBIDDEN: Any question where the answer is determinable from context, codebase, or request analysis
- ✅ REQUIRED: Classify autonomously and state the classification as part of the design proposal
- ✅ REQUIRED: Only ask when multiple valid structures exist with genuinely ambiguous trade-offs (e.g., 3+ subsystems with unclear boundaries)
- ✅ REQUIRED: Authorization scope MUST be auto-resolved from the verb-prefix parsing table per the approval-gate skill → Authorization Scope Model

**See `brainstorming` skill → `explore` task → "Autonomous Structural Classification" for the complete criteria. See `approval-gate/tasks/pre-implementation-analysis.md` Step 0.15 for the classification decision table that maps screening results to autonomous actions. See `approval-gate/tasks/screen-issue.md` §"Autonomous Resolution" for the exhaustive `requires_developer: true` conditions.**

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

## Critical Violation: Sub-issue Linkage Verification — Phase Count Mismatch

**⚠️ `get_sub_issues` count MUST match plan body phase count before implementation proceeds. If counts don't match, block implementation and offer remediation via `issue-operations --task link-sub-issue`.**

**This enforcement point is `approval-gate --task verify-authorization` Step 5, specifically the phase-count cross-reference check (Step 5.2.1).** **AUTHORITY: `approval-gate/tasks/verify-authorization.md` Step 5.2.1** (this line is a reference only)

- 🚫 FORBIDDEN: Proceeding with implementation when a multi-task plan has fewer formal sub-issues than phases in its body; treating markdown headings as equivalent to formal sub-issue linkage; skipping the phase-count cross-reference check
- ✅ REQUIRED: Parse plan body for `### Phase N:` or `#### Task N:` heading patterns to count expected phases; compare count against `github_issue_read(method=get_sub_issues)` result count; if plan body has N > 1 phases and `get_sub_issues` returns fewer than N sub-issues, report STRUCTURE-VIOLATION and block implementation with a remediation offer to run `issue-operations --task link-sub-issue`
- ✅ REQUIRED: Single-task plans (0 or 1 phases expected) skip the count check and pass automatically

**See `020-go-prohibitions.md` §5 for multi-task plan sub-issue requirements.** **AUTHORITY: `020-go-prohibitions.md` §5** (this line is a reference only)

## Critical Violation: Inline Screening of Authorization Sets

**⚠️ The agent MUST ALWAYS dispatch `screen-issue` sub-agents for per-issue screening, regardless of approval set size. Loading issue bodies into the orchestrator's own context is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Fetching approved issue bodies into orchestrator context before sub-agent dispatch
- 🚫 FORBIDDEN: Running screening logic inline for ANY approval set size
- ✅ REQUIRED: Dispatch one `screen-issue` sub-agent for EVERY approved issue — no count threshold
- ✅ REQUIRED: Orchestrator receives only compact result contracts (≈100-500 words each)
- ✅ REQUIRED: Cross-issue merge and dependency graph built from result contracts, not raw issue bodies

**AUTHORITY:** `approval-gate/tasks/pre-implementation-analysis.md` Step -1

### Common Misconception: "Small approval sets can be screened inline"

**This is INCORRECT.** There is no inline screening path. Every approved issue — whether 1, 2, or 20 — MUST be screened by a `screen-issue` sub-agent dispatched via `task(subagent_type="general")`. The count threshold was removed because:

1. Inline screening creates a forked code path that agents exploit to skip sub-agents
2. Even a single issue can consume significant context (long spec, many comments, sub-issues)
3. Sub-agent dispatch has near-zero cost but guarantees consistent execution
4. The "context savings" of inline screening for ≤3 issues never materialized in practice

**DO NOT re-introduce a count threshold.** This is a structural invariant, not a performance optimization.

## Critical Violation: Silent Halt Without Prompt — No Spec/Plan Search Before Stopping

**⚠️ Halting silently when no spec/plan exists for an implementation request — without first searching GitHub Issues for candidates and presenting them — is a CRITICAL GUIDELINE VIOLATION.**

When an agent receives an implementation instruction but cannot find an associated spec or plan, it must actively search for existing candidates before halting. A silent halt with no search and no presentation of options is a process gap that treats missing documentation as the user's problem rather than an actionable finding.

- 🚫 FORBIDDEN: Halting silently without searching GitHub Issues; presenting no candidates when implementation authorization lacks a matching spec/plan; offering only "create a new spec" without checking for existing specs first
- ✅ REQUIRED: Search GitHub Issues for candidate specs/plans using label filters (`[SPEC]`, `[PLAN]`, `[SPEC-FIX]`) and keyword matching against the request target; present all candidates with URLs; offer create-or-select before halting; flag as FAILURE if no candidates found
- ✅ REQUIRED: When no candidate exists, the agent MUST present the failure state ("No existing spec/plan found for [topic]") before offering to create one

**Why this matters:** The current Q/A mode halt is passive — it stops work but doesn't help the user find existing tracking. Active search turns "no spec found" from a dead end into a decision point: "here are N existing issues that may match, which one (if any) did you mean?" This reduces duplicate spec creation and connects implementation requests to existing tracking.

**See `020-go-prohibitions.md` §1 "NEVER DO" and "ALWAYS DO" for the search procedure, and `approval-gate` skill → `verify-qa-mode` task → Step 2.5 for the mandatory search step.** **AUTHORITY: `020-go-prohibitions.md` §1** (this line is a reference only)

## Critical Violation: Non-Idempotent API Mutations

**⚠️ Creating duplicate resources through non-idempotent API mutations is a CRITICAL GUIDELINE VIOLATION.**

Any API mutation (PR creation, issue creation, branch creation) MUST be idempotent — check for existing resource before creating, handle "already exists" gracefully, never create duplicates through retry.

- 🚫 FORBIDDEN: Creating a PR without checking for existing open PR on the same head branch; retrying a mutation POST after the first call succeeded but response parsing failed; creating duplicate issues, branches, or releases without a pre-check
- ✅ REQUIRED: Before any mutation POST, check whether the resource already exists (e.g., `list_pull_requests(state='open')` before `create_pull_request`); if resource exists, return existing data — do NOT create duplicate; if creation call succeeded but parsing failed, the resource was created — report what happened, do NOT retry the POST

## Critical Violation: Inline Mutation Scripts

**⚠️ API calls that mutate state (POST, PUT, PATCH) inlined in `python -c '...'` strings are a CRITICAL GUIDELINE VIOLATION.**

API calls that mutate state must use the platform's dedicated API client (e.g., `gitbucket-api` CLI tool, GitHub MCP). If the client lacks the method, HALT — do NOT work around it with inline scripts. Shell interpolation corrupts inline Python, POST calls succeed but parsing crashes, and agents retry the entire call creating duplicates.

- 🚫 FORBIDDEN: `uv run python -c '...'` for any POST/PUT/PATCH operation; raw `requests.post()` / `requests.put()` / `requests.patch()` outside the dedicated API client; any inline script containing a mutation HTTP method
- ✅ REQUIRED: Use `./.opencode/tools/gitbucket-api create-pr`, `./.opencode/tools/gitbucket-api create-issue`, etc. for all GitBucket mutations; use GitHub MCP for GitHub mutations; if a needed command is missing, HALT and report the gap; use the tool's built-in error handling and response parsing

## Sub-Agent Extraction Pattern

All skill task dispatches follow a sub-agent-first paradigm. The main agent is a pure orchestrator that never loads task files directly — it dispatches every task via `task(subagent_type="general")` and receives compact result contracts. Each SKILL.md contains a "Sub-Agent Tasks" section with word-count context, result contract schemas, and dispatch context schemas. The main agent loads only SKILL.md files and reads compact result contracts (≈100-500 words), never loading task files directly.

- All tasks → sub-agent dispatch via `task(subagent_type="general")`
- Word counts in tables are for context estimation only, not dispatch selection
- Result contracts reference task files as source of truth (no duplication)
- Dispatch context MUST include `worktree.path`, `github.owner`, `github.repo`, `dev.name`, `dev.email`

**See each skill's SKILL.md → "Sub-Agent Tasks" section for word-count context and result contract schemas.**

______________________________________________________________________

**Search guidelines:** Use `srclight_search_symbols` or `grep` to find relevant guidelines.
