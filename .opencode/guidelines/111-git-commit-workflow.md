# Git Protocol: Commit Workflow

## 1. Commit Policy (User-Initiated Only)

### 🚫 NEVER DO
- **NEVER run `git restore`, `git checkout`, `git reset`, `git clean`, or any other git command that discards or modifies working tree state.**
- **NEVER discard uncommitted changes** — even if they appear to be formatting-only, unintended, or erroneous. Analysis commands are read-only.
- **NEVER commit or merge without direct instruction.** Commits and merges may ONLY be initiated by the developer as a direct instruction to the AI agent. Autonomously committing or merging is FORBIDDEN.
- **NEVER create a PR without direct instruction.** PRs require explicit developer request — the agent does NOT automatically create PRs after completing implementation. See `113-git-pr-workflow.md`.
- Agent MUST NOT create commit messages or scripts proactively (without user request).
- When asked to "prepare a commit" — see Section 2 for the mandatory script-based workflow.

### STOP ASKING FOR COMMITS AND PRS

The developer will say "commit" or "create a PR" when they want git operations. Until then, do nothing—no questions, no prompts:

1. **After completing implementation**: Report completion concisely, then STOP and wait silently
2. **Do NOT ask**: "Commit?", "Ready to commit?", "Should I commit?", "Ready for a PR?", "Create a PR?", "Push and PR?"
3. **Do NOT automatically create PRs**: PR creation requires the same explicit instruction as commits

### ✅ ALWAYS DO
- **Include co-author trailers for both AI and human collaborator.** Every implementation commit MUST include TWO trailers:
  - AI author: Use the AI's actual identity dynamically (the AI knows its own name)
  - Human collaborator: Use session-cached values from `000-session-init.md` §0.1 (`DEV_NAME`, `DEV_EMAIL`)
- Re-run discovery (`git status`, `git diff`) before any commit workflow.
- If `pyproject.toml` changed, include `uv.lock`.

### Co-Author Trailer Workflow

**⚠️ CRITICAL: AI Identity is DYNAMIC — NEVER copy the AI name from examples!**

The AI must use its **own identity**, not the example name. Examples show placeholders like `OpenCode` — the actual AI must substitute its own name/email.

**Step 1: Determine AI identity dynamically:**
- The AI uses its **own actual identity** (the AI knows its own name and email)
- **DO NOT use generic placeholders like "AI"** — use the actual AI agent name (e.g., "OpenCode Desktop", "OpenCode")
- **Email format**: Use a noreply address associated with the AI service (e.g., `noreply@opencode.ai`, `noreply@anthropic.com`)
- **NEVER use the project domain** (e.g., `ai@<project-domain>.com` is WRONG — those belong to the human collaborators)
- **MODEL INFO REQUIRED**: The AI MUST include the backing model name and size/provider in the co-author trailer:
  - Format: `Agent-Name (model-id) <email>`
  - Example: `Co-authored-by: OpenCode (glm-5) <noreply@opencode.ai>`

**Step 2: Use cached human identity from session start:**
- Human collaborator values are cached at session start via `000-session-init.md` §0.1
- `DEV_NAME`: Human's name (or `$USER` fallback)
- `DEV_EMAIL`: Human's email (or `$USER@$HOSTNAME` fallback)
- **Do NOT re-run `git config`** — use stored session values

**Step 3: Include BOTH trailers (MANDATORY):**
```bash
git commit -m "message" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"
```

---

## 2. Preparing Commits (Script-Based Workflow)

When asked to "prepare a commit" (or similar READ-ONLY phrase):

**Mandatory Steps:**
1. Run read-only commands: `git status`, `git diff`, `git diff --cached`, `git log`
2. Summarize the changes (grouped logically if multiple files)
3. **Create a shell script in `./tmp/`** containing the `git add` and `git commit` commands
4. **STOP** — do NOT run the script, do NOT run `git add` or `git commit`
5. Report the script path and proposed commit message for the user to review and execute

---

## 3. Reading Historical Content

### ✅ ALWAYS DO
- To inspect a file at a historical commit, use `git show <ref>:<path> > ./tmp/historical_file.ext`.
- Process the saved file with the appropriate `ai_bin/` or IDE tool.

### 🚫 NEVER DO
- Using `python3`, `python -c`, `json.tool`, `grep`, or `sed` to process `git show` output is a critical violation.

---

## 4. Lockfile Policy

- This repository is an application/CI repo — commit `uv.lock`.

---

## 5. WIP Commit Before HALT (MANDATORY)

**CRITICAL: Work-in-progress commits MUST be made before ANY HALT to prevent data loss.**

### Why WIP Commits Are Required

When implementation halts (for ANY reason), uncommitted changes are at risk:
- Session crashes
- Context window exhaustion
- Developer needs to switch branches
- Machine restarts
- Awaiting clarification/approval

WIP commits preserve work in progress in recoverable git history.

### When to Commit WIP

| Scenario | Commit Type | Message Format |
|----------|-------------|----------------|
| Task complete | Full commit | `[Phase N] Task description` |
| Phase complete | Full commit | `[Phase N] Phase complete` |
| Mid-task HALT | WIP commit | `WIP: Phase N - description` |
| Awaiting clarification | WIP commit | `WIP: Phase N - awaiting clarification` |
| Error encountered | WIP commit | `WIP: Phase N - error: description` |
| Session ending | WIP commit | `WIP: Phase N - session end` |

### WIP Commit Workflow

**Before ANY HALT (awaiting approval, clarification, error, session end):**

```bash
# Step 1: Check for uncommitted changes
git status

# Step 2: If changes exist, commit WIP
git add -A
git commit -m "WIP: Phase N - <brief description>" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"

# Step 3: Verify commit was created
git log -1 --oneline

# Step 4: Report WIP commit made
```

### WIP Commit Characteristics

| Characteristic | Description |
|---------------|-------------|
| **Prefix** | Always starts with `WIP:` for easy identification |
| **Phase** | Includes phase number for context |
| **Description** | Brief description of what was being worked on |
| **Trailers** | Same co-author trailers as full commits |
| **Squashable** | Can be squashed or amended later with subsequent work |

### After WIP Commit

- **Continue work**: Next commit can amend or squash the WIP commit
- **Session resumes**: Rebase or continue from WIP commit
- **PR creation**: Squash WIP commits with final work before PR

### What Counts as HALT

| HALT Trigger | WIP Required? |
|-------------|--------------|
| Awaiting approval | ✅YES |
| Awaiting clarification | ✅ YES |
| Mid-task pause | ✅ YES |
| Error encountered | ✅ YES |
| Session ending | ✅ YES |
| Task complete | ❌ NO (use full commit) |
| Phase complete | ❌ NO (use full commit) |

---

*Source: Content migrated from `110-git-protocol.md`*