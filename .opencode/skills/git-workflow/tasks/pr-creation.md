# Task: pr-creation

## Purpose

Create pull request after explicit user instruction. Squash commits to single commit, push branch, create PR targeting `dev` branch (three-branch workflow: feature → dev → main).

## Operating Protocol

1. **User-initiated only:** This task runs when user says "create a PR" or similar
2. **Squash to single commit:** ALL implementation commits combined into ONE clean commit
3. **Target `dev` branch:** Feature PRs merge to `dev` (not directly to `main`)
4. **HALT after PR creation:** Wait for human to merge

## Entry Criteria

- User says "create a PR", "make a PR", "push and create PR", or similar
- Implementation is complete
- Developer has reviewed changes via compare URL

## Procedure

### Step 1: Verify PR Instruction (MANDATORY FIRST)

**🚫 CRITICAL: This is an ENFORCEMENT GATE, not just documentation.**

**If ANY check fails → STOP and report. DO NOT proceed.**

#### Enforcement Gate (MUST PASS ALL)

**Before creating ANY PR, verify ALL conditions:**

```
□ Condition 1: Explicit PR instruction detected
  - "create a PR", "make a PR", "push and create PR", "let's get a PR up"
  - Implementation complete alone does NOT satisfy this check
  
□ Condition 2: review-prep was completed
  - Compare URL was generated and reported in chat
  - Developer had opportunity to review via GitHub diff
  
□ Condition 3: Branch was pushed to remote
  - git branch -vv shows [origin/branch]
  - Compare URL will work correctly
  
If ANY condition NOT satisfied → STOP and report.
```

#### PR Instruction Verification

1. **Check for PR instruction:**

   **Valid PR instructions (PROCEED):**

   - "create a PR"
   - "make a PR"
   - "push and create PR"
   - "let's get a PR up"
   - "open a PR"
   - "create pull request"
   - "pr" (shorthand)

   **What does NOT authorize PR creation (HALT):**

   | Phrase | Reason |
   | -- | -- |
   | "approved" | Authorizes implementation ONLY, NOT PR creation |
   | "go" | Authorizes implementation ONLY, NOT PR creation |
   | Implementation complete | Does NOT authorize PR - wait for explicit instruction |
   | "continue" | Ambiguous - could mean next phase |
   | "proceed" | Ambiguous - could mean next task |
   | "fix the skill and guideline" | Implementation instruction, NOT PR instruction |

2. **Authorization scope table:**

   | Authorization | What It Authorizes |
   | -- | -- |
   | `approved` / `go` | Implementation ONLY |
   | `approved: X.Y` | Phase X.Y ONLY |
   | Implementation complete | NOTHING - wait for "create a PR" |
   | `create a PR` | PR creation workflow |
   | `create pull request` | PR creation workflow |

3. **Enforcement matrix:**

   | Scenario | Action |
   | -- | -- |
   | User says "create a PR" | ✅ PROCEED with PR creation |
   | User says "approved" only | ⛔ HALT - "approved authorizes implementation, not PR. Wait for 'create a PR' instruction." |
   | Implementation complete, no PR instruction | ⛔ HALT - report completion, wait for PR instruction |
   | User asks "ready for PR?" | ⛔ HALT - question, not instruction |
   | User says "fix X" (implementation only) | ⛔ HALT - implementation instruction, not PR instruction |

#### Verification Checklist

**BEFORE creating PR, confirm:**

```
✅ Explicit "create a PR" instruction present
✅ review-prep completed (compare URL reported)
✅ Developer had chance to review
✅ Branch pushed to remote
✅ Changelog generated OR [skip changelog] directive present
✅ Ready to squash and create PR
```

**If ANY checkbox unchecked → STOP and report what's missing.**

### Step 1.5: Check Existing PR State (MERGED PR HANDLING)

**🚫 CRITICAL: This check MUST happen BEFORE squashing or creating PR.**

This step handles the edge case where a PR already exists for the branch.

#### Step 1.5a: Check for Existing PR

Query GitHub API to check if a PR already exists for this branch:

```python
# Get current branch name
branch_name = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()

# List PRs for this branch
prs = github_list_pull_requests(
    owner=GIT_OWNER,
    repo=GIT_REPO,
    state="all",  # Include open, closed, merged
    head=f"{GIT_OWNER}:{branch_name}"
)
```

**If NO existing PR found:**

- Proceed to Step 2 (Changelog Generation)
- This is a new PR

**If PR EXISTS:**

- Continue to Step 1.5b to check PR state

#### Step 1.5b: Check PR State (open/merged/closed)

```python
pr = prs[0]  # Take first (most recent) PR
pr_state = pr.get("state")  # "open", "closed"
merged_at = pr.get("merged_at")  # Timestamp if merged, None otherwise
```

**PR State Decision Matrix:**

| State | merged_at | Action |
| -- | -- | -- |
| open | None | ✅ **UPDATE EXISTING PR** - Push new commits, existing PR updates automatically |
| closed | None | ⚠️ **Check close reason** - May be draft closed, proceed with caution |
| closed | timestamp | 🔄 **MERGED PR DETECTED** - Go to Step 1.5c |
| open | timestamp | ❌ **INVALID STATE** - Report error, HALT |

#### Step 1.5c: Handle Merged PR (MANDATORY HALT POINT)

**If PR is already merged:**

1. **Rebase branch on main:**

   ```bash
   git fetch origin
   git rebase origin/dev
   ```

2. **Check for remaining changes:**

   ```bash
   git diff origin/dev
   ```

3. **Decision:**

   | Remaining Changes | Action |
   | -- | -- |
   | Has differences | Create NEW PR for additional work |
   | No differences | HALT - branch already merged, no new PR needed |

4. **HALT with appropriate message:**

**If branch has remaining changes:**

```
🔄 MERGED PR DETECTED - Creating New PR

The existing PR #{pr_number} was merged to main.

Branch has been rebased on dev and contains new changes:
- Rebased commits: {commit_count}
- New PR will be created for additional work

Proceeding with new PR creation...
```

**If branch is already merged (no remaining changes):**

```
✅ BRANCH ALREADY MERGED

The branch '{branch_name}' has already been merged via PR #{pr_number}.

Current state:
- Branch is up-to-date with origin/dev
- No additional changes to merge

No new PR needed. The work from this branch was already incorporated.

**Action:** Consider deleting the local branch if no further work is needed.
  git checkout dev
  git branch -d {branch_name}
```

#### ⚠️ Edge Cases

**Branch ahead of main after merge:**

- Developer added commits after PR merged
- Create new PR for continuation work
- New PR title should reflect continuation

**Branch behind main after merge:**

- Rebase will fast-forward
- Check for remaining changes after rebase

**Conflicts during rebase:**

- HALT and report conflicts
- Provide guidance on resolution
- Suggest manual intervention

### Step 1.5d: Check for Merge Conflicts (CONFLICT DETECTION)

**🚫 CRITICAL: This check MUST happen BEFORE squashing or creating PR.**

This step detects merge conflicts in the PR and handles them appropriately.

#### Step 1.5d.1: Check GitHub PR Mergeable State

For OPEN PRs, check the `mergeable` attribute from GitHub API:

```python
# For existing open PRs
if pr_state == "open":
    pr_details = github_pull_request_read(method="get", owner=GIT_OWNER, repo=GIT_REPO, pullNumber=pr_number)
    mergeable = pr_details.get("mergeable")  # True, False, or None
    mergeable_state = pr_details.get("mergeable_state")  # "clean", "dirty", "unknown", etc.
```

**Mergeable State Matrix:**

| mergeable | mergeable_state | Meaning | Action |
| -- | -- | -- | -- |
| True | "clean" | No conflicts | ✅ Proceed with PR creation |
| True | "has_hooks" | No conflicts + hooks | ✅ Proceed (hooks run on merge) |
| False | "dirty" | Merge conflicts | 🔄 **CONFLICTS DETECTED** - Go to Step 1.5d.2 |
| None | "unknown" | GitHub checking | ⏳ Wait and retry, or check locally |
| False | "blocked" | Blocked by branch protection | ⚠️ Report blocker, HALT |

#### Step 1.5d.2: Handle Merge Conflicts (MERGED PR HANDLING)

**If PR has merge conflicts (mergeable=False, mergeable_state="dirty"):**

1. **Fetch conflict files:**

   ```bash
   git fetch origin
   git log --oneline origin/dev..HEAD  # See commits to be merged
   ```

2. **Get conflict files from GitHub API:**

   ```python
   # GitHub doesn't provide conflict files directly via API
   # Local check required:
   result = subprocess.run(['git', 'merge', '--no-commit', '--no-ff', 'origin/dev'], capture_output=True)
   if result.returncode != 0 and "CONFLICT" in result.stderr:
       # Conflicts detected
       conflict_files = subprocess.check_output(
           ['git', 'diff', '--name-only', '--diff-filter=U'],
           text=True
       ).strip().split('\n')
   ```

3. **Classify conflicts (AI-objective vs AI-subjective):**

**AI-Objective Conflicts (Auto-Resolve):**

| Conflict Type | Auto-Resolution Strategy |
| -- | -- |
| Import statement changes | Take both import sets |
| Whitespace/formatting | Apply consistent formatting |
| Same function moved to different location | Use new location |
| Additive changes (both sides add, no overlap) | Take both additions |
| Configuration file additions | Merge sections |

**AI-Subjective Conflicts (Request User Input):**

| Conflict Type | Why Subjective | HALT Action |
| -- | -- | -- |
| Logical/behavioral conflicts | Different implementations | Request clarification |
| Deleted file vs modified file | Need design decision | Request decision |
| Architectural changes | Multiple valid approaches | Request approach choice |
| Unclear intent | Both sides modify same logic | Request which version |

4. **Resolution Flow:**

**For AI-objective conflicts:**

```bash
# Auto-resolve
git checkout --ours <file>   # or --theirs, or merge manually
git add <resolved_files>
```

**For AI-subjective conflicts:**

````
🚫 MERGE CONFLICTS DETECTED - User Input Required

The following conflicts need your decision:

**File:** src/file.py
**Conflict:** Lines 42-50
**Type:** AI-subjective (behavioral conflict)
**Description:** Both branches modified the authentication logic differently

**Your branch:**
```python
def authenticate(user):
    return validate_token(user.token)
````

**Main branch:**

```python
def authenticate(user):
    return check_session(user.session_id)
```

**Please specify which approach to use:**

1. Keep your branch's version: `git checkout --ours src/file.py`
2. Use main's version: `git checkout --theirs src/file.py`
3. Provide custom resolution

**Files with conflicts:**

- src/file.py (AI-subjective)
- src/other.py (AI-objective - auto-resolved)

Resolution command: `git checkout --{ours|theirs} src/file.py`
Then: `git add src/file.py src/other.py`

````

5. **After resolution:**
```bash
# Continue with rebase
git rebase --continue
# Or abort if unrecoverable
git rebase --abort
````

#### ⚠️ Edge Cases

**All conflicts AI-objective:**

- Auto-resolve all
- Continue with PR creation
- Post comment noting resolution

**All conflicts AI-subjective:**

- HALT with full conflict list
- Request user decision for each
- Do NOT proceed without resolution

**Mixed objective/subjective:**

- Auto-resolve objective conflicts
- List subjective conflicts
- HALT for subjective decisions

**Unable to classify:**

- HALT with conflict details
- Request user inspection
- Do NOT assume subjective/objective

### Step 2: Changelog Generation (MANDATORY FOR ALL PLATFORMS)

**⚠️ CRITICAL: This step EXECUTES the changelog-generator skill as a sub-task.**

**Platform-Agnostic Requirement:**

Changelog generation is MANDATORY for ALL PRs - GitHub, GitBucket, or any other platform. There are NO platform-specific exemptions.

The skill MUST run as a sub-task to ensure context isolation - the main session will only see the final result, not the intermediate analysis.

#### Step 2.1: Check Skip Directive

Before invoking the skill, check for `[skip changelog]` in:

- Last commit message (if squashing multiple commits)
- PR title

If `[skip changelog]` is present, proceed directly to Step 3 (skip changelog generation).

#### Step 2.2: Execute Changelog Sub-Task (MANDATORY EXECUTION)

**EXECUTE THIS COMMAND AS A SUB-TASK:**

```
/skill changelog-generator --since-last-release
```

**Why This Is Critical:**

- Sub-task execution isolates the skill's thinking from main context
- Prevents skill output from consuming main session context window
- Skill runs in its own context and writes CHANGELOG.md
- Main context receives minimal confirmation only

**Expected Result:**

- Skill analyzes commits since last release
- Skill categorizes changes (added, changed, deprecated, fixed, security)
- Skill generates user-facing changelog entries
- Skill writes CHANGELOG.md to filesystem
- Main context sees: "Changelog generated successfully" or similar confirmation

#### Step 2.3: Stage Changelog Changes (MANDATORY)

After the sub-task completes, stage the changelog:

```bash
git add CHANGELOG.md
```

**CRITICAL:** This happens BEFORE the squash in Step 3, ensuring changelog changes are included in the single commit.

#### Step 2.4: Verify Changelog Staged (ENFORCEMENT GATE)

**BEFORE proceeding to Step 3, verify changelog was actually staged:**

```bash
# Check if CHANGELOG.md is staged (M = modified in index)
git status --porcelain CHANGELOG.md
```

**Expected Result:**

- `M CHANGELOG.md` OR `A CHANGELOG.md` (staged for commit)
- OR `[skip changelog]` directive was present (proceed to Step 3)

**If changelog NOT staged and NO skip directive:**

```
⛔ ENFORCEMENT GATE FAILED: Changelog not staged

The changelog-generator skill was invoked but CHANGELOG.md is not staged.

Diagnostic checklist:
□ Did Step 2.2 execute the skill?
□ Did Step 2.3 stage the result?
□ Is [skip changelog] directive present?

Resolution:
1. Run: /skill changelog-generator --since-last-release
2. Run: git add CHANGELOG.md
3. Verify: git status --porcelain CHANGELOG.md
4. Expected: "M CHANGELOG.md" appears
5. Continue to Step 3

If skipping changelog, ensure [skip changelog] is in commit message or PR title.
```

**Why This Check Exists:**

PRs #109, #114, #118, #119, #120 merged without changelog updates because Step 1 Enforcement Gate passed, Step 2 documented the changelog generation, but nothing verified the changelog was actually staged before squash.

This checkpoint ensures:

1. Skill invocation (Step 2.2) actually happened
2. Staging (Step 2.3) actually happened
3. Changelog changes ARE in the squash commit

#### Context Isolation Benefits

| What Happens in Sub-Task | What Returns to Main Context |
| -- | -- |
| Git commit analysis | Minimal confirmation only |
| Commit categorization | NOT: intermediate reasoning |
| Technical → User-friendly translation | NOT: commit details analyzed |
| Noise filtering | NOT: generated text |
| Context consumed by sub-task | Minimal result only |

Then continue to Step 3 (squash).

### Step 3: Squash to Single Commit

**Squash strategy depends on branch type:**

| Branch Type | Squash Strategy |
| -- | -- |
| **Single-issue branch** | All commits squashed to ONE commit |
| **Batch branch** | One commit per implementation item (N commits is correct) |

#### Single-Issue Branch (Default)

Squash ALL implementation commits into ONE clean commit:

```bash
git reset --soft origin/dev
git commit -m "<descriptive message>" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"
```

#### Batch Branch

A batch branch already has one squash-merged commit per implementation item from `assemble-batch`. These commits are correct — do NOT squash them further.

**Detect batch branch:** If the branch was created by `assemble-batch` (branch name typically starts with `batch/` or the batch state file exists at `.opencode/tmp/batch-*.md`), it is a batch branch with correctly-structured commits.

**For batch branches, skip squash.** The commit history from `assemble-batch` is the intended final state.

**Verify batch branch commits:**

```bash
# Check if batch state file exists
ls .opencode/tmp/batch-*.md 2>/dev/null

# If exists, this is a batch branch — skip squash
# If not exists, treat as single-issue branch — squash to one commit
```

### Step 3.5: Rebase on Current Dev (MANDATORY)

After squashing and before pushing, re-verify the branch is on top of current `dev`:

```bash
git fetch origin
git rebase origin/dev
```

**Why this matters:**

- Another agent may have merged a PR into `dev` between review and PR creation
- The squash commit must be based on the current `dev` tip, not a stale one
- Prevents the PR from having unexpected merge conflicts or stale base

**If conflicts occur during rebase:**

1. HALT and report conflicts to the developer
2. List the conflicting files
3. Request resolution — the developer must decide how to proceed
4. After resolution, re-run squash if needed, then retry push

**This step is MANDATORY.** Even if the review-prep rebase just ran, `dev` may have been updated since.

**For worktree-based branches:** The rebase runs inside the worktree directory. The `origin/dev` reference is shared across all worktrees, so `git fetch origin` and `git rebase origin/dev` work correctly from any worktree.

### Worktree Mode (MANDATORY — NO EXCEPTIONS)

All feature branches operate in worktrees. There is no alternative — worktree is the only method.

If `WORKTREE_PATH` is not set or empty: **FATAL ERROR → FLAG DEV → HALT.** Do not proceed without a valid worktree path.

1. All `bash` tool calls MUST use `workdir="{{WORKTREE_PATH}}"`
2. All `read`/`edit`/`write`/`glob`/`grep` tool calls MUST prefix `filePath`/`path` with `{{WORKTREE_PATH}}/` — these tools have NO `workdir` parameter and resolve relative paths against the main repo
3. Before any push/squash/rebase operation, verify:
   ```bash
   git branch --show-current
   # MUST match BRANCH_NAME
   ```
4. `git rev-parse --show-toplevel` MUST return the worktree path
5. NEVER operate in the main working directory during implementation
6. `origin/dev` may have moved since worktree creation (due to parallel PR merges) — always rebase on current `origin/dev`
7. If conflicts arise from `dev` movement, invoke `conflict-resolution` skill

### Step 4: Push to Remote

```bash
git push --force-with-lease origin <branch>
```

### Step 5: Collect Sub-Issues (Multi-Task Specs)

**For specs with sub-issues:**

```python
# Fetch all sub-issues for the parent issue
sub_issues = github_issue_read(method="get_sub_issues", issue_number=<parent>)

# Build autoclose list: parent + all sub-issues
autoclose_issues = [<parent>] + [sub["number"] for sub in sub_issues]
```

**For single-task specs:**

No sub-issues needed. Include only parent issue.

**⚠️ CRITICAL: Sub-issues are closed by the platform, NOT by the agent.**

- The "Fixes #N" annotation in PR body triggers automatic closure
- Agent does NOT manually close sub-issues after implementation
- Agent does NOT close sub-issues after PR creation
- Agent verifies closure AFTER PR merge via GitHub API
- Only in edge case (platform fails) does agent manually close

### Step 6: Create PR (Platform-Agnostic)

**Detect platform from session init (`GIT_PLATFORM`) and use appropriate tool:**

**Three-Branch Workflow Target:**

- Feature branches PR to `dev` (staging/integration)
- Releases PR from `dev` to `main` (human-triggered, not by AI)
- Hotfixes PR to both `dev` and `main` (paired issues)

#### GitHub (GIT_PLATFORM=github)

```python
github_create_pull_request(
    owner=GIT_OWNER,
    repo=GIT_REPO,
    title="[SPEC] <description>",
    body="""**Summary:**

<1-2 sentences describing the impact and stakeholder value>

**Outcome:** <What changed for stakeholders>

Fixes #<parent>
Fixes #<child1>
Fixes #<child2>
...
""",
    head=branch_name,
    base="dev"  # Three-branch workflow: feature → dev
)
```

#### GitBucket (GIT_PLATFORM=gitbucket)

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()
pr = api.create_pull_request(
    owner=GIT_OWNER,
    repo=GIT_REPO,
    title="[SPEC] <description>",
    body="""**Summary:**

<1-2 sentences describing the impact and stakeholder value>

**Outcome:** <What changed for stakeholders>

Fixes #<parent>
Fixes #<child1>
Fixes #<child2>
...
""",
    head=branch_name,
    base="dev"
)
```

**PR Body Requirements:**

- Must include `Fixes #<issue-number>` for autoclose
- Include ALL sub-issues for multi-task specs
- **MUST use executive summary format** (see Critical Violation: Wrong PR Body Format in `000-critical-rules.md`)
- `Summary:` section — 1-2 sentences describing stakeholder value and business impact (NOT implementation details)
- `Outcome:` section — what changed for stakeholders
- `Fixes #N` annotations at the bottom
- Target branch is `dev` for feature work

**⚠️ CRITICAL: PR Body Must Use Executive Summary Format**

The PR body MUST follow the executive summary format, matching the chat output and issue comment format:

```
**Summary:**

<1-2 sentences describing the impact and stakeholder value — NOT implementation details.>

**Outcome:** <What changed for stakeholders>

Fixes #<parent>
Fixes #<child1>
...
```

**❌ WRONG (Implementation Details):**

```
Add plan-fidelity-auditor skill as the first auditor in the mandatory audit chain. It generates independent clean-room plans from problem statements and compares them against existing spec plans to identify substantive gaps.
```

**✅ CORRECT (Executive Summary):**

```
**Summary:**

Ensures specs are audited for plan fidelity before implementation, catching missing phases and scope misalignment early.

**Outcome:** Developers will catch spec quality issues before code changes begin.

Fixes #505
```

### Step 7: Report PR URL and HALT

### ⚠️ CRITICAL: PR URL Reporting is MANDATORY

**You MUST report exec summary + PR URL in chat:**

```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

**PR URL:** ${BASE_URL}${GIT_OWNER}/${GIT_REPO}/pull/<number>

Wait for human to merge.
```

**Format Requirements:**

- Executive summary FIRST (provides context)
- PR URL LAST (clickable link)
- MUST include "Wait for human to merge"

### What If PR Creation Fails?

| Failure Reason | Response |
| -- | -- |
| No commits between branches | Report: "Branch has no commits to main. Changes may already be merged. Verify and HALT." |
| Branch conflicts | Report: "Branch conflicts with main. Rebase and push, then create PR." |
| GitHub API error | Report error details and HALT |

### Post-PR Creation Checklist

- [ ] Exec summary posted in chat
- [ ] PR URL posted in chat
- [ ] HALT — waiting for human merge

**🚫 NEVER:** Skip reporting PR URL, merge PR, or proceed without developer confirmation.

## Review Phase (Mandatory)

After implementation completes and BEFORE PR creation authorization:

1. **Agent pushes feature branch** to remote:

   ```bash
   git push -u origin <branch-name>
   ```

2. **Agent reports compare URL in CHAT ONLY** (NEVER to GitHub Issues):

   - URLs go in chat dialog ONLY
   - GitHub Issues receive completion comment WITHOUT URL

3. **Developer reviews changes** via GitHub diff viewer

4. **Developer decides** whether to create PR or request changes

5. **If satisfied, developer says** "create a PR"

6. **Agent creates PR** (squash, push, create PR, HALT)

**Why This Matters:**

- URLs in chat keep conversations clean
- Issues remain focused on task tracking, not URLs
- Developer can review changes before PR exists
- Clear separation between "implementation done" and "PR requested"

## PR Requirements

- Reference issue: `Fixes #123` in PR description
- Pass CI checks
- **Human review required** — Copilot review is supplemental, not sufficient for merge

## Skill Execution (Mandatory)

**When a skill is invoked, EXECUTE it, not just read it.**

| Wrong Behavior | Correct Behavior |
| -- | -- |
| Load skill content | Load skill content |
| Read the content | READ AND EXECUTE each step |
| Halt without action | Follow procedural steps |
| Report completion without doing work | Complete workflow then report |

**Correct Behavior:**

User says "pr merged" → Agent invokes /skill git-workflow → Agent EXECUTES cleanup task → HALT

**Why This Matters:**

- Skills encapsulate procedural knowledge
- Loading ≠ Executing
- The workflow must be followed, not just understood
- Halt happens AFTER execution, not during

## Agent Merge Prohibition

**🚫 ABSOLUTE PROHIBITION: AGENTS MUST NEVER MERGE PRs**

- **PR merging is HUMAN-ONLY.** The agent MUST NOT call `github_merge_pull_request` at any time.
- **ALL PRs require human review before merge** — no exceptions, no self-merging.
- **"go" does NOT authorize merging.** "go" means "proceed to the next task or phase" — NOT "merge the PR".
- After PR creation, the agent MUST report the PR URL and HALT.
- If PR is open and user says "go", the agent must clarify that merging requires explicit "merge" instruction.

## Enforcement Mechanisms

| Layer | Mechanism | Scope | Bypassable? |
| -- | -- | -- | -- |
| **Local** | `.githooks/pre-commit` | Blocks commit to main/master/dev | No |
| **Local** | `.githooks/post-commit` | Warns after commit to main/master/dev | N/A (post) |
| **GitBucket** | Branch protection rules | Requires PR for dev/main | No |

**There is NO emergency bypass.** If you need to make an urgent fix:

1. Create a hotfix worktree: `git worktree add .worktrees/hotfix-urgent-fix -b hotfix/urgent-fix dev`
2. Make your changes and commit
3. Push and create PR with `hotfix` label (targeting `dev`)
4. Request expedited review

## Recovery from Accidental Protected Branch Commit

If you somehow committed to `main`, `master`, or `dev` locally (hooks not installed):

```bash
# Create recovery branch from the commit
git branch feature/recovery HEAD

# Reset protected branch to match remote
git checkout dev  # or main/master
git reset --hard origin/dev  # or origin/main/origin.master

# Switch to recovery branch
git checkout feature/recovery

# Push and create PR (targeting dev)
git push origin feature/recovery
```

## Common Issues

| Issue | Resolution |
| -- | -- |
| Multiple commits (single-issue branch) | Run `git reset --soft origin/dev` and re-commit |
| Multiple commits (batch branch) | Expected — N commits = N implementation items. Do NOT re-squash. |
| PR body missing Fixes | Verify sub-issues, add all to body |
| Branch conflicts | Rebase on dev: `git rebase origin/dev` |
| Wrong base branch | Close PR, create new one with `base="dev"` |

## Co-Author Trailers (MANDATORY)

Every squash commit MUST include:

1. AI Author trailer
2. Human Collaborator trailer

**AI Trailer Format:**

- Use dynamic model detection at runtime
- Format: `Co-authored-by: <AI-Name> (<model-id>) <noreply@example.com>`
- Example: `Co-authored-by: OpenCode (glm-5) <noreply@opencode.ai>`

**Human Trailer:**

- Use session values from the session-enforcement plugin
- `DEV_NAME`: Human's name
- `DEV_EMAIL`: Human's email
- Format: `Co-authored-by: <Human-Name> <human-email>`

## Sub-Issue Autoclose

| Spec Type | PR Body Format |
| -- | -- |
| Single-task | `**Summary:** <impact>\n\n**Outcome:** <stakeholder value>\n\nFixes #<parent>` |
| Multi-task | `**Summary:** <impact>\n\n**Outcome:** <stakeholder value>\n\nFixes #<parent>` AND `Fixes #<child>` for each sub-issue |
| Batch | `**Summary:** <impact>\n\n**Outcome:** <stakeholder value>\n\n## Batch Issues\n\nImplements #<issue1>\nImplements #<issue2>\n\nFixes #<parent1>\nFixes #<child1>\nFixes #<parent2>` |

**Example Multi-Task PR Body:**

```markdown
**Summary:**

Ensures specs are audited for plan fidelity before implementation, catching missing phases and scope misalignment early.

**Outcome:** Developers will catch spec quality issues before code changes begin.

Fixes #469
Fixes #470
```

**Example Batch PR Body:**

```markdown
**Summary:**

Unified five approved issues into a single batch implementation, eliminating forked execution paths.

**Outcome:** All approvals now follow one consistent workflow: sub-issue expansion → assemble-batch → batch branch → single PR.

## Batch Issues

Implements #660 — Add pre-implementation analysis task
Implements #662 — Fix batch branch squash verification
Implements #621 — Collapse executing-plans into divide-and-conquer

Fixes #660
Fixes #662
Fixes #621
```

## Common Issues

| Issue | Resolution |
| -- | -- |
| Multiple commits in PR | Run `git reset --soft origin/dev` and re-commit |
| PR body missing Fixes | Verify sub-issues, add all to body |
| Branch conflicts | Rebase on dev: `git rebase origin/dev` |
| Wrong base branch | Close PR, create new one with `base="dev"` |

## After PR Creation

1. Report PR URL
2. HALT — wait for human merge
3. Do NOT merge (human-only operation)
