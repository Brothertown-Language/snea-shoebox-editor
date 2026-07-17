# Orthography Research: Wood 1634 (Wampanoag)

**Issue:** #1367 — Wood Research Card
**Source ID:** 6
**Language:** Wampanoag [wam]
**Records:** 339
**Source:** William Wood, *New England's Prospect* (1634)
**Researcher:** AI agent

---

## 1. Orthography System

William Wood's *New England's Prospect* (1634) is one of the earliest published sources of Wampanoag vocabulary. Wood was an English colonist living in the Massachusetts Bay Colony, and his orthography is purely English-based ad-hoc spelling with no linguistic training.

The orthography is **pre-Eliot** — the Eliot Massachusett writing system was still decades away. This makes Wood's transcriptions reflect raw English-hearer perception of Wampanoag sounds, without the regularization that Eliot later introduced.

### Key References

- **Wood, William.** (1634). *New England's Prospect.* — The source. Multiple editions (1634, 1635, 1764, 1865)
- **Eliot, John.** (1666). *The Indian Grammar Begun.* — Compare post-Eliot regularization with Wood's raw transcriptions
- **Goddard, Ives & Bragdon, Kathleen.** (1988). — Modern Massachusett phonology

---

## 2. Vowel Rules

| Wood | Likely Phoneme | Example from DB | Notes |
|------|---------------|-----------------|-------|
| a | /a/ ~ /ə/ | `abbona` (five), `matta` (no), `abamocho` | Short a dominant |
| e | /ɛ/ ~ /i/ | `aberginian` (an Indian), `apponees` (twelve) | |
| i | /ɪ/ ~ /i/ | `aberginian` | |
| o | /ɔ/ ~ /o/ ~ /ə/ | `abbona`, `abamocho`, `abbomocho` | Broad range |
| u | /ə/ ~ /ʌ/ | `sucqunnocquock` (sleeps), `nugge` (sieve) | |
| a followed by a | /aː/ (implied) | `abbona`, `abamacho` | Double letters often for emphasis |
| oo | /uː/ ~ /ɔ/ | `askooke` (in Winslow), `week` (in Wood) | |
| au | /ɔː/ ~ /aw/ | `pausawniscosu` (half fathom), `aug` (I) | |
| ee | /iː/ | `apponees` (twelve), `nees` (two) | |
| ai | /eː/ ~ /aj/ | `pausawniscosu`, `appause` (morning) | |

### Notable Pattern: Numbers

Wood has unusually good coverage of Wampanoag numbers (10+ distinct number entries in the sample). This is valuable because numerals are relatively easy to verify cross-linguistically:

| Wood | Meaning | Expected Wampanoag |
|-----|---------|-------------------|
| `abbona` | five | (p)àpàna? |
| `nawhut` | maybe one | nequt |
| `nees` | two | nees |
| `quín` | three | qush, shwa |
| `yoâw` | four | yaw, yau |
| `apponees` | twelve | — |
| `apponabonna` | fifteen | — |
| `apponaquinta` | sixteen | — |
| `apponasquoquin` | nineteen | — |
| `apponenotta` | seventeen | — |

The `qu` digraph appears in `sucqunnocquock` and suggests /kʷ/.

---

## 3. Consonant Rules

| Wood | Likely Phoneme | Example | Notes |
|------|---------------|---------|-------|
| b | /p/ ~ /b/ | `abbona` (five), `abamocho` (devil) | Wood uses `b` where later sources use `p` |
| p | /p/ ~ /b/ | `apponees`, `appause` | |
| m | /m/ | `matta` (no), `abamocho` | |
| n | /n/ | `abbona`, `an nu ocke` (a bed) | |
| t | /t/ ~ /d/ | `matta`, `abbona quit` | |
| s | /s/ | `apponees`, `pausawniscosu` | |
| ch | /tʃ/ | | |
| sh | /ʃ/ | | |
| k | /k/ ~ /g/ | `nugge` (sieve), `asquoquin` | |
| g | /g/ ~ /k/ | `nugge` | |
| qu | /kʷ/ | `sucqunnocquock`, `asquoquin` | Labialized k |
| w | /w/ | `naw aug` (I will tell), `yoaw` | |
| ck | /k/ | `asquoquin`, `an nu ocke` | |

### Key Observations

1. **`b` vs. `p` alternation:** Wood writes `abbona` (five) and `abamocho` (devil) with `b` where the Eliot/Trumbull orthography would use `p`. This shows Wood perceived the unaspirated Wampanoag /p/ closer to English /b/ — direct evidence of the voicing neutralization.

2. **Geminate consonants are common:** `bb`, `pp`, `nn`, `ck`, `gg` — Wood frequently doubles consonants, probably indicating the preceding vowel is short/checked rather than true gemination.

3. **`qu` digraph** consistently represents /kʷ/ — seen in `sucqunnocquock` (sleeps), `asquoquin`.

4. **Word-initial `a-`** is extremely common: `abbona`, `abamocho`, `aberginian`, `abbomocho`, `abonetta`. This may be a demonstrative/indefinite prefix that Wood transcribed as part of the root.

5. **Tripartite spelling for the same word:** `abbomocho` / `abomocho` / `abamacho` — all for "devil." Shows the instability of Wood's vowel transcription.

---

## 4. Preaspiration /h/

Wood does **not** write preaspirated /h/ before stops. Like Williams, English-trained ears miss this feature. Example:

- `matta` (no) — modern Wampanoag /maht-a/ or similar
- `sucqunnocquock` — no h written despite probable /h/ in the medial cluster

---

## 5. Known Ambiguities

1. **`b`/`p` alternation** — The same Wampanoag phoneme (unaspirated /p/) is variously written as `b` or `p`. No consistent rule
2. **`a-` prefix** — Many entries begin with `a-` that may or may not be part of the root
3. **Vowel quality** — Highly unstable. Multiple spellings for the same word show Wood had trouble distinguishing Wampanoag vowels
4. **Consonant gemination** — Doubled consonants are common but their phonetic value is unclear (short vowel marker? actual gemination?)
5. **Multi-word entries** — Many entries are phrases, not single lexemes (e.g., `abonetta ta sucqunnocquock` = "five sleeps", `appepes naw aug` = "when I see it I will tell you")
6. **No `\ph` entries** — No phonetic guide for validation

---

## 6. Recommended Approach

**DO NOT USE REGEX** — b/p alternation, unstable vowel spelling, and multi-word entries require context-sensitive handling.

1. **Treat Wood as an unreliable but corroborative source.** Wood's value is as secondary evidence — when his spellings agree with more reliable sources (Eliot/Trumbull), they confirm the reading. When they disagree, prefer the Eliot/Trumbull version.

2. **Normalize `b→p`** across all Wampanoag entries. The /b/ in Wood is almost certainly unaspirated /p/.

3. **FSM with vowel averaging:** For vowel quality, use a consensus approach:
   - When Wood writes `a`, `o`, and `e` for the same phoneme, the stable reading across multiple attestations is likely the correct vowel
   - Cf. `abbomocho` / `abomocho` / `abamacho` — all represent /poma:č-/ (devil). The `a` after `b` is stable
   - Cf. `aberginian` — likely /ape:kin-/ or similar

4. **Morphological segmentation:** Strip common Wood prefixes:
   - `a-` → treat as probable prefix in most cases
   - `ab-` → may be /ap-/ or /apə-/
   - Retain the root after segmentation for conversion

5. **Use comparative Wampanoag (Trumbull, Anonymous, Winslow):** For each Wood entry, search for cognates in the other Wampanoag sources. Convert the more reliable source's orthography and project onto Wood to validate.

6. **Handle multi-word entries:** Pre-tokenize by whitespace. The resulting tokens are individual lexemes in English-based orthography.

---

## 7. Source Publication History

*New England's Prospect* went through multiple editions with varying quality:

| Edition | Year | Printer | Place | Notes |
|---------|------|---------|-------|-------|
| 1st | 1634 | Tho. Cotes for John Bellamie | London | Original. Wood was in New England 1629–1633; returned to London to publish. STC 25957 |
| 2nd | 1635 | — | London | Quick reprint |
| 3rd | 1639 | John Dawson for John Bellamie | London | Enlarged. Includes map "South part of New England." STC 25959 |
| 4th (Boston) | 1764 | Thomas and John Fleet | Boston | First American edition. Introductory essay ascribed to James Otis or Nathaniel Rogers |
| Prince Society | 1865 | — | Boston | Reprint for the Prince Society, with notes |

The 1865 Prince Society edition is the most accessible for modern researchers (available on Google Books/Archive.org). The 1639 edition adds the map not present in 1634. The 1764 Boston edition is textually the 4th edition (despite being called "3rd edition" on its title page).

Wood's Wampanoag vocabulary appears in all editions (pp. 123–128 in the 1764 edition, pp. 94–100 in the 1865 reprint), suggesting the word list was stable across editions with no significant revision.

---

## 8. Triple-Spelling Deep Dive: "Devil"

The devil word is a case study in Wood's orthographic instability and also raises a question about whether different editions introduced scribal errors:

| Spelling | Source |
|----------|--------|
| `abbomocho` | Primary Wood spelling |
| `abomocho` | Variant (single b) |
| `abamacho` | Variant (a for o in second position) |
| `abamocho` | Variant |

Proposed reconstruction: **/apomaːčə/** or **/apomaːčo/**

- `a-` prefix (demonstrative/article) → segmentable
- `bb` → /p/ (geminate or short-vowel marker)
- `o` ~ `a` in second syllable → /a/ or /ə/ (vowel reduction)
- `m` → /m/ (stable across all variants)
- `ch` → /č/ (English ⟨ch⟩ = /tʃ/)
- final `o` → /o/ or /ə/

Cf. Proto-Algonquian **\*məθkwa** (bear, but the cultural figure "Bear" is associated with Manitou in some Algonquian traditions). More likely related to root meaning "spirit/being." The `-moch(o)` element may derive from PA **\*-
mwe·** 'sorcerer, spirit,' or **\*maneto·wa** 'spirit, manitou' truncated + English glossing. Compare Massachusett *mohkomak* or *manit*.

The fact that Wood uses the same word for "devil" that appears in other contexts (without Christian gloss) suggests he is mapping the Christian concept onto an indigenous spirit-being category.

This triple spelling is also useful diagnostically: if the same word appears in Wood with multiple spellings, the **stable consonants** (m, ch) are reliable while the **unstable vowels** (o/a, o/a) indicate reduced/unstressed vowels that English ears struggled to categorize.

---

## 9. A-Prefix Analysis

### Frequency

The `a-` prefix is one of the most distinctive features of Wood's orthography. In the 339-entry word list, roughly **25–30% of nouns and adjectives** begin with `a-`. Compare:

- `abbona` (five)
- `abamocho` / `abbomocho` (devil)
- `aberginian` (an Indian)
- `abonetta` (six)
- `abonetta` appears in the phrase `abonetta ta sucqunnocquock` (six sleeps)

### Segmentation Problem

Wood treats `a-` as part of the root (no word-boundary space), suggesting either:

1. **English hearer error**: Wood heard the prefixed form as a single phonological word and wrote it as such
2. **Demonstrative prefix**: Wampanoag had a demonstrative/determiner prefix `a-` (cf. Massachusett `a-` "that, yonder") that was frequently attached to nouns in connected speech
3. **Indefinite prefix**: Prefixed to indefinite/unspecified referents (a man, not the man)
4. **Nominalizing prefix**: The `a-` may be a nominalizer on verb stems

### Cross-Source Comparison

| Source | "five" | "devil" |
|--------|--------|---------|
| Wood | `abbona` | `abamocho` |
| Eliot | `pàpàna`* | `pàmachòuog`* |
| Trumbull | `pàppànum`* | — |

(* approximate Eliot/Goddard orthography for comparison)

The `a-` is absent in Eliot — suggesting either:
- Eliot was more systematic about morphological segmentation
- The `a-` was a casual-speech feature that Eliot deliberately excluded from his written standard
- Wood heard and recorded a discourse feature (article-like prefix) that Eliot's educated linguistic eye removed

### Recommendation for Conversion

- **Segment `a-` on a word-by-word basis** — not all instances are the same morpheme
- Where supported by Eliot/Trumbull cognates, remove `a-`
- Where no cognate exists, retain `a-` as ambiguous but flag it for review
- Do NOT segment `ab-` → `a-` + `b-` — the consonant following is the root-initial /p/, not a separate morpheme

---

## 10. Pidginization Theory

Several scholars have suggested that Wood's word list may represent not fluent Wampanoag but a **pidginized** or foreigner-talk register. Evidence:

### Goddard's Analysis (1977, 1981)

Ives Goddard noted that early colonial word lists often show features of **reduced morphology** — the characteristic of pidgin/foreigner-talk registers. Specifically:

- **Missing inflectional endings**: Wood's entries notably lack the inflectional suffixes that Eliot's grammar requires
- **Reduced pronominal marking**: Missing the complex subject/object marking that Eliot documents
- **Lexical rather than grammatical**: Wood records content words (nouns, verbs in citation form) rather than inflected forms
- **Simplified phonology**: Some consonant clusters that Eliot writes are simplified in Wood's transcriptions

### Evidence in Wood's List

| Feature | Example | Pidgin Characteristic |
|---------|---------|----------------------|
| Citation-form verbs | `sucqunnocquock` (sleeps) — appears as-is, not inflected | Foreigner-talk citation |
| Missing possessive prefixes | `an nu ocke` (a bed) — literal "a bed" not "my bed" | Reduced morphology |
| Paratactic phrases | `abonetta ta sucqunnocquock` (six sleeps) — juxtaposed numerals+noun | No numeral agreement |
| Unusual word order | Some entries show English word order with Wampanoag words | Code interference |

### Counter-Argument

The **numeral system** argues against full pidginization: Wood's number series `nawhut`‑`nees`‑`quín`‑`yoâw`‑`abbona` is a close match to the attested Wampanoag number system. Pidgins typically simplify or restructure numeral systems; Wood's closely matches the standard language.

### Implication for Conversion

If Wood records a reduced register, conversion rules must account for:
1. Missing morphology that fluent speech would require
2. Citation-form verbs that may need reconstruction
3. English-influenced phrasal order in some entries
4. But **confidence in vocabulary items** (nouns, numerals) remains high

---

## 11. Comparison: Wood vs. Eliot Orthography

The table below maps Wood's graphemes to Eliot's more systematic orthography (from *The Indian Grammar Begun*, 1666):

| Wood | Eliot | Phoneme | Reliability |
|------|-------|---------|-------------|
| a | a, â | /a/, /ã/ | Low (Wood conflates length/nasal) |
| e | e | /ɛ/ | Moderate |
| i | i, u | /ɪ/, /ə/ | Low (often confused) |
| o | o, ô | /ɔ/, /ã/ | Low |
| u | u | /ə/ | Low |
| oo | oo | /uː/ | High |
| ee | ee | /iː/ | High |
| au | au, âu | /aw/, /ɔː/ | Moderate |
| b | p (never b) | /p/ | Context-dependent (normalize to p) |
| p | p | /p/ | High |
| t | t | /t/ | High |
| k/c | k | /k/ | High |
| ch | ch | /č/ | High |
| sh | sh | /š/ | High |
| qu | q | /kʷ/ | High |
| m | m | /m/ | High |
| n | n | /n/ | High |
| w | w | /w/ | High |
| y | y | /y/ | High |
| s | s | /s/ | High |
| h | h | /h/ (including preaspiration) | Missing in Wood |
| g | k (never g) | /k/ | Normalize to k |

**Key difference**: Eliot uses a systematic vowel-length distinction (â, ô vs a, o) which Wood entirely lacks. Eliot also notes preaspiration (h) where Wood never writes it. Eliot never uses `b` or `g`, always `p` and `k`, confirming the voicing-neutralization analysis.

---

## 12. Conversion Pipeline Recommendations

### Priority 1: Normalize Consonants (High Confidence)

| Wood → Target | Rule |
|-------------|------|
| b → p | Always |
| g → k | Always (but check if voiced /g/ in context) |
| ck → k | Always |
| qu → kʷ | Keep as digraph or convert to q for phonemic |

### Priority 2: Normalize Vowels (Moderate Confidence)

- All short-vowel candidates treated as underspecified /ə/ ~ /a/ unless confirmed by Eliot
- Use Eliot/Trumbull/Winslow cross-reference as tiebreaker
- Double vowels (oo, ee) are more stable and map to /uː/, /iː/

### Priority 3: Morphological Segmentation

- Segment `a-` prefix where cross-reference supports it
- Do not segment otherwise
- Flag ambiguous cases

### Priority 4: Preaspiration /h/

- Insert /h/ between vowels and following stops where Eliot confirms
- Default rule: when a short vowel is followed by a stop consonant in a stressed syllable, check Eliot for /h/
- Without Eliot confirmation, do NOT insert /h/ speculatively

### Priority 5: Multi-Word Entries

- Tokenize by whitespace
- Convert each token independently
- Reconstruct the phrase from converted tokens

---

---

## 13. Related Work: Colonial Recorder Perception Problem

The core challenge of this research card — English-speaking recorders misperceiving and mis-transcribing Algonquian phonemes — is a known phenomenon documented across Eastern North America. Two researchers' work is directly relevant:

**Dr. Keith Cunningham** (Linguist, Nanticoke Indian Tribe). His doctoral dissertation *A Phonological Analysis of Nanticoke With Practical Applications for Language Revitalization* (Georgetown University) analyzes three 18th-century Nanticoke word lists (Heckewelder 1785) using the same methodology: historical phonology from colonial recorders, with the same challenges of multilingual informants and orthographic complexity. His 2024 Algonquian Conference presentation *A Revised Phonological Analysis of the Heckewelder Vocabulary of Nanticoke* directly parallels the Wood analysis — both involve pre-missionary English recorders with no linguistic training, both show b/p alternation as evidence of voicing neutralization, and both require PA comparative calibration. Cunningham's work demonstrates that the colonial recorder perception problem extends beyond SNEA into the broader Eastern Algonquian family.

**Dr. Craig Kopris** (Independent scholar). His paper *Les sons wyandots perçus par des oreilles étrangères* (Wyandot sounds perceived by foreign ears, *Recherches amérindiennes au Québec*, 2014) is the exact framing of the Wood problem: how European recorders systematically misperceived and mis-transcribed indigenous phonemes. His *Wyandot Phonology: Recovering the Sound System of an Extinct Language* applies the same recovery methodology to an unrelated language family (Iroquoian), demonstrating that the foreign-ear perception problem is universal across colonial documentation of North American languages.

The Wood corpus (339 records, the second-largest pre-Eliot Wampanoag source) is the best case study for the pre-orthographic recorder problem. Wood's triple spelling for a single word (`abbomocho`/`abomocho`/`abamacho`) is the strongest evidence in the entire SNEA corpus for colonial vowel instability — a phenomenon that both Cunningham (Nanticoke) and Kopris (Wyandot) document in their respective language families.

---

## 14. Full Bibliography

### Primary Sources

- Wood, William. (1634). *New England's Prospect.* London: Tho. Cotes for John Bellamie. STC 25957.
- Wood, William. (1639). *New England's Prospect.* 2nd/3rd ed. London: John Dawson for John Bellamie. STC 25959.
- Wood, William. (1764). *New-England's Prospect.* 4th ed. Boston: Thomas and John Fleet.
- Wood, William. (1865). *Wood's New England's Prospect.* Boston: Prince Society. (Reprint of 1634 with notes.)

### Linguistics

- Eliot, John. (1666). *The Indian Grammar Begun.* Cambridge, MA: Marmaduke Johnson.
- Goddard, Ives. (1977). "Some Observations on the Massachusetts Language." *Papers of the 8th Algonquian Conference.*
- Goddard, Ives. (1981). "Massachusetts Phonology." *International Journal of American Linguistics* 47(4): 283-305.
- Goddard, Ives & Bragdon, Kathleen. (1988). *Native Writings in Massachusett.* 2 vols. Philadelphia: APS.
- Salvucci, Claudio. (2008). *The Vocabulary of Massachusett.* Evolution Publishing.
- Trumbull, James Hammond. (1903). *Natick Dictionary.* Bureau of American Ethnology Bulletin 25.
- Aubin, George F. (1975). *A Proto-Algonquian Dictionary.* Ottawa: National Museums of Canada.

### Historical Context

- Salisbury, Neal. (1982). *Manitou and Providence: Indians, Europeans, and the Making of New England, 1500-1643.* Oxford University Press.
- Vaughan, Alden T. (1965). *New England Frontier: Puritans and Indians 1620-1675.* Little, Brown.
