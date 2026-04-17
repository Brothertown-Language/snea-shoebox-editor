# Pair-Mode Resume Task

Detect and report on `pair-*` branch at session start.

## Detection

```bash
BRANCH=$(git branch --show-current)
```

If `$BRANCH` starts with `pair-`:

1. **Identify issue number from branch name:**
   Extract numeric issue reference from branch: `pair-feature/123-xyz` → issue #123

2. **Show diff summary:**
   ```bash
   git diff --stat origin/dev..HEAD
   ```

3. **Check for uncommitted changes:**
   ```bash
   git status --porcelain
   ```

4. **Check for unpushed commits:**
   ```bash
   git rev-list --count origin/<pair-branch>..HEAD
   ```

5. **Report to developer:**
   ```
   Pair mode resumed on `<branch>`
   - Related issue: #123
   - Changes: <diff summary>
   - Uncommitted: <count> file(s)
   - Unpushed: <count> commit(s)
   ```

## No Pair Branch Active

If current branch does NOT start with `pair-`:
- No pair-mode resume needed
- Skip this task entirely

## Result Contract

```yaml
status: DONE | SKIP
task: pair-mode-resume
pair_branch: <str|null>
issue_number: <N|null>
changes_summary: <str>
uncommitted_count: <int>
unpushed_count: <int>
```