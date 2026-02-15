# ⭐ The De Facto Standard Layout for Algonquian Dictionaries

Across Cree, Ojibwe, Mi’kmaq, Munsee, Mohegan‑Pequot, Passamaquoddy‑Maliseet, and other Algonquian languages, dictionaries tend to share the same **core architecture**:

## 1. **Headword (Lexeme)**
- Usually the **underlying stem** or **citation form**
- For verbs: **AI, II, TA, TI** class is encoded here or in the part‑of‑speech field
- For nouns: **animacy** is encoded here or in the POS field

**Examples:**
- wîcihêw (Cree TA verb)
- ahkosiw (Cree AI)
- nəmahq (Passamaquoddy noun)

## 2. **Part of Speech + Morphosyntactic Class**
This is extremely standardized in Algonquian lexicography:

| Category | Typical Label |
|---------|----------------|
| Animate noun | NA |
| Inanimate noun | NI |
| Animate intransitive verb | VAI |
| Inanimate intransitive verb | VII |
| Transitive animate verb | VTA |
| Transitive inanimate verb | VTI |

This is consistent across Cree, Ojibwe, Mi’kmaq, Passamaquoddy, Munsee, Mohegan‑Pequot, etc.

## 3. **English Gloss**
Usually a short, neutral gloss.

- "to help someone"
- "to be sick"
- "house"

## 4. **Extended Definition (Optional)**
Many Algonquian dictionaries include:
- cultural notes
- usage notes
- dialectal variation
- Proto‑forms (if historical)

## 5. **Inflectional Examples**
This is where Algonquian dictionaries differ from Indo‑European ones.
The standard practice is:

- Provide **a few representative inflected forms**, not the whole paradigm
- Include **person/object information**
- Include **order/mode** (IND, CONJ, IMP)
- Include **obviation** when relevant

This is exactly the pattern used with \inf and \infg fields.

## 6. **Morphological Segmentation**
Another near‑universal standard:

- Provide a **morpheme‑by‑morpheme breakdown**
- Optionally provide **glosses** in a separate field

This is essential for polysynthetic languages and is standard in Cree, Ojibwe, Passamaquoddy, and Mohegan‑Pequot lexica.

## 7. **Derivational Family / Stem Relations**
Algonquian dictionaries almost always include:

- related stems
- derivational variants
- theme‑sign variants
- noun/verb correspondences

Because Algonquian morphology is stem‑based and derivationally rich.

## 8. **Cross‑References**
Standard cross‑references include:

- synonyms
- antonyms
- variant spellings
- dialectal equivalents
- Proto‑Algonquian or Proto‑SNEA reconstructions (in scholarly dictionaries)

# 📘 Putting It Together: The Standard Template

Here’s the canonical structure used across Algonquian dictionaries:

HEADWORD  
POS (with animacy or verb class)  
English gloss  
Extended definition (optional)  
Inflected forms (selected)  
    Form  
    Person/Object features  
    Order/Mode  
Morphological segmentation  
Derivational family  
Cross-references  
Dialect/variant notes
