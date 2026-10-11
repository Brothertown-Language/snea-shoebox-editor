---
title: "MDF Reference browser rail — raw keys, source parens, missing blurbs"
date: 2026-10-11
confidence: 0.95
tags: [MDF, mdf-reference, UI, field-markers, master-json, issue-triage]
sources:
  - "src/frontend/pages/mdf_reference.py"
  - "docs/mdf/build/master.json"
  - "docs/mdf/MDFields19a_UTF8.txt"
  - "scripts/convert_mdf_master.py"
  - "src/mdf/mdf_tags_metadata.json"
---

# Research Card: MDF Reference browser rail — three reported UI issues

Developer-reported issues (2026-10-11, screenshots of the in-app MDF
Reference browser rail). Root causes traced; no code changed.

## Issue 1 — Rail entries with underscores (`Range_Sets`, `Order_of_Fields`, `Sections_in_a_Lexical_Entry`)

**Root cause: presentation choice in the rail renderer, not missing data.**

- `_render_browser_tree()` in `src/frontend/pages/mdf_reference.py` labels
  the chapter button with the raw topic key
  (`st.button(chapter_key, ...)`), member buttons with `member["key"]`, and
  reference entries with `entry["key"]`.
- The keys are the source's own topic identifiers (`\key Range_Sets` in
  `docs/mdf/MDFields19a_UTF8.txt`), used by `\cf` cross-references —
  underscores are source data, faithful to the original document.
- Every topic also carries a human `\shd` heading in
  `docs/mdf/build/master.json` (`Range_Sets` → heading `"Range Sets"`;
  `Order_of_Fields` → `"Recommended Field Order"`;
  `Sections_in_a_Lexical_Entry` → `"Sections in a Lexical Entry"`). The rail
  already renders that heading as a `###` markdown line immediately above
  the underscore-keyed button — so the user sees both.
- Precedent: commit 9ea6b9e (issue #1379) relabeled the home button plain
  "Home", with the recorded rationale "the bare key is meaningless to them
  and never renders user-facing" — but only the home button got that
  treatment; chapter/member/reference buttons kept raw keys. The
  search-chip path (commit 22a7171) deliberately keeps bare keys ("that IS
  the lookup key").
- Sibling renderers split the same way: the HTML edition's nav sidebar uses
  human headings for chapters but `\key`-prefixed raw tokens for marker
  entries (`html_nav()` in `scripts/convert_mdf_master.py`); PDF cf-links
  show raw keys (source-faithful, the source's own stated convention).

## Issue 2 — Parenthesized rail entry ("(Understanding the hierarchical structure of an entry)")

**Root cause: verbatim source text.**

- `docs/mdf/MDFields19a_UTF8.txt` line 2387 reads
  `\shd2 (Understanding the hierarchical structure of an entry)` — the
  parentheses are in the original SIL document, marking it as a subordinate
  aside/subtitle.
- The rail's shd2 buttons render the stripped marker text verbatim
  (`"▸ " + strip_marker(block["text"]).strip()`), so the parens pass
  through. The HTML edition (`Sections_in_a_Lexical_Entry.html` h3) and the
  PDF reproduce them identically — all three renderers are source-faithful
  here.
- Contrast: the other shd2s have natural inline parens
  (`Changing Range Set Labels (for the \ps, \lf, and \pdl fields)`);
  stripping outer-wrapping parens would be a presentation-layer decision,
  not a data fix.

## Issue 3 — Field marker entries are bare tags with no explanatory blurbs (`lx`, `ce`, `cf`, `cn`)

**Root cause: the blurb data exists but the rail does not use it.**

- Each marker topic in `master.json` has a `heading` that IS the one-line
  description: `\ce` → `"\ce  cross-reference (English gloss)"`;
  `\lx` → `"\lx  lexeme or headword of the lexical entry"`. All 90 marker
  topics carry it (source `\shd` lines).
- A second, derived source exists: `src/mdf/mdf_tags_metadata.json` maps
  every tag to a clean short `name` (`ce` → `"cross-reference (English
  gloss)"`) plus a long `description` — 90 entries.
- The rail buttons show only the key; the blurb appears only after clicking
  (detail-pane heading uses `topic_display_heading()`, which prefers the
  source heading). Search chips behave the same (bare key, deliberate per
  2026-10-06 comment).

## Fix-shape notes (for the eventual spec/plan)

- Rail labels can switch to `topic_display_heading()` output (or
  `mdf_tags_metadata.json` `name`) with the key kept as button `help` /
  secondary text; deep-link `?marker=` keys are unaffected (keys stay the
  lookup identity, only labels change).
- Marker labels in HTML/PDF sibling renderers would need a matching pass if
  cross-edition consistency is required (their nav currently shows
  `\key`-prefixed tokens).
- Tests pinning current labels: `test/ui/test_mdf_reference_e2e.py`
  (buttons located by bare-key names: `lc`, `ge`, `xg`, …), smoke tests are
  structural only.
- Any label change should respect the recorded #1379/#1417 design intent —
  the new directive supersedes, but the spec should say so explicitly.

## Published-editions map (verified 2026-10-11, for the #1433 follow-up)

| Element | HTML | PDF | Compliance with #1431's regime |
|---|---|---|---|
| Chapter/topic titles | human `\shd` headings (nav, pages) | human `\shd` headings (`\chapter`, ToC) | compliant already |
| Field Marker Reference entries | `h4` topic headings carry token+name | `\subsection{...\lx  lexeme...}` token+name | compliant already |
| HTML search hit headings | `doc.heading` = token+name | n/a | compliant already |
| HTML nav marker entries | bare `\ce`-style tokens, no names | n/a | gap → #1433 SC-1 |
| HTML nav multi-key stub | raw `\1s 1p 1e ...` string | n/a | gap → #1433 SC-1 |
| `\shd2` headings | source-verbatim `h3` (paren-wrapped one present) | source-verbatim `\section` (paren-wrapped one present, enters print ToC) | gap → #1433 SC-2 |
| `\cf` links | source tokens raw | source tokens raw | unchanged by design (uniform with app detail pane) |

Confidence: high — all claims verified against the live files listed above,
2026-10-11.
