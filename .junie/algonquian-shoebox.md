---
author: Human
contributor: AI
status: complete
date: 2026-01-26
---

# Guidelines for Encoding Algonquian Polysynthetic Lexicon Entries in Shoebox/Toolbox

This document defines how to store headwords, inflections, person/object agreement, and morphological information in a Shoebox/Toolbox lexicon for Algonquian polysynthetic languages.

---

## 1. General principles

- One lexeme per entry: each lexical entry corresponds to one lexeme.
- Headword in `\lx`: the citation form is stored in `\lx`.
- Inflections inside the same record: inflected forms are stored inside the same record, not as separate entries.
- Inflectional space: inflectional information reflects person, object, animacy, obviation, order, and mode, not tense.
- Repeated fields: repeated fields (e.g., multiple `\inf` lines) are allowed and expected.

---

## 2. Required fields

| Field | Purpose |
|-------|---------|
| `\lx` | Headword (citation form) |
| `\ps` | Part of speech (AI, II, TA, TI, N, etc.) |
| `\ge` | English gloss (for headword or inflection) |
| `\de` | Full definition |
| `\inf` | Inflected surface form |
| `\infg` | Inflectional features (person→object, order, mode, etc.) |
| `\morph` | Morphological segmentation of the inflected form |
| `\morphg` (optional) | Morpheme glosses |

---

## 3. Encoding inflected forms

### 3.1 Surface form

Store each inflected form in its own `\inf` field:

\`\`\`
\inf  niwîcihâw
\`\`\`

### 3.2 Inflectional features

Use compact, typologically clear notation:

- Person→object:
  - `1→3` = first person acting on third
  - `3→2` = third person acting on second
  - `3→3'` = proximate acting on obviative
  - `1PL.EXCL→3` etc. as needed
- Order/mode:
  - `IND`, `CONJ`, `IMP`
- Number:
  - `SG`, `PL`
- Verb class (optional if already in `\ps`):
  - `TA`, `TI`, `AI`, `II`

Example:

\`\`\`
\infg 1→3 IND
\`\`\`

### 3.3 Morphological segmentation

Use segmentation only (no glossing) in `\morph`:

\`\`\`
\morph ni- + wîcihê- + -âw
\`\`\`

If glosses are needed, use a separate field `\morphg`:

\`\`\`
\morphg 1SG + help + DIR
\`\`\`

---

## 4. Recommended conventions

### 4.1 Headword morphology

Only include `\morph` for the headword if it is morphologically complex:

\`\`\`
\morph wîcihê- + -w
\`\`\`

### 4.2 Inflection morphology

Each `\inf` should be followed by its own `\ge`, `\infg`, and `\morph` block:

\`\`\`
\inf  niwîcihâw
\ge   I help him
\infg 1→3 IND
\morph ni- + wîcihê- + -âw
\`\`\`

The use of `\ge` in the inflection block provides a specific English translation for that form, which is essential for community accessibility and clarity in polysynthetic languages where an inflected form functions as a full proposition.

### 4.3 Order of fields

Recommended order inside each entry:

\`\`\`
\lx
\ps
\ge
\de

\inf
\ge
\infg
\morph

\inf
\ge
\infg
\morph
\`\`\`

---

## 5. Lexicon entry template

```markdown
# Shoebox/Toolbox Lexicon Entry Template (Algonquian Polysynthetic)

# Headword information
\lx   ${HEADWORD}
\ps   ${POS}
\ge   ${GLOSS}
\de   ${DEFINITION}

# Optional: headword morphology (only if morphologically complex)
# \morph ${HEADWORD_MORPH}

# ============================
# Inflection Block 1
# ============================
\inf   ${INFLECTED_FORM_1}
\ge    ${ENGLISH_TRANSLATION_1}
\infg  ${PERSON_OBJECT_1} ${ORDER_MODE_1}
\morph ${MORPH_SEGMENTATION_1}
# \morphg ${MORPH_GLOSSES_1}

# ============================
# Inflection Block 2
# ============================
# Duplicate this block as needed

# \inf   ${INFLECTED_FORM_2}
# \ge    ${ENGLISH_TRANSLATION_2}
# \infg  ${PERSON_OBJECT_2} ${ORDER_MODE_2}
# \morph ${MORPH_SEGMENTATION_2}
# \morphg ${MORPH_GLOSSES_2}

# ============================
# Notes
# ============================
# - PERSON_OBJECT uses notation like: 1→3, 3→2, 3→3', 1PL.EXCL→3
# - ORDER_MODE uses: IND, CONJ, IMP
# - POS uses: vTA, vTI, vAI, vII, N, etc.
# - Keep all inflections inside the same entry.
# - Repeat inflection blocks as needed.
```

---

## 6. Example: TA verb entry (Algonquian-style)

\`\`\`
\lx   wîcihêw
\ps   vTA
\ge   help (someone)
\de   to help someone

\inf  niwîcihâw
\ge   I help him
\infg 1→3 IND
\morph ni- + wîcihê- + -âw

\inf  kiwîcihâw
\ge   you help him
\infg 2→3 IND
\morph ki- + wîcihê- + -âw

\inf  wîcihêwak
\ge   they help him/her
\infg 3→3' PL IND
\morph wîcihê- + -w + -ak

\inf  niwîcihân
\ge   that I help him (if/when I help him)
\infg 1→3 CONJ
\morph ni- + wîcihê- + -ân
\`\`\`

---

## 7. Example: SNEA-style (Proto-SNEA / Mohegan-Pequot-like)

\`\`\`
\lx   *mehtuw
\ps   vTA
\ge   give (to someone)
\de   to give to someone

\inf  nmehtuw
\ge   I give it to him
\infg 1→3 IND
\morph n- + mehtu- + -w

\inf  kmehtuw
\ge   you give it to him
\infg 2→3 IND
\morph k- + mehtu- + -w

\inf  mehtuwak
\ge   they give it to him
\infg 3→3' PL IND
\morph mehtu- + -w + -ak
\`\`\`

---

## 8. Summary of best practices

- Keep all inflections inside the same lexical entry.
- Use `\inf` for the surface form, `\ge` for the specific English translation, `\infg` for person/object and related features, and `\morph` for segmentation.
- Use compact, consistent notation for person→object relationships and order/mode.
- Separate segmentation (`\morph`) from glossing (`\morphg`).
- Maintain a consistent field order for readability and machine parsing.
