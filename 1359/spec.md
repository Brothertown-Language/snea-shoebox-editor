---
issue_number: 1359
title: "[RESEARCH] Exhaustive Search for Additional SNEA Materials — Vocabularies, Reconstructions, and Comparison Sources"
state: open
created_at: "2026-07-17T00:00:00Z"
---

# [RESEARCH] Exhaustive Search for Additional SNEA Materials

## Problem Statement

The existing research issues (#1362–#1369) cover 8 primary colonial-era orthography-to-phoneme analyses for Southern New England Algonquian (SNEA) languages. However, several significant sources — both colonial-era vocabularies and modern reconstructions — remain unexamined. These materials could provide:

1. **Additional lexical data** for cross-source comparison and validation
2. **Modern reconstructed vocabularies** that can serve as comparison baselines
3. **Later colonial attestations** that show diachronic change within the SNEA language family
4. **Tribal community language work** that represents living knowledge traditions

## Scope

This spec covers the discovery, evaluation, and documentation of SNEA materials NOT already covered by issues #1362–#1369. Each identified source must be evaluated for: size, dialect, time period, orthographic system, accessibility, and potential utility for the shoebox editor project.

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC-1 | All known colonial-era SNEA vocabularies not in #1362–#1369 are identified and documented | `string` | Research card entries with source URLs and size estimates |
| SC-2 | All major modern reconstruction dictionaries for SNEA languages are identified and documented | `string` | Research card entries with source URLs and scope descriptions |
| SC-3 | Each identified source has a confidence-rated research card in `.issues/research-cards/` | `structural` | File existence check for each new card |
| SC-4 | Cross-source comparison table is updated to include all newly identified sources | `string` | Updated `cross-source-comparison.md` with new rows |
| SC-5 | Sources manifest (`.issues/research-cards/sources/MANIFEST.md`) is updated with any newly mirrored files | `structural` | File modification check |
| SC-6 | Each new research card includes: source description, dialect affiliation, date, estimated entry count, orthographic system, accessibility status, and utility assessment for the shoebox editor | `string` | grep for required fields in each new card |
| SC-7 | Sources that are freely accessible online have their full text or key excerpts mirrored to `.issues/research-cards/sources/` | `structural` | File existence check for mirrored sources |
| SC-8 | A gap analysis identifies any known SNEA sources that could not be accessed, with reason | `string` | Gap analysis section in spec body or research card |

## Identified Source Candidates (Preliminary)

### Colonial-Era Vocabularies (not in #1362–#1369)

| # | Source | Date | Dialect | Est. Entries | Current Status |
|---|--------|------|---------|-------------|----------------|
| 1 | John Cotton Jr. — Indian Vocabulary | 1666–1678 | Martha's Vineyard Wampanoag | Lexicon (size TBD) | Mentioned in research cards; no dedicated issue |
| 2 | Josiah Cotton — Vocabulary of the Massachusett Language | 1707–1708 | Massachusett | ~60 leaves | Mentioned in research cards; no dedicated issue |
| 3 | Ezra Stiles — Pequot Vocabulary | 1762 | Pequot (Mohegan-Pequot) | ~159 forms | Not covered; manuscript at Yale |
| 4 | James Noyes — Pequot Vocabulary | 1690 | Pequot (Mohegan-Pequot) | Unknown | Not covered; earliest Pequot documentation |
| 5 | Experience Mayhew — Indian Converts (1727) + Massachusett Psalter | 1727 | Martha's Vineyard Wampanoag | Scattered vocab | Not covered; contains Wampanoag language material |
| 6 | Thomas Mayhew Jr. — Missionary vocabularies | 1640s–1650s | Martha's Vineyard Wampanoag | Unknown | Not covered; early MV missionary |
| 7 | Francis Brinley — "Briefe Narrative of the Nanhiganset Countrey" | c. 1700 | Narragansett | Unknown | Not covered; supplements Williams |
| 8 | General Treat — Vocabulary | 18th c. | Mohegan-Pequot | Unknown | Not covered; analyzed in Cowan (1982) |
| 9 | Albert S. Gatschet — Narragansett Vocabulary | 1879 | Narragansett | Unknown | Not covered; last known speaker elicitation |

### Modern Reconstruction Dictionaries

| # | Source | Date | Language | Est. Entries | Current Status |
|---|--------|------|---------|-------------|----------------|
| 10 | WLRP (Wôpanâak Language Reclamation Project) — Baird et al. | 1993–present | Wampanoag (Wôpanâak) | 10,000–13,000+ | Not covered; modern reconstruction |
| 11 | A Modern Mohegan Dictionary — Fielding & Costa (2006) | 2006 | Mohegan-Pequot | Full dictionary | Not covered; modern reconstruction |
| 12 | Wampanoag Dictionary (GitHub: wampanoag-dictionary/dictionary) | 2020s | Wampanoag | Online dictionary | Not covered; modern web app |
| 13 | DOBES Narragansett Dictionary (Max Planck Institute) | 2000s | Narragansett | Unknown | Not covered; online archive |
| 14 | The Narragansett Dawn — Language Lessons (1935–1936) | 1935–1936 | Narragansett | 14 lessons | Not covered; tribal community work |
| 15 | O'Brien (Moondancer) — Grammatical Studies + Introduction | 2000–2009 | Narragansett | Pedagogical | Partially covered in #1362 research card; needs dedicated card |

## Phases

### Phase 1: Colonial-Era Vocabularies (SC-1, SC-3, SC-6, SC-7)

Research and document each colonial-era source not covered by #1362–#1369:

1. **John Cotton Jr. (1666–1678)** — Martha's Vineyard Wampanoag
   - Locate the MHS manuscript (Ms. N-1042) and any digital edition
   - Assess the "Wôpanâak Inscribed" NHPRC project status
   - Document dialect affiliation (MV Wampanoag vs. mainland Massachusett)
   - Create research card

2. **Josiah Cotton (1707–1708)** — Massachusett
   - Access Pickering (1829/1830) edition via HathiTrust / Archive.org
   - Document structure (topical vocabularies, dialogues, Creed, Lord's Prayer)
   - Create research card

3. **Ezra Stiles (1762)** — Pequot
   - Access the manuscript via Yale Beinecke Library
   - Use Cowan (1973) "Pequot from Stiles to Speck" as secondary analysis
   - Document the 159 forms
   - Create research card

4. **James Noyes (1690)** — Pequot
   - Search for the original manuscript or transcriptions
   - Document what is known about its contents
   - Create research card (may be limited if source is lost)

5. **Experience Mayhew (1727)** — Martha's Vineyard Wampanoag
   - Access "Indian Converts" full text
   - Extract Wampanoag words and phrases from the biographical narratives
   - Document the Massachusett Psalter
   - Create research card

6. **Thomas Mayhew Jr. (1640s–1650s)** — Martha's Vineyard Wampanoag
   - Search for any surviving vocabulary material
   - Document his role as first English missionary to learn Wampanoag
   - Create research card

7. **Francis Brinley (c. 1700)** — Narragansett
   - Access the "Briefe Narrative" via RIHS publications
   - Extract Narragansett vocabulary
   - Create research card

8. **General Treat (18th c.)** — Mohegan-Pequot
   - Locate Cowan (1982) analysis
   - Create research card

9. **Gatschet (1879)** — Narragansett
   - Access the IJAL 1973 publication
   - Document as last-known-speaker elicitation
   - Create research card

### Phase 2: Modern Reconstruction Dictionaries (SC-2, SC-3, SC-6, SC-7)

Research and document each modern reconstruction source:

10. **WLRP Dictionary (Baird, 1993–present)**
    - Document the reconstruction methodology (Eliot orthography → modern phonemic orthography)
    - Assess accessibility (WLRP website, published materials)
    - Document the 10,000–13,000 word scope
    - Create research card

11. **A Modern Mohegan Dictionary (Fielding & Costa, 2006)**
    - Access the PDF (available on Archive.org and Brothertown Indians site)
    - Document the Costa alphabet and reconstruction methodology
    - Assess utility for cross-dialectal comparison
    - Create research card

12. **Wampanoag Dictionary (GitHub)**
    - Access the web app at wampanoag-dictionary.github.io
    - Document the data model and API
    - Create research card

13. **DOBES Narragansett Dictionary**
    - Access the Max Planck Institute archive
    - Document contents
    - Create research card

14. **The Narragansett Dawn (1935–1936)**
    - Access the full PDF (available via Dawnland Voices / queer.archive.work)
    - Extract the 14 language lessons
    - Document as tribal community language work
    - Create research card

15. **O'Brien (Moondancer) Narragansett Materials**
    - Create dedicated research card for O'Brien's pedagogical works
    - Document: Grammatical Studies (2009), Introduction (2001), Indian Grammar Dictionary (2000)
    - Assess utility for orthography-to-phoneme comparison

### Phase 3: Cross-Source Integration (SC-4, SC-5, SC-8)

1. Update `cross-source-comparison.md` with new sources
2. Update `MANIFEST.md` with any newly mirrored files
3. Produce gap analysis documenting inaccessible sources
4. Assess which new sources provide usable vocabulary data for the shoebox editor

## Research Card Requirements

Each new research card must include:

- **YAML frontmatter** with: title, date, confidence score (0.0–1.0), tags, sources (URLs)
- **Source description**: author, title, date, publication context
- **Dialect affiliation**: which SNEA language/variety
- **Estimated entry count**: number of words/phrases
- **Orthographic system**: description of spelling conventions
- **Accessibility status**: freely available, paywalled, manuscript only, lost
- **Utility assessment**: how this source can be used in the shoebox editor project
- **Key lexical items**: notable or unique vocabulary (if applicable)
- **Cross-references**: links to related research cards and issues

## Gap Analysis

Sources that are known to exist but could not be accessed must be documented with:
- Source name and reference
- Reason for inaccessibility (paywall, manuscript not digitized, lost)
- Potential value if accessed in the future
- Alternative access paths (interlibrary loan, institutional access, etc.)

## Artifacts

- `.issues/1359/spec.md` — This spec
- `.issues/research-cards/<source-name>.md` — New research cards (one per source)
- `.issues/research-cards/cross-source-comparison.md` — Updated comparison table
- `.issues/research-cards/sources/MANIFEST.md` — Updated manifest
- `.issues/research-cards/sources/` — Newly mirrored source files

## Dependencies

- None on other issues; this is independent research that feeds into the broader SNEA corpus
- May inform future orthography-to-phoneme conversion work

## Change Control

| Date | Change |
|------|--------|
| 2026-07-17 | Initial spec |

🤖 Co-authored with AI: OpenCode (ollama-cloud/deepseek-v4-flash)
