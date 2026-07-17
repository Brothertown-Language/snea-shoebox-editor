# Orthography Research: Trumbull 1903 (Wampanoag)

**Issue:** #1363 — Trumbull Research Card
**Source ID:** 1
**Language:** Wampanoag (Massachusett) [wam]
**Records:** 4,491
**Source:** James Hammond Trumbull, *Natick Dictionary* (1903), Bureau of American Ethnology Bulletin 25
**Researcher:** AI agent

---

## 1. Orthography System

Trumbull's *Natick Dictionary* is the definitive lexical compilation for the Massachusett (Wampanoag) language, primarily drawing from the 17th-century Eliot "Indian Bible" and other evangelical texts in the Massachusett writing system. The orthography is the **Eliot orthography** — the first standardized writing system for an Algonquian language, developed by John Eliot and his Massachusett collaborators in the 1650s–1660s.

The Eliot orthography is based on English sound-spelling conventions but with significant regularization. Trumbull's edition (1903) adds some typographic conventions of early 20th-century philology.

### Key References

- **Trumbull, James Hammond.** (1903). *Natick Dictionary.* BAE Bulletin 25. Smithsonian Institution. — The source itself
- **Goddard, Ives & Bragdon, Kathleen.** (1988). *Native Writings in Massachusett.* American Philosophical Society. — Modern analysis of the Eliot orthography, phonology
- **O'Brien, Frank Waobu.** *Guide to Historical Spellings.* Chart C — master table covering both Massachusett and Narragansett
- **Eliot, John.** (1663). *Mamusse Wunneetupanatamwe Up-Biblum God.* — The "Eliot Bible" that defined the orthography

---

## 2. Eliot Orthography — Vowel Rules

### Simple Vowels

| Eliot | Massachusett Sound | Notes |
|-------|-------------------|-------|
| a | /aː/ ~ /ə/ | Long a or schwa depending on stress |
| e | /iː/ ~ /ɛ/ ~ /ə/ | Often /iː/ in stressed position, word-final /ə/ or silent |
| i | /iː/ ~ /ɪ/ ~ /ə/ | |
| o | /uː/ ~ /ə/ ~ /ɔː/ | Broad range, often /uː/ |
| u | /ə/ ~ /a/ | Typically schwa |
| ee | /iː/ | Consistent long i |
| oo | /uː/ | Consistent long u |
| ii | /iː/ (long) | Less common |
| ô, ê | unknown | Rare in Eliot orthography, mostly modern editorial additions |

### Special Characters

| Char | Meaning | Found in DB |
|------|---------|-------------|
| `∞` | Represents the sequence **oozzz** (a preaspirated/breathy vowel sequence). This is NOT an infinity symbol — it's Trumbull's typographic convention for a phonetically complex vowel+consonant sequence. | 654 occurrences across records |
| `∞̌` | oozzz with a breve — phonetically reduced/ultra-short variant | Rare |
| `|` (pipe) | Morpheme boundary marker. Most entries are enclosed in `|...|` to isolate the citation form. | 4,488 records (near-universal) |

### ∞ Symbol Decoding

Per `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md`:

> *"∞ is a valid letter, maps to oozzz"*

The ∞ symbol in Trumbull's transcription represents a phonetically complex sequence that English speakers heard/perceived differently from Massachusett speakers. It is **not** an actual /∞/ — it is a typographic convention for a sound sequence that Trumbull could not represent with standard Latin letters.

In the conversion pipeline, `∞` → `oozzz` is the first normalization step.

---

## 3. Consonant Rules

| Eliot | Massachusett Sound | Notes |
|-------|-------------------|-------|
| p | /p/ ~ /b/ | Unaspirated, often lenis |
| t | /t/ ~ /d/ ~ /tʲ/ | Context-dependent |
| k | /k/ ~ /g/ ~ /kʷ/ | Before vowels may be labialized |
| c (before a/o/u) | /k/ | Hard c |
| c (before e/i) | /s/ | Soft c (English convention) |
| ch | /tʃ/ | |
| sh | /ʃ/ | |
| s, ss | /s/ | |
| m, n | /m/, /n/ | |
| w | /w/ ~ /j/ before e/i | |
| q | /kʷ/ | Labialized k |
| h | /h/ | Occasionally used; preaspiration often unwritten |

### Preaspiration /h/

Same problem as Williams (Narragansett): English-speaking recorders consistently fail to hear preaspirated /h/ before stops. In Massachusett, /h/ occurs before /p/, /t/, /k/ word-medially. Trumbull/Eliot sometimes write it (`hk`, `hp`, `ht`) but often omit it.

**Evidence from the DB:** Trumbull entries with `h` clusters:
- `m'tah` — note the apostrophe indicating a reduced syllable
- `askkuhnk` — unusual `h` insertion
- `achm∞wonk` — `chm` cluster suggests an intermediate h-like transition

The apostrophe `'` in Trumbull may also represent elided /h/ or glottal stop in some contexts.

---

## 4. Entry Structure

Trumbull entries have a complex multi-part structure parsed into a single `lx` field:

```
*|achm∞wonk|, vbl. n. `news'    C.
```

Breaking this down:
- `*` — likely marks cross-reference or reconstructed form
- `|...|` — citation form with morpheme boundaries
- `vbl. n.` — grammatical label (verbal noun)
- `` `news' `` — gloss in backtick quotes
- `C.` — abbreviation (probably "Collins" or comparable reference)

```
|-adchaubuk|, in comp. words, root, or roots
```
- `|...|` — root citation
- `-` prefix — bound morpheme (cannot stand alone)
- `in comp. words, root, or roots` — grammatical note

```
|asqhutt∞che| `whilst'    C. = |asq-utt∞che|.
```
- Cross-reference syntax with `=`
- Internal hyphenation showing morpheme breakdown

---

## 5. Known Ambiguities

1. **∞ symbol** — The `∞→oozzz` mapping is established but the exact phonetics behind this convention are unclear. It may represent a breathy vowel, a vowel+glottal sequence, or a complex cluster
2. **Preaspiration** — /h/ before stops is inconsistently written. The apostrophe `'` and some digraphs may encode h-quality that is not phonetically explicit
3. **Vowel quality** — Eliot orthography shares the same ambiguity as Williams: `a`, `e`, `i`, `o`, `u` each map to 2-4 possible phonemes
4. **`c` ambiguity** — Before back vowels = /k/, before front vowels = /s/. This English convention is inconsistently applied
5. **Boundary markers** — The `|` pipes enclose citation forms, but embedded glosses, cross-references, and abbreviations inside the same lx field make parsing non-trivial
6. **gloss delimiters** — Backtick quotes `` `...' `` mark glosses but may span multi-word definitions

---

## 6. Recommended Approach

**DO NOT USE REGEX** — the ∞ symbol, pipe boundaries, embedded glosses, and cross-reference syntax require context-sensitive parsing.

1. **Preprocessing FSM (Stage 1):** Tokenize Trumbull entries by:
   - Recognizing `|...|` citation boundaries and stripping pipes
   - Identifying `∞` and replacing with `oozzz`
   - Extracting backtick-delimited glosses
   - Isolating grammatical abbreviations (vbl. n., C., etc.)
   - Handling `*` prefix and `= cross-reference` syntax

2. **Conversion FSM (Stage 2):** Apply Eliot→phoneme mapping rules:
   - Map Eliot vowel digraphs (ee, oo) to phonemes
   - Handle `c→k/s` disambiguation based on following vowel
   - Infer preaspiration /h/ from morphotactic position
   - Resolve ∞→oozzz (already mapped in Stage 1)

3. **Fallback/ML:** For ambiguous vowel quality (a/e/i/o/u), use:
   - Comparative evidence from Proto-Algonquian reconstructions (Aubin)
   - Sister-language evidence from Narragansett (Williams)
   - Known cognate patterns between Eliot orthography and modern Wampanoag revitalization

4. **Weighted State Transitions:** Encode known Eliot→phoneme mappings with confidence weights. Use the large corpus (4,491 entries) for distributional/statistical patterns — e.g., vowel quality predictions based on surrounding consonants.

The comparative mass of Trumbull (4,491 records vs. Williams' 2,134) makes statistical/ML approaches more viable here.
