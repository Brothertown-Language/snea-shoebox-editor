# Spec — Route MDF field documentation lookups to `docs/mdf/ai-progressive` in root AGENTS.md

> Full spec and plan artifacts: https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/1441/
> Remote issue: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1441

## Problem

The root `AGENTS.md` is the auto-loaded instruction surface for every agent session in this repo. It currently carries no MDF field-documentation guidance at all (verified 2026-10-25 by reading the full 132-line file — no section references any MDF documentation surface). The observable failure this session: a `\ph` field-fact question (multiplicity, hierarchy placement) was answered by reading the frozen original `docs/mdf/MDFields19a_UTF8.txt` directly; the maintained progressive set `docs/mdf/ai-progressive/` — the post-migration source of truth per its own `README.md` ("After migration these files are the maintained source of truth; the Toolbox original stays frozen as provenance") — was reached only after developer correction.

The agent routing card that already implements the fix (`docs/agents/mdf-progressive.md`, created under issue #1380) is undiscoverable from the always-loaded surface, so the failure mode — agents reaching for the frozen `.txt` instead of the progressive set — repeats every session.

## Requirement source

Developer instruction (2026-10-25): "fix the root project AGENTS.md so the agent references the progressive docs and not the original file."

## Scope

Root `AGENTS.md` only: one added cross-reference section, shaped like the file's existing cross-reference table pattern (Lessons Learned / Research Catalog). No other file changes.

## Requirements

- **R-1:** AGENTS.md SHALL carry an MDF field-documentation cross-reference naming `docs/agents/mdf-progressive.md` (agent routing card) and `docs/mdf/ai-progressive/` (maintained source of truth), with entry points `docs/mdf/ai-progressive/index.md` and the `docs/mdf/ai-progressive/markers/{code}.md` layout (one file per `\key` entry; intent-based routes live in the card).
- **R-2:** the added guidance SHALL NOT present `docs/mdf/MDFields19a_UTF8.txt` as an agent reading surface or field-fact lookup source. If the path is named at all, it is named solely as frozen provenance (its programmatic consumers, `scripts/build_mdf_docs.sh` and `scripts/convert_mdf_master.py`, legitimately parse it at build time and are not reading surfaces).
- **R-3:** every path named in the new section SHALL resolve to an existing repo file or directory — dead pointers are the exact drift class this spec exists to prevent.

## Success criteria

| ID | Criterion | Class | Instrument |
|---|---|---|---|
| SC-1 | AGENTS.md contains an MDF field-documentation section naming the routing card and the progressive set with its entry points | structural | read/grep AGENTS.md for the section and both paths (`ai-progressive`, `mdf-progressive`) |
| SC-2 | No AGENTS.md line directs agents to read `docs/mdf/MDFields19a_UTF8.txt` for field facts; any mention is provenance-only framing | structural | grep AGENTS.md for `MDFields19a`; inspect every hit's context — a listing as provenance-only is compliant, a lookup direction is not |
| SC-3 | Every path named in the new section resolves to an existing repo file or directory | structural | glob/read each named path; all resolve |

## Out of scope

Observed adjacent drift, recorded here for a possible follow-up (not part of this spec):

- `src/mdf/validator.py:14` references `docs/mdf/original/MDFields19a_UTF8.txt` — a path that does not exist (the file sits at `docs/mdf/MDFields19a_UTF8.txt`).
- `docs/mdf/mdf-quick-reference.md:3` and `docs/mdf/mdf-tag-reference.md:13` and `docs/mdf/mdf-lookup-table.md:3` reference the authoritative source at a nonexistent `documentation/MDFields19a_UTF8.txt` path.
- `docs/guidelines/natick-workbench.md:24` references `documentation/MDFields19a_UTF8.txt` (same dead path).

Not in scope either: any change to the ai-progressive set, its routing card content, or the documentation build pipeline (`scripts/build_mdf_docs.sh`, `scripts/convert_mdf_master.py`).

## Impact

- **Consumers:** every agent session in this repo — AGENTS.md is auto-loaded into context. No application code is touched.
- **Risk:** instruction-surface bloat — mitigated by a compact table-row style consistent with the existing lessons-learned sections.
- **Already correct (unchanged):** `docs/agents/mdf-progressive.md`'s routing content; the `docs/mdf/ai-progressive/` set itself.

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)