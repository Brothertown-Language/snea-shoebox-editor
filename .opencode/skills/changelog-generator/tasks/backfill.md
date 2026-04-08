# Task: backfill

## Purpose

Backfill CHANGELOG.md with entries from historical commits that were missing changelog updates.

## Operating Protocol

1. **Find last changelog entry**: Identify the version/date of last changelog entry
2. **Scan historical commits**: Analyze all commits from project start to last changelog
3. **Categorize and write**: Generate entries for missing PRs/commits
4. **Preserve existing**: Keep existing changelog entries intact
5. **Stage changes**: `git add CHANGELOG.md`

## When to Use

- Initial changelog creation for existing project
- Catching up after PRs merged without changelog updates
- Filling gaps in changelog history
- One-time historical backfill

## Procedure

### Step 1: Identify Scope

```bash
# Find last changelog entry date
git log --oneline --max-count=1 CHANGELOG.md

# Find project start
git log --reverse --max-count=1 --format="%h %ad"
```

### Step 2: Scan for Missing Entries

Generate changelog for the entire history from project start to last changelog commit.

**Important:** This task creates ENTRIES ONLY - it does not replace or modify existing entries in CHANGELOG.md.

### Step 3: Merge with Existing

1. Read existing CHANGELOG.md content
2. Extract version sections ([Unreleased], [0.1.0], etc.)
3. Insert backfilled entries into appropriate version sections based on commit dates
4. Preserve all existing entries

### Step 4: Categorization by Version

If commits span multiple releases:

```bash
# Get tags/versions in date range
git tag --sort=-creatordate

# Group commits by version
# Commits before v0.1.0 → version before that
# Commits between v0.1.0 and v0.2.0 → v0.1.x section
```

### Step 5: Write and Stage

1. Write merged changelog maintaining all existing content
2. Stage: `git add CHANGELOG.md`
3. Report: Number of backfilled entries by category

## Example

```
/skill changelog-generator --backfill
```

Creates entries for all historical PRs not yet in changelog.

## Backfill vs Since-Last-Release

| Task | Scope | Use Case |
|------|-------|----------|
| `since-last-release` | Commits after last changelog | Normal PR workflow |
| `backfill` | Entire history | One-time historical catchup |
| `date-range` | Specific dates | Weekly/monthly updates |

## Caution

Backfill is intended for ONE-TIME use to fill historical gaps. After backfill, use `since-last-release` for ongoing PR workflow.