# SPEC: AI Agent Ready Progressive Read Markdown Format for MDF Master Doc

## Intent / Executive Summary

Convert the MDF 1.9a master documentation (`docs/mdf/MDFields19a_UTF8.txt`) from Toolbox/Shoebox help format into a structured, progressively readable Markdown directory optimized for AI agent consumption. The output uses markdown-native navigation (links, frontmatter, anchors) — no JSON files — with token-efficient chunking for LLM context windows.

## Root Cause

The source file is a monolithic Toolbox-format help database (133KB, 108 `\key` entries, 315 `\cf` cross-ref lines, 414 `\ftx` examples). AI agents cannot efficiently read a single 133KB file — they need progressive disclosure: a top-level index, per-marker detail files, and topic discussions, each independently loadable via `read_file`.

## Approach

Three-level progressive read structure:

- **Level 1** (`index.md`): TOC with all 108 marker codes as markdown links to Level 2 files, one-line summaries, token budget < 2k tokens
- **Level 2** (`markers/{code}.md`): One file per marker with full definition, hierarchy, examples, cross-refs as `[text](#anchor)` links
- **Level 3** (`topics/{topic}.md`): Topic discussions (hierarchy, formatting, character styles, etc.)

Each level independently loadable — agent reads only what it needs.

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Single large Markdown file | Exceeds LLM context window for full read; no progressive disclosure |
| JSON-based navigation | LLMs navigate markdown links more reliably than JSON parsing; violates SC-6 |
| Database (SQLite) | Adds dependency; markdown is zero-dependency and universally readable |
| Split by section only | Loses per-marker granularity needed for targeted lookups |

## Key Decisions

1. **Markdown-only output**: No JSON, no database — all navigation via markdown links and frontmatter
2. **Per-marker files**: Each `\key` entry gets its own file under `markers/` for atomic loading
3. **Bidirectional cross-refs**: `\cf` references become forward links in the source file + backlinks section in the target file
4. **Frontmatter YAML**: Every file includes `marker`, `category`, `hierarchy_level`, `cross_refs`, `tokens_estimate` for agent parsing
5. **Token budgets**: Each chunk < 4k tokens; Level 1 index < 2k tokens
6. **Source fidelity**: Toolbox format fully preserved — round-trip conversion must be possible

## Source

`docs/mdf/MDFields19a_UTF8.txt` — 133KB Toolbox format with:
- 108 `\key` entries (unique marker codes)
- 315 `\cf` cross-reference lines
- 414 `\ftx` example fields
- Additional markers: `\shd`, `\txt`, `\fxv`, `\nt`, `\typ`

## Output Structure

```
docs/mdf/ai-progressive/
├── index.md                    # Level 1: TOC + all 108 markers summary table with links
├── markers/
│   ├── lx.md                   # Level 2: \lx detail with frontmatter
│   ├── ge.md
│   ├── ps.md
│   └── ... (108 files)
├── topics/
│   ├── hierarchy-standard.md
│   ├── hierarchy-alternate.md
│   ├── formatting-printing.md
│   ├── character-styles.md
│   ├── range-sets.md
│   └── old-changed-markers.md
└── README.md                   # Navigation guide for agents
```

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC-1 | All 108 `\key` entries from the source file have individual detail files under `markers/` with frontmatter containing `marker`, `category`, `hierarchy_level`, `cross_refs`, and `tokens_estimate` | `structural` | `ls docs/mdf/ai-progressive/markers/ | wc -l` yields 108; each file has valid YAML frontmatter with all 5 required fields |
| SC-2 | Level 1 `index.md` loads in < 2,000 tokens (measured by `wc -c` / 4 character-per-token heuristic or tokenizer) | `string` | Token count of `index.md` < 2,000 tokens |
| SC-3 | All 315 `\cf` cross-ref lines are resolved bidirectionally: forward links in the source file point to the target marker file, and each target file has a backlinks section listing all sources that reference it | `string` | Count of markdown links in `markers/` files matching `\cf` targets = 315; each target file has a `## Backlinks` section with matching count |
| SC-4 | Token estimates in frontmatter (`tokens_estimate`) are within ±20% of actual token count for each file | `semantic` | Sub-agent reads 10 randomly sampled files and verifies `tokens_estimate` vs actual token count |
| SC-5 | Source Toolbox format is fully preserved — a round-trip conversion (Toolbox → Markdown → Toolbox) reproduces the original content without data loss. Composite check with 3 sub-checks: (a) all 108 `\key` entries present in Markdown output with identical content, (b) all 315 `\cf` cross-ref lines present with identical content, (c) all 414 `\ftx` examples present with identical content | `behavioral` | Run conversion script on source, then reverse script on output; diff shows zero semantic differences for all `\key`, `\cf`, and `\ftx` content. Each sub-check (a/b/c) must pass independently |
| SC-6 | Zero JSON files in `docs/mdf/ai-progressive/` — all navigation via markdown links and frontmatter | `string` | `find docs/mdf/ai-progressive/ -name '*.json'` returns empty |

## Implementation Phases

### Phase 1: Parser & Index Generation
- Build a parser for the Toolbox format that extracts `\key`, `\cf`, `\ftx`, `\shd`, `\txt`, `\fxv`, `\nt`, `\typ` markers
- Generate `index.md` with all 108 markers as a markdown table
- Verify SC-2 (index < 2k tokens)

### Phase 2: Per-Marker File Generation
- Generate one `markers/{code}.md` file per `\key` entry with full frontmatter
- Include definition, hierarchy, examples, and cross-refs
- Verify SC-1 (108 files with frontmatter)

### Phase 3: Cross-Reference Resolution
- Resolve all 315 `\cf` cross-refs bidirectionally
- Add backlinks sections to each target file
- Verify SC-3 (bidirectional resolution)

### Phase 4: Topic Files & Token Budgets
- Generate topic-level files under `topics/`
- Compute and embed `tokens_estimate` in frontmatter
- Verify SC-4 (token estimate accuracy)

### Phase 5: Round-Trip Verification
- Implement reverse conversion (Markdown → Toolbox)
- Run round-trip test on all 108 markers
- Verify SC-5 (round-trip fidelity)

### Phase 6: Cleanup & Final Verification
- Remove any JSON artifacts
- Verify SC-6 (zero JSON files)
- Run full SC audit

## Requirements → SCs → Phases Traceability

| Requirement | SC ID | Phase |
|-------------|-------|-------|
| All 108 `\key` entries have individual detail files with frontmatter | SC-1 | Phase 2 |
| Level 1 index loads in < 2,000 tokens | SC-2 | Phase 1 |
| All 315 `\cf` cross-ref lines resolved bidirectionally | SC-3 | Phase 3 |
| Token estimates within ±20% of actual | SC-4 | Phase 4 |
| Round-trip fidelity: `\key`, `\cf`, `\ftx` content preserved | SC-5 | Phase 5 |
| Zero JSON files in output directory | SC-6 | Phase 6 |

## Type

SPEC (AI agent documentation format — markdown native)

---

## Change Control

| Date | Change | Reason | Authorized By |
|------|--------|--------|---------------|
| 2026-07-26 | Complete revision: added preamble sections (Intent, Root Cause, Approach, Alternatives, Key Decisions), evidence type declarations, verification methods, phase decomposition; tightened SC wording; fixed marker count from "100+" to 108; added cross-ref counts (315 lines) and example count (425) | Spec audit returned DRAFT — 6 defects remediated | Spec audit findings |
| 2026-07-26 | Fix 6 validation defects: (1) SC-5 clarified with concrete sub-checks (108 \key, 315 \cf, 414 \ftx); (2) "299 unique \cf targets" changed to "315 \cf cross-ref lines"; (3) added Requirements→SCs→Phases traceability table; (4) SC-5 documented as composite check with 3 sub-checks; (5) SC-1 evidence type changed from string to structural; (6) \ftx count corrected from 425 to 414 | Validation findings from spec revision | Validation findings |
