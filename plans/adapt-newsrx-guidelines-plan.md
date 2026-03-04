# Plan: Adapt newsrx-genai Guidelines to SNEA Shoebox Editor

**Status**: ✅ Complete
**Created**: 2026-03-03

---

## Overview

Several guideline files were ported from `newsrx-genai`. This plan adapts the universal portions to this project,
archives the newsrx-specific portions, and restructures `guidelines.md` to use the topic-file architecture.

---

## Steps

### 1. ⏳ Archive `07-persistence.md`
Move `.junie/guidelines/07-persistence.md` to `.junie/guidelines/archive/07-persistence.newsrx.md`.
The entire file is newsrx-specific (PubmedArticleRepository, pubmed_data_3, SQLAlchemy ORM, SQLite repositories).
No SNEA-equivalent content exists yet; a SNEA-specific persistence guideline is out of scope for this plan.

### 2. ⏳ Trim `09-scripting.md`
Remove the **Notebook Execution Logging** section (papermill, `logs/`, `.ipynb` artifacts — newsrx-specific).
Keep: Script Headers, Self-Location & Root Resolution, UV Run.
The shell script header boilerplate already exists in `guidelines.md` (Section IV) and should remain in `09-scripting.md`
as the canonical location after restructuring.

### 3. ⏳ Trim `05-code-standards.md`
Remove the **Parsing Logic Changes** paragraph (references `src/commons/parsing/`, `0100_ingest_xml.ipynb`,
`pubmed_data_2` — entirely newsrx-specific pipeline).
Remove the **NLP packages** bullet (NLTK, FSM/LALR grammars — not relevant to SNEA).
Keep all other code standards (typing, KISS, DRY, SRP, modern Python, pathlib, f-strings).

### 4. ⏳ Trim `06-data-integrity.md`
Remove the **Exhaustive Automated Analysis** bullet (references `pubmed_data_2` large archive — newsrx-specific).
Remove the **NO UNAUTHORIZED FORMAT CHANGES** and **MANDATORY AUDIT LOGGING** bullets (reference "Ground Truth"
archived datasets like `pubmed_data_2`).
Keep: Fail-Fast, NO FALSE DATA, NO DEFAULT DATA, Verify Before Recommend, Robust Sampling, Evidence-Based Remediation,
Batch Operations.

### 5. ⏳ Replace `LONG_TERM_MEMORY.md` with `memory.md`
Create `.junie/memory.md` as a structured 40-line max key:value file with a `<!-- Last pruned: -->` marker.
Migrate any active/relevant entries from `LONG_TERM_MEMORY.md` into `memory.md`.
Archive `LONG_TERM_MEMORY.md` to `.junie/archive/LONG_TERM_MEMORY.archived.md`.

### 6. ⏳ Restructure `guidelines.md` using topic-file architecture
Replace the current monolithic `guidelines.md` with the `guidelines (copy).md` header structure:
- Keep the immutable STRICT DIRECTIVE MODE header verbatim.
- Add the topic table pointing to `guidelines/` files (updated for SNEA: no `07-persistence.md` row, memory file
  updated to `memory.md`).
- Add SNEA-specific sections not covered by any topic file:
  - **UI Patterns** (sidebar controls, icon buttons, MDF rendering, diff icons, line indicators)
  - **MDF Standards** (record spacing, core tags, non-enforcement policy, no fallback languages, tag integrity)
  - **Ethics** (Nation Sovereignty)
  - **Development Workflow** (Streamlit lifecycle scripts, port protocol, migration versioning `YYYYMMDDSSSSS`)
  - **VCS** (declarative commit protocol — absolute prohibition, user-only responsibility)
  - **Initialization** (re-read guidelines, acknowledge, update memory)
- Remove content from `guidelines.md` that is now canonical in a topic file (approval gate, scope, tool usage,
  environment, code standards, data integrity, git protocol, authority source, scripting).

### 7. ⏳ Delete `guidelines (copy).md`
Remove `.junie/guidelines (copy).md` — it was the source template and is superseded by the updated `guidelines.md`.

### 8. ⏳ Update topic table row for `07-persistence.md`
The topic table in `guidelines.md` must not reference the archived persistence file.
Add a placeholder row noting SNEA persistence guidelines are pending, or omit the row entirely.

---

## Files Modified
| File | Action |
|------|--------|
| `.junie/guidelines/07-persistence.md` | Move → `.junie/guidelines/archive/07-persistence.newsrx.md` |
| `.junie/guidelines/09-scripting.md` | Trim notebook/papermill section |
| `.junie/guidelines/05-code-standards.md` | Trim newsrx pipeline + NLP bullets |
| `.junie/guidelines/06-data-integrity.md` | Trim newsrx archive-specific bullets |
| `.junie/LONG_TERM_MEMORY.md` | Archive → `.junie/archive/LONG_TERM_MEMORY.archived.md` |
| `.junie/memory.md` | Create new structured key:value memory file |
| `.junie/guidelines.md` | Replace with topic-file architecture + SNEA-specific sections |
| `.junie/guidelines (copy).md` | Delete (superseded) |
