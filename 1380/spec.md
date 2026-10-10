# SPEC: AI Agent Ready Progressive Read Markdown Format for MDF Master Doc

## Intent / Executive Summary

Convert the MDF 1.9a master documentation (`docs/mdf/MDFields19a_UTF8.txt`) from Toolbox/Shoebox help format into a structured, progressively readable Markdown directory optimized for AI agent consumption. The output uses markdown-native navigation (links, frontmatter, anchors) — no JSON files — with token-efficient chunking for LLM context windows.

## Root Cause

The source file is a monolithic Toolbox-format help database (one field per line, 130,520 bytes). AI agents cannot efficiently read the single file in one pass — they need progressive disclosure: a top-level index, per-marker detail files, and topic discussions, each independently loadable via `read_file`.

## Approach

Three-level progressive read structure:

- **Level 1** (`index.md`): TOC with all `\key` marker codes as markdown links to Level 2 files, one-line summaries, token budget < 2k tokens
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
3. **Bidirectional cross-refs**: `\cf` references become forward links in the referencing entry's detail file + a backlinks section in the target entry's detail file
4. **Frontmatter YAML**: Every file includes `marker`, `category`, `hierarchy_level`, `cross_refs`, `tokens_estimate` for agent parsing
5. **Token budgets**: Each chunk < 4k tokens; Level 1 index < 2k tokens
6. **Source fidelity**: Toolbox format fully preserved — round-trip conversion must be possible

## Source

`docs/mdf/MDFields19a_UTF8.txt` — 130,520-byte Toolbox-format database (UTF-8, one field per line) with:

- 108 `\key` entries (lines beginning with `\key`; each entry's code is unique)
- 297 `\cf` cross-reference lines (lines beginning with `\cf`)
- 425 `\ftx` example fields (lines beginning with `\ftx`)
- Additional markers: `\shd`, `\txt`, `\fxv`, `\nt`, `\typ`

**Cross-reference derivation.** A `\cf` field names its cross-reference targets as whitespace-separated tokens: a token that equals a `\key` code names that entry; a token ending in `*` (e.g. `de*`, `ue*`) names the family of all `\key` codes beginning with the token's prefix; surrounding punctuation and description prose name nothing.

## Output Structure

```
docs/mdf/ai-progressive/
├── index.md                    # Level 1: TOC + summary table of all `\key` entries with links
├── markers/
│   ├── lx.md                   # Level 2: \lx detail with frontmatter
│   ├── ge.md
│   ├── ps.md
│   └── ... (one file per `\key` entry)
├── topics/
│   ├── hierarchy-standard.md
│   ├── hierarchy-alternate.md
│   ├── formatting-printing.md
│   ├── character-styles.md
│   ├── range-sets.md
│   └── old-changed-markers.md
└── README.md                   # Navigation guide for agents
```

## Affected Files

| File / Directory | Action | Description |
|------------------|--------|-------------|
| `docs/mdf/ai-progressive/` | Create | Output directory — tracked deliverable containing all generated Markdown files |
| `docs/mdf/ai-progressive/index.md` | Create | Level 1 TOC with all `\key` entries |
| `docs/mdf/ai-progressive/markers/*.md` | Create | Level 2 per-marker detail files (one per `\key` entry) |
| `docs/mdf/ai-progressive/topics/*.md` | Create | Level 3 topic discussion files |
| `docs/mdf/ai-progressive/README.md` | Create | Navigation guide for agents |

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC-1 | Every `\key` entry in the source file has an individual detail file under `markers/` with frontmatter containing `marker`, `category`, `hierarchy_level`, `cross_refs`, and `tokens_estimate` | `structural` | Script comparison: the set of files under `docs/mdf/ai-progressive/markers/` equals the set of `\key` codes extracted from the source file; each file parses as valid YAML frontmatter carrying all 5 required fields |
| SC-2 | Level 1 `index.md` loads in < 2,000 tokens (measured by `wc -c` / 4 character-per-token heuristic or tokenizer) | `string` | Token count of `index.md` < 2,000 tokens |
| SC-3 | Every cross-reference expressed in the source's `\cf` fields is resolved bidirectionally: for each (source entry → target) pair derived under the Cross-reference derivation rule, the source entry's detail file contains a forward link to the target entry's detail file, and the target entry's detail file contains a `## Backlinks` section listing the source entry | `structural` | Script comparison with no hardcoded totals: extract the (source → target) pair set from the source's `\cf` fields per the derivation rule; extract the forward-link pair set and the backlink pair set from the generated `markers/*.md`; the source pair set must equal the forward-link set, and the backlink set must equal its inverse |
| SC-4 | Token estimates in frontmatter (`tokens_estimate`) are within ±20% of actual token count for each file | `semantic` | Sub-agent reads 10 randomly sampled files and verifies `tokens_estimate` vs actual token count |
| SC-5 | Source Toolbox content is preserved through round-trip conversion (Toolbox → Markdown → Toolbox). Composite check with 3 sub-checks, each passing independently: (a) every `\key` entry block is reproduced with identical content, (b) every `\cf` cross-reference line is reproduced with identical content, (c) every `\ftx` example is reproduced with identical content | `behavioral` | Run the conversion script on the source, then the reverse script on the output; extract the multiset of `\key` entry blocks, of `\cf` lines, and of `\ftx` examples from both the original source and the round-trip output; each sub-check requires multiset equality between the original and round-trip extractions |
| SC-6 | Zero JSON files in `docs/mdf/ai-progressive/` — all navigation via markdown links and frontmatter | `string` | `find docs/mdf/ai-progressive/ -name '*.json'` returns empty |
| SC-7 | All generated Markdown files are written to `docs/mdf/ai-progressive/`: `index.md`, one `markers/{code}.md` per `\key` entry in the source, the `topics/` files listed in Output Structure, and `README.md` | `structural` | The `markers/` file set equals the source's `\key` code set (script comparison); `index.md`, the enumerated `topics/` files, and `README.md` exist on disk |
| SC-8 | The output directory `docs/mdf/ai-progressive/` is committed to the repository (not gitignored) so that other specs can reference individual marker files as artifacts | `structural` | `git ls-files docs/mdf/ai-progressive/` lists every generated file: the tracked file set equals the generated on-disk file set, with no generated file ignored or untracked |

## Implementation Phases

### Phase 1: Parser & Index Generation
- Build a parser for the Toolbox format that extracts `\key`, `\cf`, `\ftx`, `\shd`, `\txt`, `\fxv`, `\nt`, `\typ` markers
- Generate `index.md` with all `\key` entries as a markdown table
- Verify SC-2 (index < 2k tokens)

### Phase 2: Per-Marker File Generation
- Generate one `markers/{code}.md` file per `\key` entry with full frontmatter
- Include definition, hierarchy, examples, and cross-refs
- Verify SC-1 (detail files with frontmatter)

### Phase 3: Cross-Reference Resolution
- Resolve every `\cf` cross-reference bidirectionally per the Cross-reference derivation rule
- Add backlinks sections to each target file
- Verify SC-3 (bidirectional resolution)

### Phase 4: Topic Files & Token Budgets
- Generate topic-level files under `topics/`
- Compute and embed `tokens_estimate` in frontmatter
- Verify SC-4 (token estimate accuracy)

### Phase 5: Round-Trip Verification
- Implement reverse conversion (Markdown → Toolbox)
- Run the round-trip test over all `\key` entries
- Verify SC-5 (round-trip fidelity)

### Phase 6: Cleanup & Final Verification
- Remove any JSON artifacts
- Verify SC-6 (zero JSON files)
- Verify SC-7 (all files present in output directory)
- Verify SC-8 (output directory committed and tracked)
- Run full SC audit

## Requirements → SCs → Phases Traceability

| Requirement | SC ID | Phase |
|-------------|-------|-------|
| Every `\key` entry has an individual detail file with frontmatter | SC-1 | Phase 2 |
| Level 1 index loads in < 2,000 tokens | SC-2 | Phase 1 |
| Every `\cf` cross-reference resolved bidirectionally | SC-3 | Phase 3 |
| Token estimates within ±20% of actual | SC-4 | Phase 4 |
| Round-trip fidelity: `\key`, `\cf`, `\ftx` content preserved | SC-5 | Phase 5 |
| Zero JSON files in output directory | SC-6 | Phase 6 |
| All generated files written to `docs/mdf/ai-progressive/` | SC-7 | Phase 6 |
| Output directory committed to repository (not gitignored) | SC-8 | Phase 6 |

## Type

SPEC (AI agent documentation format — markdown native)

## Change Control

| Date | Change | Reason | Authorized By |
|------|--------|--------|---------------|
| 2026-07-26 | Complete revision: added preamble sections (Intent, Root Cause, Approach, Alternatives, Key Decisions), evidence type declarations, verification methods, phase decomposition; tightened SC wording; fixed marker count from "100+" to 108; added cross-ref counts (315 lines) and example count (425) | Spec audit returned DRAFT — 6 defects remediated | Spec audit findings |
| 2026-07-26 | Fix 6 validation defects: (1) SC-5 clarified with concrete sub-checks (108 \key, 315 \cf, 414 \ftx); (2) "299 unique \cf targets" changed to "315 \cf cross-ref lines"; (3) added Requirements→SCs→Phases traceability table; (4) SC-5 documented as composite check with 3 sub-checks; (5) SC-1 evidence type changed from string to structural; (6) \ftx count corrected from 425 to 414 | Validation findings from spec revision | Validation findings |
| 2026-07-26 | Added SC-7 (output directory tracking) and SC-8 (committed artifact repository); added Affected Files section; updated traceability table; appended change control entry | Revision request: add output directory as tracked deliverable for downstream spec artifact consumption | Developer request |
| 2026-10-10 | Count-independent criteria: SC-3 and SC-5 redefined to derive completeness from the source data (set/multiset equality between source-derived extractions and output content) instead of hardcoded totals; same instrument normalization applied to SC-1, SC-7, SC-8; source facts corrected to measured values (130,520 bytes, 108 \key, 297 \cf, 425 \ftx) with explicit measurement definitions; added Cross-reference derivation rule for `*` family patterns; synced spec.md artifact with issue body | Spec audit FAIL: count-dependent instruments are false measures; artifact divergence (spec.md superseded by issue body) | Developer direction on audit findings |

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
