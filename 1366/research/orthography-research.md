# Orthography Research: Winslow 1624 (Wampanoag)

**Issue:** #1366 — Winslow Research Card
**Source ID:** 5
**Language:** Wampanoag [wam]
**Records:** 24
**Source:** Edward Winslow, *Good News from New England* (1624)
**Researcher:** AI agent

---

## 1. Orthography System

Edward Winslow's *Good News from New England* (1624) is the **earliest published source** of Wampanoag vocabulary in the corpus. Winslow was a Mayflower passenger and Plymouth Colony governor. His transcriptions are phonetically naïve English ad-hoc spellings — he was recording an entirely unfamiliar language with no reference system.

The orthography is purely **English-hearer perception** with zero regularization. Only 24 records exist in the DB.

### Key References

- **Winslow, Edward.** (1624). *Good News from New England.* — The source
- **Goddard, Ives & Bragdon, Kathleen.** (1988). *Native Writings in Massachusett.* — Comparative phonology
- **O'Brien, Frank Waobu.** — Guide to historical spellings

---

## 2. Vowel Rules

With only 24 records, the patterns are sparse but consistent with English spelling conventions:

| Winslow | Likely Phoneme | Example | Notes |
|---------|---------------|---------|-------|
| a | /a/ ~ /ə/ | `ahhe` (yes), `askooke` (snake), `matta` | Short a |
| e | /ɛ/ ~ /i/ | `chise` (old man), `ahhe`, `askooke` | Often word-final /ə/ |
| i | /ɪ/ ~ /i/ | `ewachim` (maize), `kiehchise` | |
| o | /ɔ/ ~ /o/ ~ /ə/ | `commaco` (feast), `hobbamock` (devil) | |
| u | /ə/ ~ /ʌ/ | `cuts` (speak) | |
| ie | /iː/ | `kiehchise` (old man), `kiehtan` (God) | English "ie" = /iː/ |
| oo | /uː/ | `askooke` (snake) | |
| ah | /aː/ or /ah/ | `ahhe` (yes) | May be vowel length or actual /h/ |

---

## 3. Consonant Rules

| Winslow | Likely Phoneme | Example | Notes |
|---------|---------------|---------|-------|
| h | /h/ | `ahhe`, `hobbamock`, `kiehtan` | Explicitly written |
| k | /k/ ~ /g/ | `kiehtan`, `askooke`, `commaco` | |
| ch | /tʃ/ | `chise`, `ewachim`, `kiehchise` | |
| m | /m/ | `commaco`, `ewachim`, `hobbamock` | |
| n | /n/ | | |
| s | /s/ | `askooke`, `chise`, `kiehchise`, `cuts` | |
| t | /t/ ~ /d/ | `kiehtan`, `matta cuts`, `commaco` | |
| c | /k/ (before a/o) | `commaco`, `cuts` | Hard c |
| w | /w/ | `ewachim`, `Winsnow` | |

### Key Observations

1. **`h` is written in most expected positions** — `ahhe`, `hobbamock`, `kiehtan`. Unlike Wood, Winslow seems to hear initial /h/ reasonably well. But preaspiration /h/ before stops (like the /ht/ in `kiehtan`) may be under-documented.

2. **`k` vs. `c` alternation:** Winslow uses both `k` and `c` for /k/. This is normal English orthography (`c` before a/o, `k` before e/i) but may obscure phonological patterns.

3. **`commaco`** — The `mm` geminate may indicate preceding vowel shortness rather than true gemination.

4. **Phonetically notable entries:**
   - `kiehtan` (God) — the `ht` cluster is important. In Wampanoag, this is a single phonological unit /ht/ or /h/
   - `hobbamock` (devil) — cognate with Wood's `abamocho`. Note Winslow writes initial `h` where Wood doesn't!
   - `keen Winsnow` — "art thou Winslow?" — shows 2nd person prefix `k-` + the name
   - `hinnaim namen, hinnaim michen, matta cuts` — a complex sentence showing the structure

---

## 4. Preaspiration /h/

Winslow writes `h` more consistently than Wood but less reliably than Edwards (Mahican). The `ht` in `kiehtan` is notable — Winslow may have heard /h/ before /t/ in this word, or the `h` may represent a different phonation.

Compare across Wampanoag sources:
- Winslow: `kiehtan` (with /h/)
- Trumbull/Eliot: would likely write `kehtan` or similar

---

## 5. Known Ambiguities

1. **Tiny corpus** — 24 records is insufficient for any statistical approach
2. **English loanwords?** — `hobbamock` may be partially influenced by English "hobgoblin" folk etymology in Winslow's perception
3. **Multi-word entries** — Some entries are sentences requiring segmentation
4. **No `\ph` entries** — No phonetic guide
5. **Proper names** — Some entries include English names (Winsnow = Winslow), which follow English orthography

---

## 6. Recommended Approach

**DO NOT USE REGEX** — the tiny corpus makes Winslow a corroborative source only.

1. **Treat Winslow as corroborative evidence only.** The 24 records are insufficient for independent conversion rules. For each Winslow entry, find the cognate in larger Wampanoag sources (Trumbull 4,491 records, Wood 339 records) and use the cross-source consensus.

2. **Key cognate mappings:**
   | Winslow | Wood | Trumbull/Eliot (expected) |
   |---------|------|--------------------------|
   | `hobbamock` (devil) | `abamocho`, `abomocho` | `pomma:č`? |
   | `matta cuts` (not speak) | `matta` (no) | `matta` |
   | `kiehtan` (God) | — | `kehtan` |
   | `commaco` (feast) | — | `kômak`? |

3. **Use Winslow's `h` transcriptions as secondary evidence** for where preaspiration occurs. When Winslow writes `h` and other sources also hear it, the /h/ is well-attested.

4. **Segment `k-` prefix:** The 2nd person prefix `k-` is seen in `keen Winsnow` and should be segmented from the root before conversion.

5. **Verify against Trumbull:** For each converted Winslow entry, verify against the expected form in the Eliot/Trumbull orthography. Flag mismatches for manual review.
