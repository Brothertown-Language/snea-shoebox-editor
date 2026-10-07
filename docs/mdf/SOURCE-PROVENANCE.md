# MDF field documentation — source provenance

cover-date: 2006-05-12

The line above is machine-readable: `scripts/build_mdf_docs.sh` parses it as the
cover-page date of this edition. It is the authoritative last-modified date of the
original document (developer ruling, 2026-10-06 — see Change control below), not a
date of this repo or of this edition.

## Provenance

| Field | Value |
|---|---|
| Original document | `ToolboxMDFFields/MDFields19a.txt` — MDF 1.9a field documentation (draft version 1.9a) |
| Authors (source's own draft line) | revisions Karen Buseman; original database David Coward |
| Distribution | `ToolboxMDFFields.zip` documentation package for the Field Linguist's Toolbox, SIL International |
| Distribution site | http://www.fieldlinguiststoolbox.org/ (JavaScript-only; requires scripting to render) |
| Original encoding | cp1252 — `file` reports "Non-ISO extended-ASCII text, with CRLF line terminators"; 133,839 bytes |
| Zip-internal last-modified | **2006-05-12 22:18** — AUTHORITATIVE for the cover-page date |
| Zip companions | `MDFields.typ` + `ToolboxMDFFields.prj` (2006-08-04 07:58); `Default.lng` (2006-07-07 09:22); no license or readme file in the zip |
| Local copy of the zip | `~/Documents/Brothertown-Language/ToolBox/MDFDocumentation/ToolboxMDFFields.zip` (readable, unmodified) |
| Tracked transcription | `docs/mdf/MDFields19a_UTF8.txt` — UTF-8, LF line endings, 130,520 bytes |
| Date ruling | the zip-internal timestamp, NOT the git last-modified date of the tracked transcription (2026-10-06, developer Michael Conrad) |

## Document self-dating

The source's own draft line (topic `aa`; lines 29–31 of the tracked transcription) reads:

> (This is draft version 1.9a, in preparation for "version 2" of the MDFields Helps
> database. The original database was constructed by David Coward. The revisions
> are being done by Karen Buseman. May 12, 2006)

This corroborates the zip-internal timestamp of 2006-05-12.

## Byte-exact conversion verification (reproducible)

The tracked transcription is a byte-exact conversion of the original — CRLF to LF plus
cp1252 to UTF-8, nothing else. Verified programmatically on 2026-10-06:

```bash
unzip -o ~/Documents/Brothertown-Language/ToolBox/MDFDocumentation/ToolboxMDFFields.zip \
    'ToolboxMDFFields/MDFields19a.txt'
python3 - <<'EOF'
import pathlib
orig = pathlib.Path("ToolboxMDFFields/MDFields19a.txt").read_bytes()
trk = pathlib.Path("docs/mdf/MDFields19a_UTF8.txt").read_bytes()
conv = orig.decode("cp1252").replace("\r\n", "\n").encode("utf-8")
assert conv == trk, "conversion mismatch"
print(f"{len(orig)} -> {len(trk)} bytes; byte-identical")
EOF
```

Note: the zip's member path carries the `ToolboxMDFFields/` prefix — extracting the bare
name `MDFields19a.txt` fails ("filename not matched"). Verified result: 133,839 →
130,520 bytes, byte-identical.

## Distribution site

- Field Linguist's Toolbox — http://www.fieldlinguiststoolbox.org/ (JavaScript-only site).
- SIL product page — https://software.sil.org/toolbox/ (quotes verified live 2026-10-06):
  - "Toolbox is the predecessor of FieldWorks, but still has a large following of users as a language data management and analysis tool for field linguists."
  - "SIL recommends the use of FieldWorks, but continues to provide access to Toolbox for those who don't want to switch."
  - "It's entirely free to download and use, making it accessible to anyone."
  - "This software is free to use. It is developed and supported by people from an SIL field entity."
  - Toolbox "is compatible with both Unicode and legacy encoding systems."

## Licensing determination

| Subject | Determination | Evidence | Confidence |
|---|---|---|---|
| Toolbox software | MIT license | https://github.com/sillsdev/Toolbox — `LICENSE.txt` (verified via GitHub API, 2026-10-06) | high |
| MDF field documentation (`MDFields19a.txt`, `MDFields.typ`) | No explicit license statement — not in the zip, not on either site. Most likely reading: © SIL International, published freely as program documentation accompanying the MIT-licensed Toolbox ("entirely free to download and use"). No explicit redistribution or modification grant found | zip contents (no license/readme file); both distribution sites | high that it is free to use as distributed; low that any formal license grant exists (none found) |

Practical reading: attribution and a source link are owed; anything beyond free
reference / derivative-documentation use should be confirmed with SIL International.

## Change control

| Date | Entry | Authorized by |
|---|---|---|
| 2026-10-06 | Provenance recorded; the `cover-date:` line above established as the machine-readable authoritative cover date for the #1379 build (`scripts/build_mdf_docs.sh` parses this file; a missing or invalid line is a build error — never a silent fallback to the git date). Supersedes the #1379 spec's Typographic Mapping row for `\_sh`, which pinned the title-block date to the tracked transcription file's git last-modified date (`git log -1 --format=%cs -- docs/mdf/MDFields19a_UTF8.txt`) — the git date dates the UTF-8 transcription, not the original document. The title-block date is rendered semantically as the original document's date (date line plus "original document" label) | Developer (Michael Conrad) |
