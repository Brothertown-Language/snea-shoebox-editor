> Full spec: this issue body (remote spec). Plan artifacts will be created at https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/1431/ when this enters its plan cycle.

## Problem
The in-app MDF Reference browser (#1379) renders its navigation rail from the source's raw topic keys — reported 2026-10-11 with screenshots, three issues:

1. **Underscore entries.** Chapter buttons show the raw `\key` identifiers (`Range_Sets`, `Order_of_Fields`, `Sections_in_a_Lexical_Entry`) while the rail already prints the human `\shd` heading directly above each chapter button — the heading says "Range Sets", the clickable button beneath says `Range_Sets`. Fifteen of the seventeen chapter keys contain underscores; no human heading does.
2. **A parenthesized entry.** The rail entry "▸ (Understanding the hierarchical structure of an entry)" reproduces the source's own wrapping parentheses (`MDFields19a_UTF8.txt` line 2387). Source-faithful, but as a navigation label the wrapping parens are noise. It is the only fully paren-wrapped `\shd2` in the source.
3. **Bare marker tags.** The Field Marker Reference section's 89 entries render the bare marker token (`lx`, `ce`, `cf`, `cn`) with no explanatory text; the token's meaning appears only after clicking. The description exists in the source data — every marker topic's `\shd` heading is exactly the marker token plus its one-line name (`\ce  cross-reference (English gloss)`).

Root cause (researched 2026-10-11, recorded in `.issues/research-cards/mdf-reference-rail-labels-and-blurbs.md`): presentation choice, not missing data — `src/frontend/pages/mdf_reference.py` labels buttons with `topic["key"]` while the human data sits unused in `docs/mdf/build/master.json` headings. The home entry already proves the pattern: #1379's commit 9ea6b9e relabeled it plain "Home" on the recorded rationale that the bare key is never user-facing; chapter and reference entries were left as raw keys.

## Design direction (developer-stated, 2026-10-11)
The reference content is static data — the JSON and other build files can carry the specific exceptions and overrides, so no renderer performs string surgery at render time: the converter (`scripts/convert_mdf_master.py`) emits resolved display data into `docs/mdf/build/master.json`, and the page renders committed fields verbatim.

## Definitions (normative)
- **Rail:** the MDF Reference browser's left column — the unfiltered tree and the search-results list alike (both render entry buttons; the label rule is identical in both).
- **Display label** (per topic): the user-facing text of the topic's rail button, derived at build time from the topic's own data — chapters and the multi-key stub: the `\shd` heading text; single-marker entries: the marker token together with its marker name.
- **Marker name** (per single-marker topic): the topic's `\shd` heading text minus the leading marker token and following whitespace, preserved byte-for-byte thereafter — internal spacing and parentheses are source content (`\is` → "index  of  semantics"; `\xg` → "(discontinued field)").
- **shd2 display text** (per `\shd2` block): the marker-stripped source text, except where the exception inventory overrides it.
- **Exception inventory:** the committed build-side table enumerating every deviation of emitted display data from source text, each entry stating the topic key, the block locator (source line), and the reason. This spec requires exactly one entry (SC-2); the inventory grows by data, never by renderer code.
- **Topic key:** unchanged throughout — keys are the lookup identity (`?marker=` deep links, `\cf` targets, search aliases); only labels change.

## Requirements
- **SC-1 (behavioral; issue 1):** every rail entry button's visible label is its committed display label; the chapter entries render "Range Sets", "Recommended Field Order", and "Sections in a Lexical Entry"; no rail entry label in the committed data contains an underscore; the home entry remains "Home".
- **SC-2 (behavioral + structural; issue 2):** the `\shd2` entry under Sections in a Lexical Entry renders "Understanding the hierarchical structure of an entry" — the source's wrapping parentheses dropped by the exception inventory's single enumerated entry; every other `\shd2` display text is byte-identical to its marker-stripped source text.
- **SC-3 (behavioral; issue 3):** each of the 89 Field Marker Reference entries presents its marker token and its marker name together on the entry affordance, both visible without navigating (the exact arrangement — token and name in one button, or token button with adjacent name text — is a plan decision); all 89 marker names are non-empty and match their source headings.
- **SC-4 (behavioral; navigation identity):** topic keys are unchanged — all 108 `?marker=` keys resolve as before; `\cf` buttons and pair rows navigate to the same targets; search ranking is unaffected (keys and corpus text are unchanged; #1417's candidate suite passes unmodified).
- **SC-5 (structural; data-carried design):** all rail labels are read from `master.json` committed fields — no render-time string transformation of label text in `mdf_reference.py` (no replace/strip/case-munging on labels); the exception inventory lives in the committed build-side data with a stated reason per entry; regenerating `master.json` from the source reproduces the committed file byte-for-byte.
- **SC-6 (structural; versioning discipline):** the master-json contract changes, so the schema version bumps (`snea-mdf-master/1` → `/2`) and every documented consumer expectation follows (the page docstring's schema pin; any test asserting the schema string).
- **Unchanged by this spec:** the rail's `###` group headings, the detail pane (headings, `\cf` rendering, pair rows), the split-pane layout, and the PDF/HTML editions' behavior.

## Verification instruments
- **Behavioral SCs (SC-1, SC-2, SC-3, SC-4):** Playwright real-browser tests against the live app (`SNEA_E2E=1`, app on :8501) per the UI testing standard — `test/ui/test_mdf_reference_e2e.py`'s rail-button selectors update to the new labels and gain the SC-1/SC-2/SC-3 assertions; screenshots under `tmp/` for layout-sensitive review.
- **Structural SCs (SC-2's data census, SC-5, SC-6):** fact-decidable — the converter's round-trip census suite (`test_mdf_converter_sc13_and_census.py`, including byte-exact source reconstruction) extended with the display-data census: 89/89 marker names non-empty and source-matched, zero underscores in display labels, exactly one shd2 exception with every other shd2 display text byte-identical; code inspection confirming no label-munging path; schema-string assertions updated.
- **Regression (SC-4):** pytest — #1417's W1/W2 candidate suites, the MDF smoke tests, the updated e2e suite.

## Out of scope
- The PDF and HTML editions' own label conventions (PDF `\cf` links keep the source's raw tokens — the source's own stated convention; the HTML nav already uses human chapter headings). The emitted display fields are available to them as data, but no renderer change is required by this spec.
- The detail pane — not among the reported issues.
- Any change to search scoring, vocabulary tables, or topic keys.
- Content changes to the source (`MDFields19a_UTF8.txt`) — display exceptions are presentation data; the source stays byte-identical.

## Impact
- **Dependencies:** none new; builds on #1379's committed pipeline (`scripts/convert_mdf_master.py` → `master.json` → page).
- **Risk:** label drift between the three editions — mitigated by single-sourcing every label in `master.json`; the exception inventory keeps deviations auditable and prevents silent general rules (the `\xg` case shows why: its name "(discontinued field)" legitimately keeps its parentheses).
- **Data integrity:** every display label traces to the source's own `\shd` text; the one exception is enumerated, located, and reasoned — no invented text.
- **Test impact:** `test/ui/test_mdf_reference_e2e.py` rail selectors (bare-key names `lc`, `ge`, `xg`, …) update to the new labels; the search suites are unaffected.

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
