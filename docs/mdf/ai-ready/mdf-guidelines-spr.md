<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
<!-- Licensed under CC BY-SA 4.0 -->
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
\dt: Date (YYYY-MM-DD)

[RULES]
- 1 tag/line.
- Starts with backslash.
- Hierarchy via indentation.
- Distinct stages for transformations (Atomic).
