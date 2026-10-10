# SPEC: AI Agent Ready Progressive Read Markdown Format for MDF Master Doc

## Intent / Executive Summary

Convert the MDF 1.9a master documentation (`docs/mdf/MDFields19a_UTF8.txt`) from Toolbox/Shoebox help format into a structured, progressively readable Markdown directory optimized for AI agent consumption. The output uses markdown-native navigation (links, frontmatter, anchors) — no JSON files, no conversion tooling — with token-efficient chunking for LLM context windows. The migrated Markdown becomes the maintained source of truth for MDF field documentation.

## Root Cause

The source file is a monolithic Toolbox-format help database (130,520 bytes; fields may wrap onto continuation lines). AI agents cannot efficiently read the single file in one pass — they need progressive disclosure: a top-level index, per-marker detail files, and topic discussions, each independently loadable via `read_file`. Association between related areas is further organized by separation of concerns — independent of semantic grouping — so agents can enter by intent (marker lookup, job-framed task, or cross-cutting topic) rather than by the author's semantic intuition alone.

## Approach

Progressive read structure with independent association axes:

- **Level 1** (`index.md`): TOC with all `\key` marker codes as markdown links to Level 2 files, one-line summaries, token budget < 2k tokens
- **Level 2** (`markers/{code}.md`): One file per entry with full definition, hierarchy, examples, cross-refs as markdown links resolving to the target entry's detail file, and fixed `##` sections — one per concern the entry participates in
- **Level 3 — concern views** (`concerns/{concern}.md`): the separation-of-concerns axis — thin slices across all entries for structure, semantics, presentation, and data-handling, linking into entry section anchors
- **Level 3 — semantic topics** (`topics/{topic}.md`): topic discussions (hierarchy variants, formatting, character styles, etc.)
- **Cross-reference graph**: bidirectional `\cf`-derived links and backlinks between entry files

Each entry point is independently loadable — an agent reads only what its intent needs.

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Single large Markdown file | Exceeds LLM context window for full read; no progressive disclosure |
| JSON-based navigation | LLMs navigate markdown links more reliably than JSON parsing; violates SC-6 |
| Database (SQLite) | Adds dependency; markdown is zero-dependency and universally readable |
| Split by section only | Loses per-entry granularity needed for targeted lookups |
| Maintained converter / reverse-converter pipeline | The source is frozen (see Source); a standing pipeline has no recurring input and adds machinery the documentation does not need |

## Key Decisions

1. **Markdown-only output**: No JSON, no database — all navigation via markdown links and frontmatter
2. **Per-entry files**: Each `\key` entry gets its own file under `markers/` for atomic loading, named for the entry's first code; a multi-code entry is one entry whose file covers all its codes, with the frontmatter `marker` field listing them
3. **Bidirectional cross-refs**: `\cf` references become forward links in the referencing entry's detail file + a backlinks section in the target entry's detail file
4. **Frontmatter YAML**: Every entry file includes `marker`, `category`, `hierarchy_level`, `concerns`, `cross_refs`, `tokens_estimate` for agent parsing
5. **Token budgets**: Each chunk < 4k tokens; Level 1 index < 2k tokens. Token counts throughout this spec are measured as ⌈bytes ÷ 4⌉ (`wc -c` / 4)
6. **Static source, Markdown as source of truth**: The source is frozen (authoritative last-modified 2006-05-12 per `docs/mdf/SOURCE-PROVENANCE.md`); content is migrated once during implementation; after migration the Markdown files are edited directly, and the Toolbox original remains in-repo as frozen provenance, never written to
7. **Separation-of-concerns axis**: Concern views (`structure`, `semantics`, `presentation`, `data-handling`) associate entries by the job the documentation content performs, independent of the semantic grouping in `topics/`; concern membership is declared in frontmatter and verified for consistency

## Source

`docs/mdf/MDFields19a_UTF8.txt` — 130,520-byte Toolbox-format database (UTF-8; fields begin with a `\marker` and may wrap onto continuation lines) with:

- 108 `\key` entries (lines beginning with `\key`), carrying 121 distinct codes; each code names exactly one entry — one entry (the verb paradigm markers, `\key 1s 1p 1e 1i 1d 2s 2p 2d 3s 3p 3d 4s 4p 4d`) carries fourteen codes, every other entry one
- 297 `\cf` cross-reference lines (lines beginning with `\cf`)
- 425 `\ftx` example fields (lines beginning with `\ftx`; 11 of these carry no example content)
- Other markers present include: `\shd`, `\shd2`, `\shd3`, `\shd4`, `\txt`, `\fxv`, `\nt`, `\nwt`, `\bib`, `\typ`

**Static source.** The document self-dates to May 12, 2006 (draft version 1.9a, in preparation for "version 2"), and `docs/mdf/SOURCE-PROVENANCE.md` records the authoritative last-modified date as 2006-05-12. The source is frozen legacy: it receives no updates, so migration is one-time and no conversion tooling is part of the deliverable.

**Content units.** A `\key` entry block is its `\key` line through the line preceding the next line beginning with `\key`, continuation lines included. A `\cf` field and an `\ftx` field each comprise their marker line plus the immediately following non-blank lines that do not begin with `\`. The file preamble is every line before the first `\key` line. Content comparisons normalize horizontal whitespace runs to single spaces; every other character compares exactly.

**Cross-reference derivation.** A `\cf` field's whitespace-separated tokens name cross-reference targets as follows:

1. A token beginning with `\` names the `\key` entry whose code equals the token with its leading `\` and trailing punctuation removed.
2. A token containing `*` names the marker family listed for it in the star-family table below; a `*` token not listed there names nothing.
3. A bare token — no `\`, no `*` — names the `\key` entry whose code equals the token with its surrounding punctuation removed only when it stands at a reference position: a token that begins its line within the field, a token preceded by a whitespace run of two or more characters, a token immediately preceded by a comma, or a code-equal token inside a parenthetical that itself contains a comma. Code-equal bare tokens elsewhere are description prose and name nothing.

**Star families.** Families follow the source's own notation note (a starred marker denotes the set of language markers for the same field across language variants — the note documents `de*` as `dv`, `dn`, `dr`, `de`) and the marker series the source's entries present:

| Star token | Family (`\key` codes) |
|------------|------------------------|
| `de*` | de, dn, dr, dv |
| `ee*` | ee, en, er, ev |
| `ge*` | ge, gn, gr, gv |
| `lv*` | lf, le, ln, lr, lv |
| `oe*` | oe, on, or, ov |
| `pdv*` | pd, pde, pdl, pdn, pdr, pdv |
| `re*` | re, rn, rr |
| `ue*` | ue, un, ur, uv |
| `va*` | va, ve, vn, vr |
| `ve*` | va, ve, vn, vr |
| `we*` | we, wn, wr |
| `xv*` | xe, xn, xr, xv |

Measured token composition across the 297 `\cf` fields (marker lines plus continuations, 1,018 tokens): 298 backslash-prefixed, 16 `*`-family occurrences across the 12 listed families, 106 bare references, 598 prose tokens; no token combines the backslash and `*` forms, and every backslash and family token resolves to at least one `\key` code.

## Output Structure

```
docs/mdf/ai-progressive/
├── index.md                    # Level 1: TOC + summary table of all `\key` entries with links
├── markers/
│   ├── lx.md                   # Level 2: \lx detail with frontmatter
│   ├── ge.md
│   ├── ps.md
│   └── ... (one file per `\key` entry, named for the entry's first code)
├── concerns/
│   ├── structure.md            # Level 3: separation-of-concerns view
│   ├── semantics.md
│   ├── presentation.md
│   └── data-handling.md
├── topics/
│   ├── hierarchy-standard.md
│   ├── hierarchy-alternate.md
│   ├── formatting-printing.md
│   ├── character-styles.md
│   ├── range-sets.md
│   └── old-changed-markers.md
└── README.md                   # Navigation guide for agents
```

The project-local entry-point card `docs/agents/mdf-progressive.md` routes agents into this structure by intent (see Affected Files).

## Affected Files

| File / Directory | Action | Description |
|------------------|--------|-------------|
| `docs/mdf/ai-progressive/` | Create | Output directory — tracked deliverable containing all generated Markdown files |
| `docs/mdf/ai-progressive/index.md` | Create | Level 1 TOC with all `\key` entries |
| `docs/mdf/ai-progressive/markers/*.md` | Create | Level 2 per-entry detail files (one per `\key` entry) |
| `docs/mdf/ai-progressive/concerns/*.md` | Create | Level 3 separation-of-concerns views (structure, semantics, presentation, data-handling) |
| `docs/mdf/ai-progressive/topics/*.md` | Create | Level 3 semantic topic discussion files |
| `docs/mdf/ai-progressive/README.md` | Create | Navigation guide for agents |
| `docs/agents/mdf-progressive.md` | Create | Project-local entry-point card: intent-based routing into the progressive structure across READ / WRITE / PLAN / VERIFY modes |

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC-1 | Every `\key` entry in the source file has an individual detail file under `markers/` — named for the entry's first `\key` code, with frontmatter containing `marker` (the entry's code or codes), `category`, `hierarchy_level`, `concerns`, `cross_refs`, and `tokens_estimate` | `structural` | Mechanical comparison: the set of detail files equals the set of `\key` entries extracted from the source file (file name = entry's first code); each file parses as valid YAML frontmatter carrying all 6 required fields |
| SC-2 | Level 1 `index.md` loads in < 2,000 tokens under the token measure defined in Key Decisions | `string` | Token measure (⌈bytes ÷ 4⌉) of `index.md` < 2,000 tokens |
| SC-3 | Every cross-reference derived from the source's `\cf` fields under the Cross-reference derivation rule is resolved bidirectionally: the referencing entry's detail file contains a forward link resolving to the target entry's detail file, and the target entry's detail file contains a `## Backlinks` section listing the referencing entry | `structural` | Mechanical comparison with no hardcoded totals: extract the (source entry → target entry) pair set from the source's `\cf` fields per the Cross-reference derivation rule (a reference to any of an entry's codes targets that entry); extract the forward-link pair set by resolving every markdown link in each `markers/*.md` outside its `## Backlinks` section to the entry whose detail file it names; extract the backlink pair set from each file's `## Backlinks` section; the source pair set must equal the forward-link set, and the backlink set must equal its inverse |
| SC-4 | Token estimates in frontmatter (`tokens_estimate`) are within ±20% of the file's actual token count under the token measure defined in Key Decisions, for every generated file | `structural` | Mechanical check over every generated file under `docs/mdf/ai-progressive/`: compute the token measure (⌈bytes ÷ 4⌉) and verify `tokens_estimate` is within ±20% of it for each file; no sampling |
| SC-5 | Migration acceptance (one-time, performed during implementation): the migrated Markdown faithfully captures the source — a fresh-context reviewer compares a minimum of 15 `\key` entries sampled across the source file, each between its `markers/{code}.md` and the corresponding source entry block (definition text, hierarchy placement, `\ftx` examples, `\cf` cross-references), and reports no content divergence; and the source file is left unmodified (git diff over `MDFields19a_UTF8.txt` is empty) | `semantic` | Fresh-context acceptance review with the stated sample minimum, plus a git-diff check confirming the source file unmodified |
| SC-6 | Zero JSON files in `docs/mdf/ai-progressive/` — all navigation via markdown links and frontmatter | `string` | `find docs/mdf/ai-progressive/ -name '*.json'` returns empty |
| SC-7 | All generated Markdown files are written to `docs/mdf/ai-progressive/`: `index.md`, one `markers/{code}.md` per `\key` entry in the source, the four `concerns/` views, the `topics/` files listed in Output Structure, and `README.md` | `structural` | The `markers/` file set equals the set of `\key` entries extracted from the source (file name = entry's first code); `index.md`, the four `concerns/` files, the enumerated `topics/` files, and `README.md` exist on disk |
| SC-8 | The output directory `docs/mdf/ai-progressive/` is committed to the repository (not gitignored) so that other specs can reference individual entry files as artifacts | `structural` | `git ls-files docs/mdf/ai-progressive/` lists every generated file: the tracked file set equals the generated on-disk file set, with no generated file ignored or untracked |
| SC-9 | Concern-view consistency: `concerns/` contains exactly `structure.md`, `semantics.md`, `presentation.md`, and `data-handling.md`; for every concern, the set of entries listed in the view equals the set of entries whose frontmatter `concerns` field includes that concern; and every concern-view link into an entry file resolves to that entry file and to a section corresponding to a concern the entry declares | `structural` | Mechanical comparison over the generated Markdown with no hardcoded totals: extract concern membership from entry frontmatter and from each view's entry list; the two sets must be equal per concern; verify every view link target exists and its anchor corresponds to a declared concern section of the target entry |
| SC-10 | Entry-point card: `docs/agents/mdf-progressive.md` exists, is tracked in git, and every concrete repository path it references exists | `structural` | `git ls-files docs/agents/mdf-progressive.md` lists the file; extract every concrete repo-relative path referenced in the card (brace pattern notation such as `markers/{code}.md` is not a concrete path) and verify each exists on disk |

## Implementation Phases

### Phase 1: One-Time Migration & Index Generation
- Transform the source content into the progressive structure (throwaway transformation steps during implementation are permitted; no conversion program is delivered as a project artifact), carrying `\key`, `\cf`, and `\ftx` fields per the Content units definitions and all remaining field content — including `\shd`, `\shd2`, `\shd3`, `\shd4`, `\txt`, `\fxv`, `\nt`, `\nwt`, `\bib`, `\typ` — verbatim within entry blocks
- Generate `index.md` with all `\key` entries as a markdown table
- Verify SC-2 (index < 2k tokens)

### Phase 2: Per-Entry File Production
- Produce one `markers/{code}.md` file per `\key` entry with full frontmatter
- Include definition, hierarchy, examples, cross-refs, and one `##` section per declared concern
- Verify SC-1 (detail files with frontmatter)

### Phase 3: Cross-Reference Resolution
- Resolve every `\cf` cross-reference bidirectionally per the Cross-reference derivation rule, including the star-family table
- Add backlinks sections to each target file
- Verify SC-3 (bidirectional resolution)

### Phase 4: Concern Views & Topic Files
- Generate the four concern views under `concerns/` and the topic files under `topics/`
- Compute and embed `tokens_estimate` in frontmatter
- Verify SC-4 (token estimate accuracy) and SC-9 (concern-view consistency)

### Phase 5: Migration Acceptance Review
- Fresh-context acceptance review per SC-5: sampled entry comparison against the frozen source; source-file-unmodified check
- Verify SC-5 (migration acceptance)

### Phase 6: Entry Card & Final Verification
- Write the entry-point card `docs/agents/mdf-progressive.md`
- Remove any JSON artifacts
- Verify SC-6 (zero JSON files), SC-7 (all files present), SC-8 (tracked deliverable), SC-10 (entry card)
- Run full SC audit

## Requirements → SCs → Phases Traceability

| Requirement | SC ID | Phase |
|-------------|-------|-------|
| Every `\key` entry has an individual detail file with frontmatter | SC-1 | Phase 2 |
| Level 1 index loads in < 2,000 tokens | SC-2 | Phase 1 |
| Every `\cf` cross-reference resolved bidirectionally | SC-3 | Phase 3 |
| Token estimates within ±20% of actual for every generated file | SC-4 | Phase 4 |
| One-time migration acceptance; source left unmodified | SC-5 | Phase 5 |
| Zero JSON files in output directory | SC-6 | Phase 6 |
| All generated files written to `docs/mdf/ai-progressive/` | SC-7 | Phase 6 |
| Output directory committed to repository (not gitignored) | SC-8 | Phase 6 |
| Concern views consistent with declared frontmatter membership | SC-9 | Phase 4 |
| Entry-point card present, tracked, with resolving path references | SC-10 | Phase 6 |

## Type

SPEC (AI agent documentation format — markdown native)

## Change Control

| Date | Change | Reason | Authorized By |
|------|--------|--------|---------------|
| 2026-07-26 | Complete revision: added preamble sections (Intent, Root Cause, Approach, Alternatives, Key Decisions), evidence type declarations, verification methods, phase decomposition; tightened SC wording; fixed marker count from "100+" to 108; added cross-ref counts (315 lines) and example count (425) | Spec audit returned DRAFT — 6 defects remediated | Spec audit findings |
| 2026-07-26 | Fix 6 validation defects: (1) SC-5 clarified with concrete sub-checks (108 \key, 315 \cf, 414 \ftx); (2) "299 unique \cf targets" changed to "315 \cf cross-ref lines"; (3) added Requirements→SCs→Phases traceability table; (4) SC-5 documented as composite check with 3 sub-checks; (5) SC-1 evidence type changed from string to structural; (6) \ftx count corrected from 425 to 414 | Validation findings from spec revision | Validation findings |
| 2026-07-26 | Added SC-7 (output directory tracking) and SC-8 (committed artifact repository); added Affected Files section; updated traceability table; appended change control entry | Revision request: add output directory as tracked deliverable for downstream spec artifact consumption | Developer request |
| 2026-10-10 | Count-independent criteria: SC-3 and SC-5 redefined to derive completeness from the source data (set/multiset equality between source-derived extractions and output content) instead of hardcoded totals; same instrument normalization applied to SC-1, SC-7, SC-8; source facts corrected to measured values (130,520 bytes, 108 \key, 297 \cf, 425 \ftx) with explicit measurement definitions; added Cross-reference derivation rule for `*` family patterns; synced spec.md artifact with issue body | Spec audit FAIL: count-dependent instruments are false measures; artifact divergence (spec.md superseded by issue body) | Developer direction on audit findings |
| 2026-10-10 | Static-source reframe: Key Decision 6 replaced — Markdown is the post-migration source of truth, source frozen at 2006-05-12 per `docs/mdf/SOURCE-PROVENANCE.md`; SC-5 reframed from standing round-trip conversion check to one-time migration acceptance review (with source-unmodified check); reverse-converter removed from Phases; Phase 1 reframed as one-time migration with no delivered conversion program; added separation-of-concerns axis (`concerns/` views, `concerns` frontmatter field, per-concern `##` sections) with SC-9; added entry-point card `docs/agents/mdf-progressive.md` with SC-10; noted 11 empty `\ftx` fields; converter pipeline recorded as rejected alternative | Developer direction: MDF documentation is static legacy (last published 2006-05-12) — no conversion machinery; association by separation of concerns; single intent-based entry-point card | Developer direction |
| 2026-10-10 | Validation remediation: Cross-reference derivation rule completed — backslash-prefixed token form made explicit (298 occurrences, the dominant reference form), star-family enumeration pinned to 12 families with `lv*` (source-notation-derived, all family codes verified present), bare-token reference positions defined (line-initial, ≥2-space column break, comma-preceded, or code-equal inside a comma-containing parenthetical) with the 7 prose false-positives (`or`, `on` in running text) excluded; token measure pinned to ⌈bytes ÷ 4⌉ throughout, removing the tokenizer-or-heuristic either/or; SC-4 reclassified from sampled semantic check to per-file structural check (no sampling); entry-block/field/preamble Content units definitions added (field continuations carry cross-reference tokens, e.g. `lv*`); multi-code entry fact added (108 entries, 121 codes; verb paradigm entry carries 14 codes) with file-naming by first code in SC-1/SC-7; marker inventory extended (`\shd2`, `\shd3`, `\shd4`, `\nwt`, `\bib`); SC-10 concrete-path clarification | Validation FAIL: SC-3 ambiguous (class 4), SC-4 misclassified evidence (class 5); live source verification during validation | Validation findings, developer-directed revision |

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
