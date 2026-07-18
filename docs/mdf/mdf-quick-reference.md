# MDF Tag Quick Reference

This file provides a concise list of valid MDF tags for Brothertown project processing. For detailed field definitions and bundling rules, always consult the authoritative source: [MDFields19a_UTF8.txt](../documentation/MDFields19a_UTF8.txt).

## Section Boundary Markers (Bundle Starters)
These tags MUST be placed at the absolute head of their respective MDF bundles to ensure subsequent fields (e.g., \ge, \nt, \so, \rf) are correctly associated and do not "leak" to preceding headwords or senses.
- `\lx` (Lexeme/Headword - Entry Root)
- `\pl` (Plural)
- `\se` (Subentry)
- `\ps` (Part of Speech/Sense Boundary)
- `\sn` (Sense Number)

## Valid Tags (Whitelist)
\aa, \bb, \bw, \ce, \cf, \cn, \cr, \de, \dn, \dr, \dt, \dv, \ec, \ee, \eg, \en, \er, \es, \et, \ev, \ge, \gn, \gr, \gv, \hm, \is, \lc, \le, \lf, \ln, \lr, \lt, \lv, \lx, \mn, \mr, \na, \nd, \ng, \np, \nq, \ns, \nt, \oe, \on, \or, \ov, \pc, \pd, \pde, \pdl, \pdn, \pdr, \pdv, \ph, \pn, \ps, \rd, \re, \rf, \rn, \rr, \sc, \sd, \se, \sg, \pl, \sn, \so, \st, \sy, \an, \tb, \th, \ue, \un, \ur, \uv, \va, \ve, \vn, \vr, \we, \wn, \wr, \xe, \xn, \xr, \xv
