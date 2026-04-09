# Git Protocol: Commit Workflow

## 1. Commit Policy (User-Initiated Only)

### 🚫 NEVER DO

- **NEVER run `git restore`, `git checkout`, `git reset`, `git clean`, or any other git command that discards or modifies working tree state.**
- **NEVER discard uncommitted changes** — even if they appear to be formatting-only, unintended, or erroneous. Analysis commands are read-only.
- **NEVER commit or merge without direct instruction.** Commits and merges may ONLY be initiated by the developer as a direct instruction to the AI agent. Autonomously committing or merging is FORBIDDEN.
- **NEVER create a PR without direct instruction.** PRs require explicit developer request — see `113-git-pr-workflow.md`.
- Agent MUST NOT create commit messages or scripts proactively (without user request).

### STOP ASKING FOR COMMITS AND PRS

The developer will say "commit" or "create a PR" when they want git operations. Until then, do nothing—no questions, no prompts:

1. **After completing implementation**: Report completion concisely, then STOP and wait silently
2. **Do NOT ask**: "Commit?", "Ready to commit?", "Should I commit?", "Ready for a PR?", "Create a PR?", "Push and PR?"
3. **Do NOT automatically create PRs**: PR creation requires the same explicit instruction as commits

### ✅ ALWAYS DO

- **Include co-author trailers for both AI and human collaborator.** Every implementation commit MUST include TWO trailers:
  - AI author: Use the AI's actual identity dynamically (the AI knows its own name)
  - Human collaborator: Use session-cached values from `000-session-init.md`
- Re-run discovery (`git status`, `git diff`) before any commit workflow
- If `pyproject.toml` changed, include `uv.lock`

### Co-Author Trailer Workflow

**⚠️ CRITICAL: AI Identity is DYNAMIC — NEVER copy the AI name from examples!**

| Identity Component | How to Detect | FORBIDDEN |
|-------------------|---------------|-----------|
| `<AgentName>` | Agent's actual name at runtime | Copying "OpenCode" or "AI Assistant" from examples |
| `<ModelID>` | Backing model ID at runtime | Copying "ollama-cloud/*" from examples |
| `<ai-email>` | Agent's noreply email | Using project domain email |

**When Identity Unknown:**
- STOP and ask user for clarification
- DO NOT use example values as defaults
- DO NOT guess or invent identity values

**Format:**
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

- To inspect a file at a historical commit, use `git show <ref>:<path> > ./tmp/historical_file.ext`
- Process the saved file with the appropriate `ai_bin/` or IDE tool

### 🚫 NEVER DO

- Using `python3`, `python -c`, `json.tool`, `grep`, or `sed` to process `git show` output is a critical violation

---

## 4. Lockfile Policy

- This repository is an application/CI repo — commit `uv.lock`

---

## 5. WIP Commit Before HALT (MANDATORY)

> **See `git-workflow` skill → `implementation` task for complete WIP commit workflow.**

**CRITICAL: Work-in-progress commits MUST be made before ANY HALT to prevent data loss.**

| HALT Trigger | WIP Required? |
|-------------|--------------|
| Awaiting approval | ✅ YES |
| Awaiting clarification | ✅ YES |
| Mid-task pause | ✅ YES |
| Error encountered | ✅ YES |
| Session ending | ✅ YES |
| Task/Phase complete | ❌ NO (use full commit) |

**When to Clear Todos:** After authorization received, clear todos if workflow was interrupted (clarification, revision, context switch, error).

---

## 6. Grouped-Step Commit Strategy

**Commit per logical group, not per step.**

| Scenario | Commit Strategy |
|----------|-----------------|
| Single file change | Single commit |
| Multiple files, same feature | Single commit |
| Multiple concerns (DB + API) | Grouped commits |
| Multi-phase spec | Grouped commits by phase |

**WIP commits happen BETWEEN phases, NOT within phases.**

> **See `git-workflow` skill → `implementation` task for grouped commit workflow.**

---

*Source: Content migrated from `110-git-protocol.md`*