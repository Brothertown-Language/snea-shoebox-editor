# Pair-Mode PR Creation Task

Squash and create PR targeting `dev` with `[pair-mode]` trailers.

## Squash Workflow

Pair mode uses the same squash workflow as autonomous mode:

1. **Soft-reset to dev:**
   ```bash
   git reset --soft origin/dev
   ```

2. **Create single commit with pair-mode trailers:**
   ```bash
   git commit -m "<conventional subject>

   <body>

   Implements #<issue>

   Co-authored-by: <dev.name> <<dev.email>> [pair-mode]
   Co-authored-by: AI: <AGENT_NAME> (<MODEL_ID>) [pair-mode]"
   ```

3. **Push:**
   ```bash
   git push -u origin <pair-branch>
   ```

4. **Create PR via GitHub MCP:**
   ```yaml
   method: create_pull_request
   owner: <github.owner>
   repo: <github.repo>
   title: "<conventional subject>"
   head: "<pair-branch>"
   base: "dev"
   body: |
     ## Summary
     <1-3 bullet points>

     ## Outcome
     <What changed for stakeholders>

     Implements #<issue>

     Co-authored-by: <dev.name> <<dev.email>> [pair-mode]
     Co-authored-by: AI: <AGENT_NAME> (<MODEL_ID>) [pair-mode]
   ```

## PR Body Keyword Discipline

- Use `Implements #N` for pair-mode PRs (never `Fixes` or `Closes`)
- `Implements` links the PR to the issue without auto-closing on merge
- Auto-closure bypasses verification gates — `Fixes`/`Closes` are prohibited

## Result Contract

```yaml
status: DONE | BLOCKED
task: pair-pr-creation
pr_number: <N|null>
pr_url: <url|null>
squash_performed: bool
pair_mode: true
```