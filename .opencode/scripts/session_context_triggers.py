#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "~=3.12"
# dependencies = []
# ///
"""Trigger section emitter for AI agent session context.

Extracted from session_context.py per spec #1107 (R6: intentional
deduplication of shared helpers across split scripts).

Emits ONLY trigger warning sections — no identity, no "Respond to the
above" directive. Called by session-enforcement.ts at
chat.messages.transform time. Output is empty when no triggers fire.

Exit codes:
    0: Success
    1: No git remote or root directory resolution failure
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime


def run_git(args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        pass
    return None


def get_remote_url() -> str | None:
    return run_git(["remote", "get-url", "origin"])


def get_current_branch() -> str | None:
    return run_git(["branch", "--show-current"])


def get_root_dir() -> str | None:
    return run_git(["rev-parse", "--show-toplevel"])


def is_on_main_branch() -> bool:
    branch = get_current_branch()
    return branch == "main" or branch == "master"


def is_on_protected_branch() -> bool:
    branch = get_current_branch()
    return branch in ("main", "master", "dev")


def has_uncommitted_changes() -> tuple[bool, list[str]]:
    result = run_git(["status", "--porcelain"])
    if not result:
        return False, []
    lines = [line for line in result.splitlines() if line.strip()]
    return len(lines) > 0, lines


def is_pair_mode_branch() -> tuple[bool, str | None]:
    branch = get_current_branch()
    if branch and branch.startswith("pair-"):
        return True, branch
    return False, None


def has_stale_stash(threshold_days: int = 7) -> list[str]:
    result = run_git(["stash", "list"])
    if not result:
        return []
    warnings: list[str] = []
    now = datetime.now()
    for line in result.splitlines():
        if not line.strip():
            continue
        parts = line.split(":")
        if len(parts) < 3:
            continue
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", line)
        if date_match:
            try:
                stash_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                if (now - stash_date).days > threshold_days:
                    warnings.append(line.strip())
            except ValueError:
                continue
        else:
            warnings.append(line.strip())
    return warnings


def has_merge_conflict() -> tuple[bool, list[str]]:
    unmerged = run_git(["diff", "--name-only", "--diff-filter=U"])
    if not unmerged:
        return False, []
    files = [f for f in unmerged.splitlines() if f.strip()]
    return len(files) > 0, files


def has_unpushed_commits() -> tuple[bool, int]:
    branch = get_current_branch()
    if not branch:
        return False, 0
    tracking = run_git(["rev-parse", "--abbrev-ref", f"{branch}@{{u}}"])
    if not tracking:
        origin_branch = f"origin/{branch}"
        if run_git(["rev-parse", "--verify", origin_branch]):
            commits_ahead = run_git(["rev-list", "--count", f"{origin_branch}..HEAD"])
            if commits_ahead:
                return True, int(commits_ahead)
        return False, 0
    result = run_git(["rev-list", "--count", f"{tracking}..HEAD"])
    if result:
        count = int(result)
        return count > 0, count
    return False, 0


def has_orphaned_worktrees() -> list[str]:
    result = run_git(["worktree", "list", "--porcelain"])
    if not result:
        return []
    orphaned: list[str] = []
    current_lines = result.splitlines()
    worktrees: list[dict[str, str]] = []
    wt: dict[str, str] = {}
    for line in current_lines:
        if not line.strip():
            if wt:
                worktrees.append(wt)
                wt = {}
            continue
        if " " in line:
            key, val = line.split(" ", 1)
            wt[key] = val
    if wt:
        worktrees.append(wt)

    for wt_entry in worktrees:
        branch = wt_entry.get("branch", "")
        wt_path = wt_entry.get("worktree", "")
        if not branch or not wt_path:
            continue
        branch_name = branch.replace("refs/heads/", "")
        if branch_name in ("main", "master", "dev"):
            continue
        merge_base = run_git(["merge-base", branch_name, "dev"])
        if merge_base:
            dev_hash = run_git(["rev-parse", "dev"])
            if dev_hash and merge_base == dev_hash:
                orphaned.append(f"{wt_path} ({branch_name} — merged into dev)")
    return orphaned


def build_main_branch_warning(has_changes: bool, changed_files: list[str]) -> str:
    lines = [
        "## ⚠️ Repository on Production Branch",
    ]
    branch = get_current_branch() or "main"
    if has_changes:
        lines.append(f"- Branch: `{branch}` (production) with {len(changed_files)} uncommitted changes")
        lines.append("- WARNING: All work must happen on feature branches, not on `main`")
        for cf in changed_files[:10]:
            _status = cf[:2].strip() if len(cf) >= 2 else "?"
            filepath = cf[3:].strip() if len(cf) >= 3 else cf
            lines.append(f"  - `{filepath}`: modified")
        if len(changed_files) > 10:
            lines.append(f"  - ... and {len(changed_files) - 10} more")
        lines.append("- Suggest: WIP commit + switch to `dev`, then create a feature branch")
    else:
        lines.append(f"- Branch: `{branch}` (production)")
        lines.append("- WARNING: All work must happen on feature branches, not on `main`")
        lines.append("- Suggest: switch to `dev` first, then create a feature branch")
    return "\n".join(lines)


def build_protected_branch_warning(changed_files: list[str]) -> str:
    branch = get_current_branch() or "dev"
    lines = [
        "## Protected Branch with Uncommitted Changes",
        f"- Branch: `{branch}` with {len(changed_files)} uncommitted changes",
        "- Suggest: create a feature branch before making changes",
    ]
    return "\n".join(lines)


def build_pair_mode_resume(branch: str) -> str:
    issue_match = re.search(r"/(\d+)[-/]", branch)
    issue_hint = f"\n- Related issue: #{issue_match.group(1)}" if issue_match else ""

    diff_stat = run_git(["diff", "--stat", "origin/dev..HEAD"])
    summary = ""
    if diff_stat:
        lines = diff_stat.strip().splitlines()
        if lines:
            summary = f"\n- Changes: {lines[-1].strip()}"

    return "\n".join(
        [
            "## Pair Mode Resumed",
            f"- Branch: `{branch}`",
            f"- Resuming pair-mode collaboration{issue_hint}{summary}",
        ]
    )


def build_uncommitted_work_warning(changed_files: list[str]) -> str:
    lines = [
        "## Uncommitted Work",
        f"- {len(changed_files)} uncommitted change(s) detected",
        "- Suggest: commit or stash changes before switching branches",
    ]
    return "\n".join(lines)


def build_stale_stash_warning(stashes: list[str]) -> str:
    lines = [
        "## Stale Stash Found",
    ]
    for s in stashes[:3]:
        lines.append(f"- `{s}`")
    if len(stashes) > 3:
        lines.append(f"- ... and {len(stashes) - 3} more")
    lines.append("- Suggest: resume or clean up the stash")
    return "\n".join(lines)


def build_merge_conflict_warning(files: list[str]) -> str:
    lines = [
        "## Merge Conflict Detected",
        f"- {len(files)} unmerged file(s):",
    ]
    for f in files[:5]:
        lines.append(f"  - `{f}`")
    if len(files) > 5:
        lines.append(f"  - ... and {len(files) - 5} more")
    lines.append("- Suggest: resolve conflicts before proceeding")
    return "\n".join(lines)


def build_unpushed_commits_warning(count: int) -> str:
    lines = [
        "## Unpushed Commits",
        f"- {count} commit(s) ahead of remote",
        "- Suggest: push when ready with `git push`",
    ]
    return "\n".join(lines)


def build_orphaned_worktrees_warning(wt_list: list[str]) -> str:
    lines = [
        "## Orphaned Worktrees",
    ]
    for w in wt_list[:3]:
        lines.append(f"- {w}")
    if len(wt_list) > 3:
        lines.append(f"- ... and {len(wt_list) - 3} more")
    lines.append("- Suggest: clean up with `git worktree remove <path>`")
    return "\n".join(lines)


def main() -> int:
    remote_url = get_remote_url()
    if not remote_url:
        print("No git remote configured. Cannot determine repository identity.", file=sys.stderr)
        return 1

    root_dir = get_root_dir()
    if not root_dir:
        print("Not in a git repository.", file=sys.stderr)
        return 1

    sections: list[str] = []

    on_main = is_on_main_branch()
    on_protected = is_on_protected_branch()
    has_changes, changed_files = has_uncommitted_changes()

    if on_main:
        sections.append(build_main_branch_warning(has_changes, changed_files))
    elif on_protected and has_changes:
        sections.append(build_protected_branch_warning(changed_files))

    is_pair, pair_branch = is_pair_mode_branch()
    if is_pair and pair_branch:
        sections.append(build_pair_mode_resume(pair_branch))

    if has_changes and not on_main and not (on_protected and has_changes):
        sections.append(build_uncommitted_work_warning(changed_files))

    stashes = has_stale_stash()
    if stashes:
        sections.append(build_stale_stash_warning(stashes))

    has_conflict, conflict_files = has_merge_conflict()
    if has_conflict:
        sections.append(build_merge_conflict_warning(conflict_files))

    has_unpushed, count = has_unpushed_commits()
    if has_unpushed:
        sections.append(build_unpushed_commits_warning(count))

    orphaned = has_orphaned_worktrees()
    if orphaned:
        sections.append(build_orphaned_worktrees_warning(orphaned))

    if len(sections) > 0:
        print("\n\n".join(sections))

    return 0


if __name__ == "__main__":
    sys.exit(main())
