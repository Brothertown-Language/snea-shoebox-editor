# Task: sync-push

## Purpose

Push core guideline/skill changes from source repository to target repository via GitHub/GitBucket issue.

## Operating Protocol

1. Invoked by: `/skill sync-guidelines --task sync-push`
2. When to use: When syncing changes FROM source repo TO target repo
3. Exit criteria: Sync issue created in target repo with classified files

## Procedure

### Step 1: Pre-Work Verification

1. Verify on feature branch (not `main`)
2. Check for uncommitted changes (`git status`)
3. Stash if needed

### Step 2: Discover Changed Files

1. Detect changed files since last sync
2. Read the entire file content of each changed file
3. Analyze semantically what the file does
4. Determine classification using `classify` task criteria

### Step 3: Conflict Detection

Before creating push issue:
1. Check if file exists in target repo (`github_get_file_contents`)
2. If both modified, note conflict in issue
3. Recommend manual merge in issue body

### Step 4: Create Sync Issue

Use `github_issue_write` to create an issue in target repository:

```
github_issue_write(
    method="create",
    owner=<target_owner>,
    repo=<target_repo>,
    title="[SYNC] Push: {count} files from {source_repo}",
    body=<structured issue with inspection analysis>,
    labels=["sync", "needs-review"]
)
```

Issue format follows the `issue-format` task template.

### Step 5: Report Completion

Report to chat documenting:
- Files analyzed
- Classification decisions with reasoning
- Issue URL created

## Context Required

- Related skills: `sync-guidelines` (parent skill)
- Related tasks: `classify`, `issue-format`