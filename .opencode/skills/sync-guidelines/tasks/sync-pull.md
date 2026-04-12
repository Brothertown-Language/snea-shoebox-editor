# Task: sync-pull

## Purpose

Pull core guideline/skill changes from source repository into local repository via GitHub/GitBucket issue.

## Operating Protocol

1. Invoked by: `/skill sync-guidelines --task sync-pull`
2. When to use: When syncing changes FROM source repo INTO local repo
3. Exit criteria: Sync issue created in source repo with classified files

## Procedure

### Step 1: Pre-Work Verification

1. Verify on feature branch (not `main`)
2. Check for uncommitted changes (`git status`)
3. Stash if needed

### Step 2: Discover Changed Files

1. Detect changed files since last sync
2. Read each file's content from source repository
3. Analyze and classify using `classify` task criteria

### Step 3: Conflict Detection (Pull)

Before creating pull issue:
1. Read local file content
2. Analyze for project-specific modifications
3. If project-specific content found:
   - SKIP this file
   - Note as "protected" in issue
   - Recommend manual review if needed
4. If safe, proceed with pull proposal

### Step 4: Create Sync Issue

Use `github_issue_write` to create an issue in source repository:

```
github_issue_write(
    method="create",
    owner=<source_owner>,
    repo=<source_repo>,
    title="[SYNC] Pull: {count} files from {source_repo}",
    body=<structured issue with inspection analysis>,
    labels=["sync", "needs-review"]
)
```

Issue format follows the `issue-format` task template.

### Step 5: Report Completion

Post comment to spec issue documenting:
- Files analyzed
- Classification decisions with reasoning
- Issue URL created

## Context Required

- Related skills: `sync-guidelines` (parent skill)
- Related tasks: `classify`, `issue-format`