# Plan — #1433: HTML/PDF label parity with committed display data

Source: `.issues/1433/spec.md`. Depends on #1431's schema-/2 display fields. Same branch/PR as #1431.

## Item 6 — SC-1 (HTML nav from display data)
- Deliverable: `html_nav` (convert_mdf_master.py ~1614, ~1625) renders marker entries as `\` + committed display label (typographic backslash prefix permitted by the parity definition); stub renders its display label without a backslash prefix ("Old verb paradigm markers"); chapters/home unchanged.
- RED: census parse of built HTML nav — bare-token entries fail.
- GREEN: emit from `display_label`; classify marker entries via `reference_group`/`is_reference_entry` (structure, not string surgery).
- Verify: renderer-suite census — 89 token+name entries, stub label, zero underscore-bearing nav labels.

## Item 7 — SC-2 (shd2 display text in HTML + PDF)
- Deliverable: `html_topic` shd2 heading (~1533) and `latex_topic` shd2 heading (~1097) use block `display_text`; paren-wrapped entry renders without parens in HTML h3 (chapter page) and PDF `\section` + print ToC.
- RED: built-artifact census finds paren-wrapped heading.
- GREEN: read committed field.
- Verify: renderer census byte-compares every shd2 heading against source-derived expectation with exactly one exception; PDF ToC spot check via the built `.tex` (checked source of truth) + successful compile.

## Item 8 — SC-3/SC-4 (single-sourcing + parity census)
- Deliverable: no render-time string transformation beyond #1431's defined derivation; parity census joins master.json display data against HTML nav, LaTeX section/subsection titles, and (via #1431's suite) the app rail; exception inventory count unchanged.
- Verify: extended `test/test_mdf_renderers_sc2_sc3_sc14.py` censuses.

## Item 9 — SC-5/SC-6 (corpus invariance + byte-exact rebuild)
- Deliverable: regenerate committed artifacts (`master.json`, `master.tex`, `site/`, PDF via `scripts/build_mdf_docs.sh`); lunr `text`/`heading` unchanged; round-trip and rebuild reproduce committed bytes.
- Verify: full renderer suite incl. byte-exact rebuild; committed PDF sha256 e2e test updated if bytes change (they will — new labels).

## Item 10 — Regression
- `bash scripts/sync_prod_to_local.sh`, then full pytest (W1/W2 candidate suites, #1431 display-data census, round-trip census, renderer suite) + SNEA_E2E=1 run.
