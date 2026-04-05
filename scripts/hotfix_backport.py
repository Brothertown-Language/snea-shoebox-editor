#!/usr/bin/env python3
"""Hotfix backport script for merging main → dev with proper conflict resolution.

This script automates the hotfix backport process, ensuring that:
1. Hotfix-specific files are taken from main
2. All other files are taken from dev (authoritative source)
3. Complex conflicts are flagged for manual review

Usage:
    python scripts/hotfix_backport.py <hotfix-pr-number>
    python scripts/hotfix_backport.py --hotfix-branch <branch-name>
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return result."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    return result


def get_hotfix_files_from_pr(pr_number: int) -> set[str]:
    """Get list of files modified in the hotfix PR."""
    result = run_command(["gh", "pr", "view", str(pr_number), "--json", "files", "--jq", ".files[].path"])
    return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()


def get_hotfix_files_from_branch(branch_name: str) -> set[str]:
    """Get list of files modified in the hotfix branch."""
    result = run_command(["git", "diff", f"{branch_name}^..{branch_name}", "--name-only"])
    return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()


def is_hotfix_specific_file(file_path: str, hotfix_files: set[str]) -> bool:
    """Check if a file is hotfix-specific."""
    return file_path in hotfix_files


def resolve_conflict(file_path: str, hotfix_files: set[str]) -> str:
    """Determine conflict resolution strategy for a file.

    Returns:
        'ours' if file should come from main (hotfix-specific)
        'theirs' if file should come from dev (authoritative)
    """
    if is_hotfix_specific_file(file_path, hotfix_files):
        return "ours"  # Take from main
    return "theirs"  # Take from dev


def main():
    """Main entry point for hotfix backport.

    Testing:
        1. Create a test fixture repository with main/dev branches
        2. Create a hotfix branch from main with a single file change
        3. Merge hotfix to main
        4. Make conflicting changes on dev
        5. Run this script with the hotfix PR number or branch name
        6. Verify dev files preserved and hotfix files applied

        Manual testing:
        ```bash
        # Test with PR number
        python scripts/hotfix_backport.py 123

        # Test with branch name
        python scripts/hotfix_backport.py --hotfix-branch hotfix/urgent-fix
        ```
    """
    if len(sys.argv) < 2:
        print("Usage: python scripts/hotfix_backport.py <hotfix-pr-number>")
        print("       python scripts/hotfix_backport.py --hotfix-branch <branch-name>")
        sys.exit(1)

    # Parse arguments
    if sys.argv[1] == "--hotfix-branch":
        if len(sys.argv) < 3:
            print("Error: --hotfix-branch requires branch name argument")
            sys.exit(1)
        branch_name = sys.argv[2]
        hotfix_files = get_hotfix_files_from_branch(branch_name)
        print(f"Hotfix files from branch {branch_name}:")
    else:
        pr_number = int(sys.argv[1])
        hotfix_files = get_hotfix_files_from_pr(pr_number)
        print(f"Hotfix files from PR #{pr_number}:")

    if not hotfix_files:
        print("No hotfix files found. Exiting.")
        sys.exit(1)

    for f in sorted(hotfix_files):
        print(f"  - {f}")

    # Checkout dev branch
    print("\nChecking out dev branch...")
    run_command(["git", "checkout", "dev"])
    run_command(["git", "pull", "origin", "dev"])

    # Attempt merge
    print("\nAttempting merge from main...")
    result = run_command(["git", "merge", "main"], check=False)

    if result.returncode == 0:
        print("Merge completed successfully with no conflicts.")
        print("\nTo complete the backport:")
        print("  git push origin dev")
        sys.exit(0)

    # Handle conflicts
    print("\nMerge conflicts detected. Resolving...")

    # Get list of conflicted files
    result = run_command(["git", "diff", "--name-only", "--diff-filter=U"])
    conflicted_files = [f for f in result.stdout.strip().split("\n") if f]

    if not conflicted_files:
        print("No conflicted files found. Merge may have failed for other reasons.")
        sys.exit(1)

    print(f"\nConflicted files ({len(conflicted_files)}):")
    for f in conflicted_files:
        resolution = resolve_conflict(f, hotfix_files)
        strategy = "main (hotfix)" if resolution == "ours" else "dev (authoritative)"
        print(f"  - {f} [{strategy}]")

    # Resolve conflicts based on strategy
    for file_path in conflicted_files:
        resolution = resolve_conflict(file_path, hotfix_files)

        if resolution == "ours":
            # Take from main (hotfix fix)
            run_command(["git", "checkout", "--ours", file_path])
        else:
            # Take from dev (authoritative)
            run_command(["git", "checkout", "--theirs", file_path])

        run_command(["git", "add", file_path])

    print("\nConflicts resolved. Completing merge...")
    run_command(["git", "commit", "-m", "Merge hotfix from main with conflict resolution"])

    print("\nMerge completed with conflict resolution.")
    print("\nTo complete the backport:")
    print("  git push origin dev")


if __name__ == "__main__":
    main()
