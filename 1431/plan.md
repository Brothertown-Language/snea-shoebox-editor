# Plan — #1431: rail labels and marker blurbs (data-carried display fields)

Source: `.issues/1431/spec.md`. Branch `feature/1431-mdf-display-labels` (base tip 1be2185).
Stacked with #1433 (same branch, one PR, one squashed commit per issue).

## Item 1 — SC-6 (schema bump) — foundational
- Deliverable: `SCHEMA = "snea-mdf-master/2"` in `scripts/convert_mdf_master.py` (line 137) + docstring header (line 19); page docstring pin `src/frontend/pages/mdf_reference.py:6`; committed `master.json` regenerated.
- RED: `test/test_mdf_reference_smoke.py:49` asserts `/1`; new assertion pins `/2`.
- GREEN: bump all; update `test/test_mdf_quote_shaping.py:232` fixture.
- Verify: pytest smoke + quote-shaping; grep shows no stale `/1` outside round-trip fixtures that pin old documents (none found — both consumers updated).

## Item 2 — SC-5 (display data in converter)
- Deliverable: converter emits per-topic `display_label` and per-shd2-block `display_text` into master.json. Derivation (build time, from topic's own data):
  - chapters + multi-key stub: topic's `heading` (`\shd` text, marker-stripped already) — stub heading is "Old verb paradigm markers".
  - single-marker entries (heading begins with `\` + token == topic key): marker name = heading minus leading `\token` + following whitespace run, byte-identical thereafter; display label = token + name (token without backslash, source spacing preserved: `ce  cross-reference (English gloss)`).
  - Exception inventory: committed build-side constant `SHD2_DISPLAY_EXCEPTIONS` in the converter keyed by (topic key, source line), each entry `{text, reason}`; exactly one entry — `("Sections_in_a_Lexical_Entry", 2387)` → "Understanding the hierarchical structure of an entry", reason: source's wrapping parentheses dropped for the navigation label (the only fully paren-wrapped `\shd2`).
  - shd2 `display_text`: marker-stripped text, except overridden by the inventory.
  - Non-reference single-key topics without a leading-marker heading and chapters use `heading`; no invented text.
- RED: census assertions fail (no `display_label` fields; underscore census; 89/89 marker names non-empty & source-matched; exactly one shd2 exception, all other shd2 display texts byte-identical to marker-stripped source; stub label).
- GREEN: parser emits fields; census suite `test/test_mdf_converter_sc13_and_census.py` extended.
- Verify: pytest census suite; deterministic-output test stays green (fields derived deterministically).

## Item 3 — SC-1/SC-2/SC-3 (app rail renders committed fields)
- Deliverable: `mdf_reference.py` label sites read committed fields, no label munging:
  - chapter button (line 426) → `display_label`; member/stub (447) and reference entries (471) → `display_label`; residual (457) → `display_label`; search chips (1002) → `display_label` (home stays "Home"); shd2 sub-buttons (436) → block `display_text` (removes `strip_marker` surgery).
- RED: e2e/unit assertions expecting new labels fail against current behavior.
- GREEN: as above.
- Verify: grep census — no replace/strip/case-munging on label text in `mdf_reference.py`; e2e suite updated (SC-1/2/3 assertions; screenshots under tmp/ for layout review).

## Item 4 — SC-4 (navigation identity, regression)
- Keys unchanged; `?marker=` resolution, `\cf` navigation, search ranking unaffected (`heading` untouched → BM25 corpus identical).
- Verify: #1417 W1/W2(/W3) suites, vocabulary #1429 suite, MDF smoke tests, updated e2e — all green after `bash scripts/sync_prod_to_local.sh`.

## Item 5 — e2e suite updates
- `test/ui/test_mdf_reference_e2e.py`: rail-button label assertions switch from bare keys to display labels (lines 128, 224–234, 239–257 stub, 348/659/685); SC-1 (no underscore labels, chapter labels), SC-2 (paren-free shd2 label), SC-3 (89 token+name labels) assertions added.
- Verify: SNEA_E2E=1 run on :8501.
