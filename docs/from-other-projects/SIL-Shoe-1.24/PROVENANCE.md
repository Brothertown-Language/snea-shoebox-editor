# SIL-Shoe 1.24 — vendored reference (NOT a runtime dependency)

## Provenance

| Field | Value |
|---|---|
| Upstream | SIL Shoebox Utilities (SIL-Shoe) |
| Version | 1.24 |
| Author | Martin Hosken (MJPH), SIL |
| Source URL | `https://scripts.sil.org/cms/sites/nrsi/download/mh_shutils_source/SIL-Shoe-1.24.tar.gz` |
| Fetched | 2026-10-05 |
| Fetched by | AI agent (OpenCode, session for #1379), at developer direction |
| Upstream integrity | tar.gz SHA-256: `44ccb0111a6b05811306d67527d6aaa086d483df8f0f39f233be823e2b1b8928`; files copied unmodified |

## Why this is vendored

The repo's MDF source document (`docs/mdf/MDFields19a_UTF8.txt`) is a Toolbox/Shoebox
**Standard Format (SFM)** help file. The SFM line grammar is documented externally, not by
the data file itself. This distribution is SIL's own utility implementation for these
formats and serves as the **authoritative format reference** for:

1. **Parsing semantics** — `lib/Data.pm` (`SIL::Shoe::Data`) implements the SF line
   grammar: a field marker is a line starting with `\` + one non-space token
   (`m/^\\(\S*)\s*(.*?)\s*$/`); lines beginning with whitespace are never markers
   ("SF markers can't start with space" — Data.pm comment); non-marker lines are
   continuations of the current field; by default multi-line fields are joined with a
   space and edge whitespace stripped, with `nostripnl`/`nostripws` opt-outs.
2. **Formatting/type style reference** — `Scripts/sh_rtf` (SFM → RTF typesetting
   conventions), `lib/Type.pm` + `lib/Settings.pm` (`.typ`/`.lng` handling — marker
   types, ordering), `Scripts/sh2xml` (marker-to-structure mapping).
3. **Format documentation** — `docs/shutils.pod` states the Toolbox/Shoebox format
   relationship: "Toolbox … being a superset of Shoebox … the Shoebox utilities will
   work quite happily with Toolbox files."

## Status and limits

- **Reference only.** The code is Perl 5 from 1998–2005, unmaintained, and NOT wired
  into this project's build or runtime. Nothing imports it.
- **License:** the upstream distribution carries no explicit license file (no LICENSE,
  COPYING, or Artistic/GPL statement in `readme.txt`, `META.yml`, or the PODs). Vendored
  here solely as attributed reference documentation; if this ever becomes more than a
  reference, license terms must be clarified with the upstream author first.
- **Curated subset:** only the files listed below are vendored — not the full tarball
  (test data, Windows installers, and unrelated utilities omitted). Full original
  available at the source URL above.

## Files

| Path | Upstream path | Purpose here |
|---|---|---|
| `modules/Data.pm` | `lib/SIL/Shoe/Data.pm` | SF line grammar reference (marker detection, continuation lines, record structure) |
| `modules/Type.pm` | `lib/SIL/Shoe/Type.pm` | `.typ` type-file handling reference (marker types, hierarchy) |
| `modules/Settings.pm` | `lib/SIL/Shoe/Settings.pm` | Project settings (.prj/.lng/.cct) handling reference |
| `docs/shutils.pod` | `docs/shutils.pod` | Format and tool documentation |
| `Scripts/sh_rtf` | `Scripts/sh_rtf` | SFM → RTF formatting conventions reference |
| `Scripts/sh2xml` | `Scripts/sh2xml` | Marker-to-structure mapping reference |
| `readme.txt` | `readme.txt` | Original upstream readme (provenance) |
| `META.yml` | `META.yml` | Upstream distribution metadata (version 1.24) |

## Relation to #1379

The #1379 spec's Parsing Semantics section is grounded in `lib/Data.pm`'s grammar plus a
live census of `docs/mdf/MDFields19a_UTF8.txt` (14 line-initial marker types, all at
byte offset 0; indented/mid-line marker-like text is content — including the three
indented `\cf` occurrences, which are wrapped prose at lines 393/406 and a display row
at line 2661, not fields).
