# MDF Reference Site Assets — Provenance

Generated artifacts under `docs/mdf/build/site/` are produced by
`scripts/convert_mdf_master.py --html-dir` from `docs/mdf/MDFields19a_UTF8.txt`
(see `.issues/1379/spec.md`). The files below are the only hand-managed assets.

## lunr.js

- **Version:** 2.3.9
- **Source URL:** https://unpkg.com/lunr@2.3.9/lunr.js
- **sha256:** `9431726f05c0eae2a6e54dc197709422869f25cad44f2430d2fb7ddae80cc717`
- **License:** MIT (Copyright (C) 2020 Oliver Nightingale) — header preserved in the file
- **Vendored:** 2026-10-05, fetched verbatim (unmodified)
- **Why vendored:** spec R-4 requires client-side search with no CDN references;
  the file is committed so the site works offline and the build never fetches.

`search-index.js` / `search-index.json`, `search.js`, and `style.css` are
regenerated on every build; `lunr.js` is static and must not be regenerated.

## Anchor scheme (deep-linking)

Every topic section carries `id="key-<slug>"` where `<slug>` is the topic's
exact `\key` value with whitespace runs replaced by `-` (a numeric suffix is
appended only in the impossible case of a slug collision). Examples:

- `\key lx` → `#key-lx`
- `\key Character_Style_Codes` → `#key-Character_Style_Codes`
- `\key 1s 1p 1e …` → `#key-1s-1p-1e-1i-1d-2s-2p-2d-3s-3p-3d-4s-4p-4d`

`\cf` cross-references link to `<page>#key-<slug>`, where `<page>` is
`index.html` for the home entry (`aa`) and `<chapter-slug>.html` for every
other topic (one page per chapter group). Unresolved backslash-prefixed `\cf`
tokens render as `a.cf-missing` placeholders (none exist in the 1.9a source).

LaTeX labels use the same slug: `\label{key:<slug>}`.
