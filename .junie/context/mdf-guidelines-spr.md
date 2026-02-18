<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
# MDF TAG REFERENCE - SPR COMPRESSED (2026-01-26)

[CONTEXT]
MDF (Multi-Dictionary Formatter) = Standard for Shoebox/Toolbox database interchange.
Source: `documentation/mdf-tag-reference.md`.

[HIERARCHY]
Root: \lx (Lexeme)
Children: \ps (POS), \sn (Sense), \se (Subentry).
Bundles: (\xv, \xe) [Example/Trans], (\cf, \ce) [Cross-ref/Gloss].

[MAPPINGS]
Legacy -> Modern:
\lmm -> \lx (Lexeme)
\ctg -> \ps (POS)
\gls -> \ge (Gloss English)
\src -> \so (Source)

[CORE_TAGS]
\lx: Headword
\hm: Homonym #
\ps: POS
\sn: Sense #
\ge/\de: Gloss/Definition
\se: Subentry (phrases/complex)
\xv/\xe: Example/Translation
\cf: Cross-reference
\nt: Notes
\ln: Language
\dt: Date (YYYY-MM-DD)

[RULES]
- 1 tag/line.
- Starts with backslash.
- Hierarchy via indentation.
- Distinct stages for transformations (Atomic).
- **DEBUGGING TRANSFORMATIONS:**
  1. Create a minimal test file with the single record causing the issue.
  2. Use a "trace script" to call transformation methods sequentially.
  3. Print the state of `record.lines` after each method call.
  4. Pinpoint the first method that damages the data.
  5. Verify the fix using the same trace.
