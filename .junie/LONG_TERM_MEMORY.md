<!-- Copyright (c) 2026 Brothertown Language -->
# AI Long-Term Memory

This file serves as a persistent memory of critical project context, user preferences, and cross-session decisions that must survive context window truncation.

## CRITICAL PROJECT CONTEXT
- **Identity**: Brothertown Language / SNEA Shoebox Editor.
- **Ethical Mandate**: Preservation and reconstruction of the Southern New England Algonquian language.
- **Data Layer**: MDF (Multi-Dictionary Formatter) standards using PostgreSQL and pgvector.

## USER PREFERENCES & HARD CONSTRAINTS
- **Sole Decision Maker**: The User is the programmer. Junie is the executor.
- **STOP AND ASK**: Never assume intent. If a task is ambiguous or high-impact, halt and ask.
- **NO ROADMAP DRIVING**: Do not implement future phases or "cleanup" code without direct orders.
- **PRIVATE DATABASE ONLY**: `JUNIE_PRIVATE_DB=true` is the only acceptable environment for operations.
- **COMMIT SCRIPT METHOD**: All source changes must be prepared as `tmp/commit_task.sh` scripts, never committed directly by the AI.
- **NO `cd` IN COMMANDS**: The shell is always at the project root. NEVER prefix commands with `cd /path &&`. Just run the command directly. (Recurring violation #3 — see VIOLATION_LOG.md.)
- **COMMIT SCRIPTS MUST EXECUTE `git commit`**: Never use `echo` to tell the user to run `git commit` separately. The script must run `git commit -F tmp/commit.msg` directly. The user's review step is choosing to run the script. (Recurring violation #4 — see VIOLATION_LOG.md.)
- **1-BASED COUNTING ONLY**: All numbered steps, task IDs, and sequential labels must start from 1, never 0. The user is not a computer — use natural counting.

## KEY CROSS-SESSION DECISIONS
- **Deep Inspection Mandate**: Memory-based verification is strictly prohibited. AI must always perform deep inspection of source files before confirming any status or re-evaluating state.
- **Phase 5 Stage 3 Refactoring**: Decoupling navigation and redirection logic into `NavigationService`. (Current focus).
- **Security Strategy**: Case-insensitive matching for GitHub identifiers is mandatory due to case mismatches between GitHub API and DB seeds.
- **UI Standard**: Use `st.html()` for all HTML/CSS/JS injections. `unsafe_allow_html=True` is deprecated in this project.
- **Path Resolution**: Always use the 3-step `git rev-parse` boilerplate in shell scripts for IDE compatibility. NEVER use `cd "$(dirname "$0")/.."` — use `BASH_SOURCE[0]` instead of `$0`.
- **Manual Testing Requirement**: The **Full Auth Flow** (OAuth -> Sync -> RBAC -> Navigation tree update) requires manual verification by the user end-to-end, as it cannot be fully automated in the current environment.

## SESSION INITIALIZATION CHECKLIST
- [ ] Re-read `.junie/VIOLATION_LOG.md`.
- [ ] Re-read `.junie/LONG_TERM_MEMORY.md`.
- [ ] Check `documentation/ACTIVE_TASK.md` for current task state.
