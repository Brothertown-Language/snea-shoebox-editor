# REVIEW PLAN: Strengthen `03-tool-usage.md` § `.junie/ File Access` Line 135

**File:** `.junie/guidelines/03-tool-usage.md`
**Status:** ✔️ Completed

---

## Problem

Violation #33 (2026-03-09): The agent piped `ai_bin/guidelines` output into a `python3 -c`
inline command — a pattern explicitly prohibited by line 135. The rule exists but lacks the
mandatory "CRITICAL VIOLATION — log immediately via `ai_bin/violation-log` and halt"
consequence that other enforced rules in the same file use. Without that consequence, the
rule reads as advisory rather than hard-stop.

## Proposed Change

**Current line 135:**
```
  - **NO SHELL PIPELINES FOR EXTRACTION**: Using shell pipelines, `python -c`, `python3 -c`, or any inline script to extract or filter guideline content is a CRITICAL VIOLATION. Use `--section <name>` directly.
```

**Replacement:**
```
  - **NO SHELL PIPELINES FOR EXTRACTION**: Using shell pipelines, `python -c`, `python3 -c`,
    or any inline script to extract or filter guideline content is a CRITICAL VIOLATION.
    Use `--section <name>` or `--files <name>` directly. The agent MUST log the violation
    immediately via `ai_bin/violation-log` and halt. No exceptions.
```

## Why

- Mirrors the enforcement pattern used for other hard-stop rules in the same file (e.g., the
  `cd <path> &&` prohibition, the `grep` prohibition, the filler-echo prohibition).
- Adds the mandatory log+halt consequence that was absent, making non-compliance
  self-documenting and unambiguous.
- Adds `--files <name>` as an explicit permitted alternative (already supported by the tool,
  not mentioned in line 135).

## Scope

- Single line edit in `.junie/guidelines/03-tool-usage.md` (line 135).
- No code changes. No other files.

## Steps

1. 🔄 Edit `.junie/guidelines/03-tool-usage.md` line 135 — replace as described above.
2. 🔄 Update `memory.md` session state to reflect task complete.
