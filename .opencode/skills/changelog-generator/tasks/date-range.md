# Task: date-range

## Purpose

Generate changelog entries for commits within a specific date range.

## Operating Protocol

1. **Parse date range**: Validate start and end dates
2. **Collect commits**: Scan all commits in the date range
3. **Categorize changes**: Group into Added/Changed/Fixed/Security/Deprecated
4. **Write entries**: Create or update CHANGELOG.md
5. **Stage changes**: `git add CHANGELOG.md`

## Procedure

### Step 1: Parse Date Range

Input format: `--date-range "YYYY-MM-DD..YYYY-MM-DD"` or `--from DATE --to DATE`

Validate:
- Both dates are valid YYYY-MM-DD format
- Start date <= End date
- Both dates are in the past

### Step 2: Collect Commits

```bash
git log --since="YYYY-MM-DD" --until="YYYY-MM-DD" \
    --pretty=format:"%h|%ad|%an|%s%n%b" --date=short
```

### Step 3-7: Same as since-last-release

Follow the same categorization, transformation, and writing procedures as `since-last-release` task.

## Use Cases

- Weekly changelogs: `--date-range "2026-03-01..2026-03-07"`
- Monthly updates: `--date-range "2026-03-01..2026-03-31"`
- Custom release windows
- Backfilling missing changelog entries

## Example

```
/skill changelog-generator --date-range "2026-03-01..2026-03-31"
```

Generates changelog for all commits in March 2026.