# Plan: #1380 AI Agent Ready Progressive Read Markdown Format for MDF Master Doc

Spec of record: `.issues/1380/spec.md` (issue body mirror; spec revision 2026-10-12 — 11 SCs, precise cross-reference derivation, traceability table). The store's `validation.yaml` verdicts address an earlier 6-SC revision; its named defects (the "299 targets" figure, missing traceability, compound SC-5, ambiguous preservation terms) are all resolved in the current revision, which this plan consumes after judging each SC plannable (all 11 are: mechanical/string criteria carry runnable instruments; SC-5 carries a fresh-context reviewer protocol and a git-diff check).

Branch: `feature/1380-mdf-progressive-read`, base tip `8c4152f` (main, verified up to date with origin/main this session; no submodules — `.gitmodules` empty).

Authorization: `approved for pr: #1380` (2026-10-17) — carries plan → implement → verify → PR under the work card's terminal-stage rule; merge remains human-only.

## Grounding (live this session)

- Source `docs/mdf/MDFields19a_UTF8.txt`: 130,520 bytes, sha256 `06492d5b…`, 108 `\key` lines, 297 `\cf` lines (exactly 1 with a continuation line), 425 `\ftx` lines (11 with no example content) — all re-measured, matching the spec's Source section.
- **Prior workflow reuse (developer-directed).** The HTML/PDF workflow (`scripts/convert_mdf_master.py` → `docs/mdf/build/master.json` → `master.tex`/PDF/`site/`) already parses this exact source: `master.json` (schema `snea-mdf-master/2`) records the source sha256 — verified identical to the live file — and carries all 108 topics as marker-tagged blocks plus `#1431` display labels. Reuse: `parse_mdf_text` block model and `build_slugs`/`derive_display_label`/`derive_shd2_display_text` conventions (imported, like `test/test_mdf_cf_pairs.py` does); `master.json` and the census/round-trip tests as oracles; the HTML pages as rendering precedent. Not reused as-is: the `pairs` field — it is the presentation-gloss derivation (419 pairs, 2026-10-06 change control) — #1380's SC-3 is governed by the spec's own reference-derivation rule (§ Cross-reference derivation), implemented fresh in the generator and cross-checked against the spec's measured census (1,018 tokens: 298 backslash, 16 star-family, 107 bare references, 597 prose) during development; the delivered SC-3 check derives everything live from the source with no hardcoded totals.
- Throwaway transformation lives under `tmp/1380/` (spec Phase 1 permits throwaway steps; no conversion program is delivered — the affected-files list has no code). SC check scripts also live there; their executed output is the evidence.
- `\typ` census: 90 `\typ` lines over 88 entries — Introduction carries three (`<Basic>`, `<Reserved>`, `<Optional>`) as content documenting the type system itself; marker entries `lx`, `xg`, and the verb-paradigm entry carry none. `category` derivation accounts for this (below).
- Hierarchy facts (source-grounded): section-boundary fields are `\lx`, `\ps` (`\pn`), `\sn`, `\se` (Sections_in_a_Lexical_Entry); standard-hierarchy nesting `\ps` → `\sn` ("lower than part of speech") → `\se` ("a further level of hierarchy"); `\hm`/`\lc` "should only occur at the top of the record"; every section "can take a full set of field markers".

## Design decisions (fixed by the plan, applied by the generator)

1. **Content fidelity rule (SC-5).** Entry files preserve source line structure: every content line is emitted as its own line (no paragraph reflow — a newline is not horizontal whitespace, so reflowing would break exact comparison); within each line, horizontal whitespace runs normalize to single spaces (the one transformation the comparison rule allows). `\ftx` and `\fxv` content renders in fenced code blocks (line structure literal). Byte-preserving otherwise: no quote shaping, no escapes — markdown rendering nuances (lone `*`, `<Reserved>` tag-likes) are acceptable; content bytes are what SC-5 compares.
2. **Entry file layout.** Frontmatter → `#` title (the `\shd` heading) → migrated body in source order (each field's content under a small marker label: `\txt`/`\nt`/`\nwt`/`\bib` prose, `\shd2/3/4` as `###`/`####`/`#####` so `##` stays reserved) → `## Cross-references` (forward links, one per derived reference target) → one `## <Concern>` section per declared concern (Structure, Semantics, Presentation, Data handling) → `## Backlinks` (only when inbound references exist — an entry with none omits the section, per SC-3's extraction rule).
3. **Frontmatter derivations** (documented in `README.md`):
   - `marker`: the entry's code or codes (multi-code entry lists all fourteen).
   - `category`: `topic` for the 18 discussion entries (the 17 `chapter_keys` from the `aa` record plus `aa` itself); otherwise the entry's own `\typ` value stripped (`Basic`/`Reserved`/`Optional`); `null` for `lx`, `xg`, and the verb-paradigm entry (the source types them nowhere).
   - `hierarchy_level`: `topic` (discussion entries); `0` `\lx` (record root); `1` `\ps`/`\pn`; `2` `\sn`; `3` `\se`; `record` `\hm`/`\lc` (top of the record only); `any` for every other marker field (sections take a full field set — the source fixes no level).
   - `concerns`: assigned per entry during implementation from the entry's documented role against the four concern definitions (structure = entry/hierarchy organization; semantics = meaning content — definitions, glosses, etymology, paradigms; presentation = print/display — formatting, styles, labels, punctuation; data-handling = data management and process). Multiple declarations allowed. The views are generated from the declarations, so SC-9's set equality holds by construction; the check also verifies every view link's anchor resolves to the declared concern section.
   - `cross_refs`: the entry's derived reference targets (entry keys).
   - `tokens_estimate`: two-pass — generate with a placeholder, measure ⌈bytes÷4⌉ of the final file, substitute; re-verify within ±20% of the final measure (a few bytes of estimate text can never breach the tolerance).
4. **Link hygiene (SC-3 determinism).** Forward links live only in `## Cross-references` (and the index/concern views reference entry files too — outside `markers/*.md`, so outside the forward-set extraction surface); migrated body text stays verbatim and unlinked, so the extracted forward-link pair set is exactly the derived reference set. Backlink lines link the referencing entry's file.
5. **Naming.** `markers/{first-code}.md` (the verb-paradigm entry is `markers/1s.md` covering all fourteen codes). Anchor slugs for concern sections are the plain heading text (`#structure`, `#semantics`, `#presentation`, `#data-handling`).

## Items

### Item 1 (SC-2, Phase 1): Level 1 `index.md`

- Deliverable: `docs/mdf/ai-progressive/index.md` — every `\key` code as a markdown link to its Level 2 file, one-line summaries (display labels from the prior workflow's `#1431` data), compact table to fit the budget.
- RED: the file does not exist — the token-measure check fails on a missing file.
- GREEN: generate `index.md`.
- verify (instrument): `⌈wc -c index.md ÷ 4⌉ < 2000` executed, output captured.

### Item 2 (SC-1, Phase 2): per-entry detail files with frontmatter

- Deliverable: 108 `markers/{first-code}.md` files (file set == `\key` entry set extracted from the source per the Content units rule), each with YAML frontmatter carrying `marker`, `category`, `hierarchy_level`, `concerns`, `cross_refs`, `tokens_estimate`, plus the migrated body and fixed `##` sections per Design decisions 1–3.
- RED: `markers/` does not exist — set-equality and frontmatter checks fail.
- GREEN: generate the entry files (concern sections included; `tokens_estimate` placeholder until Item 5).
- verify (instrument): throwaway check — extract `\key` entries from the source live; assert `markers/` filename set == entry set (first code); parse each file's frontmatter (small strict parser over the six known keys) and assert all six fields present.

### Item 3 (SC-3, Phase 3): bidirectional cross-reference resolution

- Deliverable: every derived reference resolved both ways — `## Cross-references` forward links in referencing files, `## Backlinks` in targets; derivation implements the spec's three rules (backslash tokens stripped of leading `\` and trailing punctuation; star tokens through the 12-family table; bare tokens only at reference positions: line-start within the field, comma-terminated predecessor with intervening whitespace ignored, ≥2-space predecessor run, code-equal token inside a comma-containing parenthetical) over `\cf` fields whose continuations follow the Content units rule.
- RED: with no links/backlinks written, the forward and backlink pair sets are empty while the source pair set is not — the equality assertions fail.
- GREEN: the generator writes both sections.
- verify (instrument): throwaway check deriving all three pair sets live from the source and the generated files (no hardcoded totals): source set == forward set; backlink set == inverse. Development-time assertion (not part of the delivered check): the derivation's token census matches the spec's measured 1,018/298/16/107/597 and every backslash/family token resolves.

### Item 4 (SC-9, Phase 4): concern views + consistency

- Deliverable: `concerns/structure.md`, `semantics.md`, `presentation.md`, `data-handling.md` — generated from the frontmatter declarations, each listing its entries with links to the entries' concern-section anchors.
- RED: `concerns/` does not exist — the consistency check fails.
- GREEN: generate the four views.
- verify (instrument): throwaway check — per concern, view-listed entry set == frontmatter-declared set; every view link resolves to an existing entry file whose declared concerns include the linked concern's section.

### Item 5 (SC-4, Phase 4): token estimates within ±20%

- Deliverable: real `tokens_estimate` values in every entry file's frontmatter (Design decision 3 two-pass, after Items 2–3 fixed the file contents).
- RED: placeholder estimates fail the ±20% check (or the field is absent while files are still unmeasured).
- GREEN: embed measured estimates.
- verify (instrument): throwaway check over every `markers/*.md` — `|tokens_estimate − ⌈bytes÷4⌉|` within ±20% of the actual measure, no sampling.

### Item 6 (SC-11, Phase 4/6): per-file token budget

- Deliverable: every generated file under `docs/mdf/ai-progressive/` under 4,000 tokens (⌈bytes÷4⌉); oversized files (expected risk: large entries like `Order_of_Fields`) get no content loss — the budget is met by the layout's economy; if a file still breaches, the remedy is within-file restructuring that keeps all source content (never truncation).
- RED: files absent / over-budget files fail the check.
- GREEN: generate within budget.
- verify (instrument): throwaway check — max token measure over every generated file < 4,000, per-file values captured.

### Item 7 (SC-5, Phase 5): migration acceptance review (fresh-context)

- Deliverable: a fresh-context reviewer dispatch compares ≥15 `\key` entries sampled across the source file (each between `markers/{first-code}.md` and the source entry block: definition text, hierarchy placement, `\ftx` examples, `\cf` cross-references) and reports no content divergence; plus the git-diff check that the source file is unmodified.
- RED: no deliverable exists to review — the acceptance precondition is absent.
- GREEN: implement Items 1–6, then dispatch the reviewer; any reported divergence is fixed and the sampled re-review repeats.
- verify (instrument): the reviewer's verdict record + `git diff --stat docs/mdf/MDFields19a_UTF8.txt` empty.

### Item 8 (SC-6, Phase 6): zero JSON

- Deliverable: no `.json` files anywhere under `docs/mdf/ai-progressive/` (the throwaway generator must not leak its scratch into the tree).
- RED/GREEN: N/A (generation-hygiene gate, same pattern as Item 12 — the pre-generation tree lacks the directory entirely, so the assertion is meaningful only over the generated set; the generator writes no JSON by construction).
- verify (instrument): `find docs/mdf/ai-progressive/ -name '*.json'` executed post-generation, empty output captured.

### Item 9 (SC-7, Phase 6): complete file set

- Deliverable: `index.md`, the full `markers/` set, the four `concerns/` files, the six enumerated `topics/` files (`hierarchy-standard`, `hierarchy-alternate`, `formatting-printing`, `character-styles`, `range-sets`, `old-changed-markers`), and `README.md` all on disk. Topic files are composed from the source's own discussion content (migrated excerpts with attribution to their source entries) plus links — no invented prose.
- RED: `topics/` and `README.md` do not exist.
- GREEN: generate them.
- verify (instrument): throwaway check — enumerated files exist; `markers/` set equality (shared with Item 2's instrument).

### Item 10 (SC-8, Phase 6): tracked deliverable

- Deliverable: every generated file tracked in git; nothing ignored or untracked.
- RED: before `git add`, `git ls-files docs/mdf/ai-progressive/` is empty while files exist on disk.
- GREEN: stage the directory (commit happens at squash time per the PR shape rule — one commit per issue ticket).
- verify (instrument): `git ls-files docs/mdf/ai-progressive/` set == on-disk generated set, and `git check-ignore` clean.

### Item 11 (SC-10, Phase 6): entry-point card

- Deliverable: `docs/agents/mdf-progressive.md` — intent-based routing into the progressive structure across READ / WRITE / PLAN / VERIFY modes; every concrete repo-relative path it references exists (brace-pattern notation like `markers/{code}.md` allowed and excluded from the existence check per the spec).
- RED: the card does not exist (`docs/agents/` absent).
- GREEN: write the card.
- verify (instrument): `git ls-files docs/agents/mdf-progressive.md` lists it; throwaway check extracts concrete repo-relative paths from the card and verifies each exists on disk.

### Item 12 (PR-boundary gate): full suite green + verify

- Deliverable: the PR pre-create checklist satisfied — full test suite green this session with captured output (designed skips permitted; failures block until remediated or dispositioned), and a fresh-context `verify` PASS against the spec's SCs recorded.
- RED/GREEN: N/A (gate item, #1429-validated pattern).
- verify (instrument): captured pytest summary line + the verify verdict record.
- commit: any residual fixes surfaced; single squashed commit per issue ticket at PR creation.

## Dependency order

1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12. Items 1–2 generate the base structure (index links assume marker filenames exist as named); 3 resolves references over the stable file set; 4 derives views from the settled frontmatter; 5 embeds estimates only after file contents stop changing (Item 3's backlinks are the last byte-changing step for entry files); 6 audits the whole tree; 7 is the semantic gate over the migrated content; 8–11 are the final structural gates; 12 is the PR gate. One commit per issue ticket at PR squash (single ticket: #1380).

## Notes

- The generator and check scripts are throwaway (`tmp/1380/`), consistent with the spec's no-conversion-tooling decision; they are never committed.
- Linguistic-data constraints apply: the source is UTF-8 with IPA/diacritics — the generator operates on decoded text with no ASCII-fold or normalization beyond the horizontal-whitespace rule; comparison fidelity is exact otherwise.
- The stale `validation.yaml` record stays untouched (it documents the earlier revision's review); the current spec's SC judgment lives in this plan's header.
- SC-4/SC-5/SC-7/SC-9/SC-3 checks derive their expectations live from the source (no hardcoded totals), per the spec's verification methods; the spec's measured census serves only as a development-time cross-check.
