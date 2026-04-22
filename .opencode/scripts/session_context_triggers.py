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


def get_diff_summary() -> dict[str, int | list[str]] | None:
    diff_output = run_git(["diff", "--stat"])
    if not diff_output:
        return None
    lines = diff_output.strip().splitlines()
    if not lines:
        return None
    stat_line = lines[-1].strip() if lines else ""
    file_count = len([entry for entry in lines[:-1] if entry.strip()])
    key_files: list[str] = []
    for line in lines[:-1]:
        parts = line.split("|")
        if parts:
            filepath = parts[0].strip()
            if filepath and not any(
                pat in filepath for pat in ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", ".lock")
            ):
                key_files.append(filepath)
    key_files = key_files[:5]
    insertions = 0
    deletions = 0
    ins_match = re.search(r"(\d+) insertion", stat_line)
    del_match = re.search(r"(\d+) deletion", stat_line)
    if ins_match:
        insertions = int(ins_match.group(1))
    if del_match:
        deletions = int(del_match.group(1))
    return {
        "file_count": file_count,
        "insertions": insertions,
        "deletions": deletions,
        "key_files": key_files,
    }


def get_stash_analysis() -> list[dict[str, str]]:
    stash_list = run_git(["stash", "list"])
    if not stash_list:
        return []
    analyses: list[dict[str, str]] = []
    for line in stash_list.splitlines():
        if not line.strip():
            continue
        parts = line.split(":", 2)
        if len(parts) < 2:
            continue
        stash_ref = parts[0].strip()
        branch_match = re.search(r"On ([^:]+)", line)
        branch = branch_match.group(1) if branch_match else ""
        message = parts[2].strip() if len(parts) >= 3 else ""
        issue_match = re.search(r"#(\d+)", message)
        issue_ref = issue_match.group(1) if issue_match else ""
        file_summary = ""
        show_output = run_git(["stash", "show", stash_ref])
        if show_output:
            file_summary = show_output.strip()
        analyses.append(
            {
                "stash_ref": stash_ref,
                "branch": branch,
                "message": message,
                "issue_ref": issue_ref,
                "file_summary": file_summary,
            }
        )
        if len(analyses) >= 5:
            break
    return analyses


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
        lines.append("- Action: WIP commit + switch to `dev`, then create a feature branch")
    else:
        lines.append(f"- Branch: `{branch}` (production)")
        lines.append("- WARNING: All work must happen on feature branches, not on `main`")
        lines.append("- Action: switch to `dev` first, then create a feature branch")
    return "\n".join(lines)


def build_protected_branch_warning(changed_files: list[str]) -> str:
    branch = get_current_branch() or "dev"
    lines = [
        "## Protected Branch with Uncommitted Changes",
        f"- Branch: `{branch}` with {len(changed_files)} uncommitted changes",
    ]
    diff_summary = get_diff_summary()
    if diff_summary:
        lines.append(f"- Files changed: {diff_summary['file_count']}")
        lines.append(f"- Lines: +{diff_summary['insertions']} / -{diff_summary['deletions']}")
        if diff_summary["key_files"]:
            lines.append("- Key files:")
            for kf in diff_summary["key_files"]:
                lines.append(f"  - `{kf}`")
    for cf in changed_files[:5]:
        _status = cf[:2].strip() if len(cf) >= 2 else "?"
        filepath = cf[3:].strip() if len(cf) >= 3 else cf
        if not diff_summary or filepath not in diff_summary.get("key_files", []):
            lines.append(f"  - `{filepath}`: modified")
    if len(changed_files) > 5:
        lines.append(f"  - ... and {len(changed_files) - 5} more")
    lines.append("- Diff summary available: analyze changes to suggest pair mode entry")
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
        "- Action: commit or stash changes before switching branches",
    ]
    return "\n".join(lines)


def build_stale_stash_warning(stashes: list[str]) -> str:
    lines = [
        "## Stale Stash Found",
    ]
    stash_analyses = get_stash_analysis()
    for analysis in stash_analyses[:3]:
        lines.append(f"- `{analysis['stash_ref']}`: branch={analysis['branch'] or 'unknown'}")
        if analysis["issue_ref"]:
            lines.append(f"  Related issue: #{analysis['issue_ref']}")
        if analysis["message"]:
            lines.append(f"  Message: {analysis['message']}")
        if analysis["file_summary"]:
            for fs_line in analysis["file_summary"].splitlines()[:3]:
                lines.append(f"  {fs_line}")
    if len(stashes) > 3:
        lines.append(f"- ... and {len(stashes) - 3} more")
    lines.append("- Stash analysis available: review contents to recommend resume/drop/issue")
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
    lines.append("- Action: resolve conflicts before proceeding")
    return "\n".join(lines)


def build_unpushed_commits_warning(count: int) -> str:
    lines = [
        "## Unpushed Commits",
        f"- {count} commit(s) ahead of remote",
        "- Action: push when ready with `git push`",
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
    lines.append("- Action: clean up with `git worktree remove <path>`")
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
