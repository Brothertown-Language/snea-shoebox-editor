#!/bin/bash
# Install git hooks by copying to .git/hooks/
# Usage: ./scripts/install-hooks.sh

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
HOOKS_SRC="$REPO_ROOT/.opencode/hooks"

if [ ! -d "$HOOKS_SRC" ]; then
    echo "ERROR: .opencode/hooks directory not found at $HOOKS_SRC"
    echo "Please ensure the .opencode/hooks directory exists with hook scripts."
    exit 1
fi

echo "Installing git hooks from .opencode/hooks/ to .git/hooks/..."

# Ensure .git/hooks directory exists
mkdir -p "$REPO_ROOT/.git/hooks"

INSTALLED=0
SKIPPED=0
FAILED=0

for hook in "$HOOKS_SRC"/*; do
    if [ ! -f "$hook" ]; then
        continue
    fi

    hook_name=$(basename "$hook")
    target="$REPO_ROOT/.git/hooks/$hook_name"

    # Skip sample files
    if [[ "$hook_name" == *.sample ]]; then
        continue
    fi

    # Check if target already matches source
    if [ -f "$target" ] && cmp -s "$hook" "$target"; then
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Copy hook to .git/hooks/ and make executable
    if cp "$hook" "$target" && chmod +x "$target"; then
        INSTALLED=$((INSTALLED + 1))
    else
        echo "ERROR: Failed to install $hook_name" >&2
        FAILED=$((FAILED + 1))
    fi
done

# Install hooks in submodule .git/modules directories
if [ -f "$REPO_ROOT/.gitmodules" ]; then
    while IFS= read -r path; do
        if [ -z "$path" ]; then
            continue
        fi

        # Resolve submodule git directory
        submod_hooks="$REPO_ROOT/.git/modules/$path/hooks"
        if [ ! -d "$submod_hooks" ]; then
            # Try resolving from .git file in submodule directory
            submod_git_file="$REPO_ROOT/$path/.git"
            if [ -f "$submod_git_file" ]; then
                gitdir_ref=$(cat "$submod_git_file" | head -1)
                if [[ "$gitdir_ref" == gitdir:\ * ]]; then
                    resolved_gitdir="${gitdir_ref#gitdir: }"
                    if [[ "$resolved_gitdir" != /* ]]; then
                        resolved_gitdir="$REPO_ROOT/$path/$resolved_gitdir"
                    fi
                    submod_hooks="$resolved_gitdir/hooks"
                fi
            fi
        fi

        if [ ! -d "$submod_hooks" ]; then
            echo "WARNING: Could not resolve hooks dir for submodule: $path" >&2
            continue
        fi

        mkdir -p "$submod_hooks"

        for hook in "$HOOKS_SRC"/*; do
            if [ ! -f "$hook" ]; then
                continue
            fi

            hook_name=$(basename "$hook")
            [[ "$hook_name" == *.sample ]] && continue

            target="$submod_hooks/$hook_name"

            if [ -f "$target" ] && cmp -s "$hook" "$target"; then
                SKIPPED=$((SKIPPED + 1))
                continue
            fi

            if cp "$hook" "$target" && chmod +x "$target"; then
                INSTALLED=$((INSTALLED + 1))
            else
                echo "ERROR: Failed to install $hook_name in submodule $path" >&2
                FAILED=$((FAILED + 1))
            fi
        done
    done < <(git config --file "$REPO_ROOT/.gitmodules" --get-regexp path 2>/dev/null | awk '{print $2}')
fi

# Remove legacy core.hooksPath config if present
if git config --local core.hooksPath >/dev/null 2>&1; then
    git config --unset core.hooksPath
    echo "Removed legacy core.hooksPath config (hooks now in .git/hooks/)"
fi

echo ""
echo "✅ Git hooks installed successfully!"
echo ""
echo "Protected branches:"
echo "  - main (production)"
echo "  - dev (integration)"
echo ""
echo "Hooks installed:"
echo "  - pre-commit: Blocks commits to protected branches"
echo "  - post-commit: Warns if commit made to protected branch"
echo "  - pre-push: Blocks pushes to merged branches"
echo ""
echo "Installed: $INSTALLED, Skipped (up to date): $SKIPPED, Failed: $FAILED"