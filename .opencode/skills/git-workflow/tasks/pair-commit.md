# Pair-Mode Commit Task

Commit changes with `[pair-mode]` co-author trailers and optional issue association.

## Commit Message Format

Pair mode commits include `[pair-mode]` tag in co-author trailers:

```
<conventional subject>

<optional body>

Co-authored-by: <DEV_NAME> <<DEV_EMAIL>> [pair-mode]
Co-authored-by: AI: <AGENT_NAME> (<MODEL_ID>) [pair-mode]
```

## Issue Association

When the pair branch contains an issue number (e.g., `pair-feature/123-xyz`):

1. Extract issue number from branch name
2. Include issue reference in commit footer: `Refs #123`
3. Use `Implements #123` (not `Fixes #123`) to avoid premature closure

When branch has no issue number or ambiguous:
- Ask developer: "Which issue is this commit for?"
- If developer doesn't specify, omit issue reference

## Steps

1. **Stage changes:**
   ```bash
   git add -A
   ```

2. **Create commit with pair-mode trailers:**
   ```bash
   git commit -m "<subject>

   <body if needed>

   Co-authored-by: <DEV_NAME> <<DEV_EMAIL>> [pair-mode]
   Co-authored-by: AI: <AGENT_NAME> (<MODEL_ID>) [pair-mode]"
   ```

   For commits with issue association:
   ```bash
   git commit -m "<subject>

   Implements #<issue>

   Co-authored-by: <DEV_NAME> <<DEV_EMAIL>> [pair-mode]
   Co-authored-by: AI: <AGENT_NAME> (<MODEL_ID>) [pair-mode]"
   ```

3. **Verify commit:**
   ```bash
   git log -1 --format="%B"
   ```

## Protected Branch Check

Before committing, verify NOT on `dev` or `main`:
```bash
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "dev" ] || [ "$BRANCH" = "main" ]; then
    echo "BLOCKED: Cannot commit on $BRANCH"
    # Prompt developer to create pair branch first
fi
```

## Result Contract

```yaml
status: DONE | BLOCKED
task: pair-commit
commit_hash: <sha>
issue_referenced: <N|null>
pair_mode: true
```