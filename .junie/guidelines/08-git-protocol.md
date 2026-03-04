# Git Protocol

## Prohibited

- Agent MUST NOT run `git add`, `git stage`, `git commit`, or `git push` unless the user explicitly requests it. No
  proactive commit grouping or staging advice.

## Commit Preparation (only when user requests)

- Agent MUST NOT proactively create commit messages, commit scripts, staging advice, or semantic commit groupings. Only
  provide these when explicitly asked.
- When requested: may create commit message files (e.g., `commit.msg`) and identify all relevant side-effect changes (
  e.g., `uv.lock`, auto-updated configs). Flag untracked in-scope files.
- When requested: re-run discovery (`git status`, `git diff`, `git diff --cached`) before advising — don't rely on
  memory.
- If `pyproject.toml` changed, note that `uv.lock` should be included (when policy is to commit it).

## Lockfile Policy

- This repository is an application/CI repo — commit `uv.lock`. (Pure libraries would add it to `.gitignore` and
  document rationale instead.)
