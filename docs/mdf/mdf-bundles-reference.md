# MDF Bundle Reference — Brothertown/Natick Project

> **Source of truth**: MDF 1.9a — `MDFields19a_UTF8.txt` (Buseman, 2006)
> Deprecated markers (`\1s`–`\4p` etc.) are excluded.
> **Section-boundary markers** (start new hierarchical sections): `\lx`, `\ps`, `\pn`, `\sn`, `\se`

## Overview

| Tag | Description | Bundle Group | Section Boundary | In Natick Output |
|-----|-------------|--------------|:----------------:|:----------------:|
| `\lx` | lexeme or headword of the lexical entry | Record Header | ✓ | ✓ |
| `\hm` | homonym number | Record Header | — | ✓ |
| `\lc` | lexical citation | Record Header | — | — |
| `\ph` | phonetic/phonemic form | Record Header | — | — |
| `\se` | subentry (a polymorphemic form or a phrase) | Part-of-Speech / Sense Section | ✓ | ✓ |
| `\ps` | part of speech | Part-of-Speech / Sense Section | ✓ | ✓ |
| `\pn` | part of speech (national) | Part-of-Speech / Sense Section | ✓ | — |
| `\sn` | sense number | Part-of-Speech / Sense Section | ✓ | ✓ |
| `\gv` | gloss (vernacular) | Gloss & Definition | — | — |
| `\dv` | definition (vernacular) | Gloss & Definition | — | — |
| `\ge` | gloss (English) | Gloss & Definition | — | ✓ |
| `\re` | reversal form (English) | Gloss & Definition | — | — |
| `\we` | word-level gloss (English) | Gloss & Definition | — | — |
| `\de` | definition (English) | Gloss & Definition | — | — |
| `\gn` | gloss (national) | Gloss & Definition | — | — |
| `\rn` | reversal form (national) | Gloss & Definition | — | — |
| `\wn` | word-level gloss (national) | Gloss & Definition | — | — |
| `\dn` | definition (national) | Gloss & Definition | — | — |
| `\gr` | gloss (regional) | Gloss & Definition | — | — |
| `\rr` | reversal form (regional) | Gloss & Definition | — | — |
| `\wr` | word-level gloss (regional) | Gloss & Definition | — | — |
| `\dr` | definition (regional) | Gloss & Definition | — | — |
| `\lt` | literal meaning | Literal Meaning / Scientific Name | — | — |
| `\sc` | scientific name | Literal Meaning / Scientific Name | — | ✓ |
| `\rf` | reference to notebooks, texts, etc. | Example Sentences | — | ✓ |
| `\xv` | example sentence (vernacular) | Example Sentences | — | ✓ |
| `\xe` | translation of example (English) | Example Sentences | — | ✓ |
| `\xn` | translation of example (national) | Example Sentences | — | — |
| `\xr` | translation of example (regional) | Example Sentences | — | — |
| `\uv` | usage (vernacular) | Usage | — | — |
| `\ue` | usage (English) | Usage | — | — |
| `\un` | usage (national) | Usage | — | — |
| `\ur` | usage (regional) | Usage | — | — |
| `\ev` | encyclopedic information (vernacular) | Encyclopedic Information | — | — |
| `\ee` | encyclopedic information (English) | Encyclopedic Information | — | — |
| `\en` | encyclopedic information (national) | Encyclopedic Information | — | — |
| `\er` | encyclopedic information (regional) | Encyclopedic Information | — | — |
| `\ov` | only   [restrictions]   (vernacular) | Restrictions | — | — |
| `\oe` | only [restrictions] (English) | Restrictions | — | — |
| `\on` | only [restrictions] (national) | Restrictions | — | — |
| `\or` | only [restrictions] (regional) | Restrictions | — | — |
| `\lf` | lexical function label | Lexical Functions | — | ✓ |
| `\lv` | vernacular lexeme referenced by the lexical function | Lexical Functions | — | ✓ |
| `\le` | lexical function (English gloss) | Lexical Functions | — | ✓ |
| `\ln` | lexical function (national gloss) | Lexical Functions | — | — |
| `\lr` | lexical function (regional gloss) | Lexical Functions | — | — |
| `\sy` | synonym | Synonyms / Antonyms | — | — |
| `\an` | antonym | Synonyms / Antonyms | — | — |
| `\mr` | morphemic representation | Morphology | — | ✓ |
| `\cf` | confer/cross-reference | Cross-References | — | ✓ |
| `\ce` | cross-reference (English gloss) | Cross-References | — | ✓ |
| `\cn` | cross-reference (national gloss) | Cross-References | — | — |
| `\cr` | cross-reference (regional gloss) | Cross-References | — | — |
| `\mn` | main entry form | Main Entry / Variants | — | — |
| `\va` | variant forms | Main Entry / Variants | — | ✓ |
| `\ve` | variant comment (English) | Main Entry / Variants | — | — |
| `\vn` | variant comment (national) | Main Entry / Variants | — | — |
| `\vr` | variant comment (regional) | Main Entry / Variants | — | — |
| `\bw` | borrowed word | Borrowed Word | — | — |
| `\et` | etymology | Etymology | — | ✓ |
| `\eg` | etymology-gloss | Etymology | — | ✓ |
| `\es` | etymology-source | Etymology | — | ✓ |
| `\ec` | etymology-comment | Etymology | — | ✓ |
| `\pd` | paradigm set | Paradigm | — | — |
| `\pdl` | paradigm label | Paradigm | — | — |
| `\pdv` | paradigm vernacular form | Paradigm | — | — |
| `\pde` | paradigm form (English gloss) | Paradigm | — | — |
| `\pdn` | paradigm form (national gloss) | Paradigm | — | — |
| `\pdr` | paradigm form (regional gloss) | Paradigm | — | — |
| `\sg` | singular form | Inflection Forms | — | — |
| `\pl` | plural form | Inflection Forms | — | ✓ |
| `\rd` | reduplication form(s) | Inflection Forms | — | — |
| `\tb` | table | Table | — | — |
| `\sd` | semantic domain | Semantic Domain | — | — |
| `\is` | index  of  semantics | Semantic Domain | — | — |
| `\th` | thesaurus | Semantic Domain | — | — |
| `\bb` | bibliographic reference | Bibliographic / Picture | — | — |
| `\pc` | picture | Bibliographic / Picture | — | — |
| `\nt` | notes, etc. | Notes | — | ✓ |
| `\np` | notes on phonology | Notes | — | — |
| `\ng` | notes on grammar | Notes | — | ✓ |
| `\nd` | notes on discourse | Notes | — | — |
| `\na` | notes  on   anthropology | Notes | — | — |
| `\ns` | notes on sociolinguistics | Notes | — | — |
| `\nq` | questions | Notes | — | — |
| `\so` | source of data | Source / Status / Datestamp | — | ✓ |
| `\st` | status | Source / Status / Datestamp | — | — |
| `\dt` | datestamp | Source / Status / Datestamp | — | — |

## Bundle Groups (Recommended Ordering per MDF 1.9a)

Tags are listed in the recommended field order from the official `Order_of_Fields` section.

### Record Header

**Section-boundary marker(s):** `\lx`

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\lx` | lexeme or headword of the lexical entry | ✓ | ✓ |
| 2 | `\hm` | homonym number | — | ✓ |
| 3 | `\lc` | lexical citation | — | — |
| 4 | `\ph` | phonetic/phonemic form | — | — |

### Part-of-Speech / Sense Section

**Section-boundary marker(s):** `\se`, `\ps`, `\pn`, `\sn`

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\se` | subentry (a polymorphemic form or a phrase) | ✓ | ✓ |
| 2 | `\ps` | part of speech | ✓ | ✓ |
| 3 | `\pn` | part of speech (national) | ✓ | — |
| 4 | `\sn` | sense number | ✓ | ✓ |

### Gloss & Definition

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\gv` | gloss (vernacular) | — | — |
| 2 | `\dv` | definition (vernacular) | — | — |
| 3 | `\ge` | gloss (English) | — | ✓ |
| 4 | `\re` | reversal form (English) | — | — |
| 5 | `\we` | word-level gloss (English) | — | — |
| 6 | `\de` | definition (English) | — | — |
| 7 | `\gn` | gloss (national) | — | — |
| 8 | `\rn` | reversal form (national) | — | — |
| 9 | `\wn` | word-level gloss (national) | — | — |
| 10 | `\dn` | definition (national) | — | — |
| 11 | `\gr` | gloss (regional) | — | — |
| 12 | `\rr` | reversal form (regional) | — | — |
| 13 | `\wr` | word-level gloss (regional) | — | — |
| 14 | `\dr` | definition (regional) | — | — |

### Literal Meaning / Scientific Name

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\lt` | literal meaning | — | — |
| 2 | `\sc` | scientific name | — | ✓ |

### Example Sentences

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\rf` | reference to notebooks, texts, etc. | — | ✓ |
| 2 | `\xv` | example sentence (vernacular) | — | ✓ |
| 3 | `\xe` | translation of example (English) | — | ✓ |
| 4 | `\xn` | translation of example (national) | — | — |
| 5 | `\xr` | translation of example (regional) | — | — |

### Usage

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\uv` | usage (vernacular) | — | — |
| 2 | `\ue` | usage (English) | — | — |
| 3 | `\un` | usage (national) | — | — |
| 4 | `\ur` | usage (regional) | — | — |

### Encyclopedic Information

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\ev` | encyclopedic information (vernacular) | — | — |
| 2 | `\ee` | encyclopedic information (English) | — | — |
| 3 | `\en` | encyclopedic information (national) | — | — |
| 4 | `\er` | encyclopedic information (regional) | — | — |

### Restrictions

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\ov` | only   [restrictions]   (vernacular) | — | — |
| 2 | `\oe` | only [restrictions] (English) | — | — |
| 3 | `\on` | only [restrictions] (national) | — | — |
| 4 | `\or` | only [restrictions] (regional) | — | — |

### Lexical Functions

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\lf` | lexical function label | — | ✓ |
| 2 | `\lv` | vernacular lexeme referenced by the lexical function | — | ✓ |
| 3 | `\le` | lexical function (English gloss) | — | ✓ |
| 4 | `\ln` | lexical function (national gloss) | — | — |
| 5 | `\lr` | lexical function (regional gloss) | — | — |

### Synonyms / Antonyms

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\sy` | synonym | — | — |
| 2 | `\an` | antonym | — | — |

### Morphology

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\mr` | morphemic representation | — | ✓ |

### Cross-References

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\cf` | confer/cross-reference | — | ✓ |
| 2 | `\ce` | cross-reference (English gloss) | — | ✓ |
| 3 | `\cn` | cross-reference (national gloss) | — | — |
| 4 | `\cr` | cross-reference (regional gloss) | — | — |

### Main Entry / Variants

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\mn` | main entry form | — | — |
| 2 | `\va` | variant forms | — | ✓ |
| 3 | `\ve` | variant comment (English) | — | — |
| 4 | `\vn` | variant comment (national) | — | — |
| 5 | `\vr` | variant comment (regional) | — | — |

### Borrowed Word

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\bw` | borrowed word | — | — |

### Etymology

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\et` | etymology | — | ✓ |
| 2 | `\eg` | etymology-gloss | — | ✓ |
| 3 | `\es` | etymology-source | — | ✓ |
| 4 | `\ec` | etymology-comment | — | ✓ |

### Paradigm

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\pd` | paradigm set | — | — |
| 2 | `\pdl` | paradigm label | — | — |
| 3 | `\pdv` | paradigm vernacular form | — | — |
| 4 | `\pde` | paradigm form (English gloss) | — | — |
| 5 | `\pdn` | paradigm form (national gloss) | — | — |
| 6 | `\pdr` | paradigm form (regional gloss) | — | — |

### Inflection Forms

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\sg` | singular form | — | — |
| 2 | `\pl` | plural form | — | ✓ |
| 3 | `\rd` | reduplication form(s) | — | — |

### Table

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\tb` | table | — | — |

### Semantic Domain

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\sd` | semantic domain | — | — |
| 2 | `\is` | index  of  semantics | — | — |
| 3 | `\th` | thesaurus | — | — |

### Bibliographic / Picture

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\bb` | bibliographic reference | — | — |
| 2 | `\pc` | picture | — | — |

### Notes

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\nt` | notes, etc. | — | ✓ |
| 2 | `\np` | notes on phonology | — | — |
| 3 | `\ng` | notes on grammar | — | ✓ |
| 4 | `\nd` | notes on discourse | — | — |
| 5 | `\na` | notes  on   anthropology | — | — |
| 6 | `\ns` | notes on sociolinguistics | — | — |
| 7 | `\nq` | questions | — | — |

### Source / Status / Datestamp

| Order | Tag | Description | Section Boundary | In Natick Output |
|------:|-----|-------------|:----------------:|:----------------:|
| 1 | `\so` | source of data | — | ✓ |
| 2 | `\st` | status | — | — |
| 3 | `\dt` | datestamp | — | — |

## All Tags Quick Reference (Alphabetical)

| Tag | Description | Bundle Group | Section Boundary | In Natick Output |
|-----|-------------|--------------|:----------------:|:----------------:|
| `\an` | antonym | Synonyms / Antonyms | — | — |
| `\bb` | bibliographic reference | Bibliographic / Picture | — | — |
| `\bw` | borrowed word | Borrowed Word | — | — |
| `\ce` | cross-reference (English gloss) | Cross-References | — | ✓ |
| `\cf` | confer/cross-reference | Cross-References | — | ✓ |
| `\cn` | cross-reference (national gloss) | Cross-References | — | — |
| `\cr` | cross-reference (regional gloss) | Cross-References | — | — |
| `\de` | definition (English) | Gloss & Definition | — | — |
| `\dn` | definition (national) | Gloss & Definition | — | — |
| `\dr` | definition (regional) | Gloss & Definition | — | — |
| `\dt` | datestamp | Source / Status / Datestamp | — | — |
| `\dv` | definition (vernacular) | Gloss & Definition | — | — |
| `\ec` | etymology-comment | Etymology | — | ✓ |
| `\ee` | encyclopedic information (English) | Encyclopedic Information | — | — |
| `\eg` | etymology-gloss | Etymology | — | ✓ |
| `\en` | encyclopedic information (national) | Encyclopedic Information | — | — |
| `\er` | encyclopedic information (regional) | Encyclopedic Information | — | — |
| `\es` | etymology-source | Etymology | — | ✓ |
| `\et` | etymology | Etymology | — | ✓ |
| `\ev` | encyclopedic information (vernacular) | Encyclopedic Information | — | — |
| `\ge` | gloss (English) | Gloss & Definition | — | ✓ |
| `\gn` | gloss (national) | Gloss & Definition | — | — |
| `\gr` | gloss (regional) | Gloss & Definition | — | — |
| `\gv` | gloss (vernacular) | Gloss & Definition | — | — |
| `\hm` | homonym number | Record Header | — | ✓ |
| `\is` | index  of  semantics | Semantic Domain | — | — |
| `\lc` | lexical citation | Record Header | — | — |
| `\le` | lexical function (English gloss) | Lexical Functions | — | ✓ |
| `\lf` | lexical function label | Lexical Functions | — | ✓ |
| `\ln` | lexical function (national gloss) | Lexical Functions | — | — |
| `\lr` | lexical function (regional gloss) | Lexical Functions | — | — |
| `\lt` | literal meaning | Literal Meaning / Scientific Name | — | — |
| `\lv` | vernacular lexeme referenced by the lexical function | Lexical Functions | — | ✓ |
| `\lx` | lexeme or headword of the lexical entry | Record Header | ✓ | ✓ |
| `\mn` | main entry form | Main Entry / Variants | — | — |
| `\mr` | morphemic representation | Morphology | — | ✓ |
| `\na` | notes  on   anthropology | Notes | — | — |
| `\nd` | notes on discourse | Notes | — | — |
| `\ng` | notes on grammar | Notes | — | ✓ |
| `\np` | notes on phonology | Notes | — | — |
| `\nq` | questions | Notes | — | — |
| `\ns` | notes on sociolinguistics | Notes | — | — |
| `\nt` | notes, etc. | Notes | — | ✓ |
| `\oe` | only [restrictions] (English) | Restrictions | — | — |
| `\on` | only [restrictions] (national) | Restrictions | — | — |
| `\or` | only [restrictions] (regional) | Restrictions | — | — |
| `\ov` | only   [restrictions]   (vernacular) | Restrictions | — | — |
| `\pc` | picture | Bibliographic / Picture | — | — |
| `\pd` | paradigm set | Paradigm | — | — |
| `\pde` | paradigm form (English gloss) | Paradigm | — | — |
| `\pdl` | paradigm label | Paradigm | — | — |
| `\pdn` | paradigm form (national gloss) | Paradigm | — | — |
| `\pdr` | paradigm form (regional gloss) | Paradigm | — | — |
| `\pdv` | paradigm vernacular form | Paradigm | — | — |
| `\ph` | phonetic/phonemic form | Record Header | — | — |
| `\pl` | plural form | Inflection Forms | — | ✓ |
| `\pn` | part of speech (national) | Part-of-Speech / Sense Section | ✓ | — |
| `\ps` | part of speech | Part-of-Speech / Sense Section | ✓ | ✓ |
| `\rd` | reduplication form(s) | Inflection Forms | — | — |
| `\re` | reversal form (English) | Gloss & Definition | — | — |
| `\rf` | reference to notebooks, texts, etc. | Example Sentences | — | ✓ |
| `\rn` | reversal form (national) | Gloss & Definition | — | — |
| `\rr` | reversal form (regional) | Gloss & Definition | — | — |
| `\sc` | scientific name | Literal Meaning / Scientific Name | — | ✓ |
| `\sd` | semantic domain | Semantic Domain | — | — |
| `\se` | subentry (a polymorphemic form or a phrase) | Part-of-Speech / Sense Section | ✓ | ✓ |
| `\sg` | singular form | Inflection Forms | — | — |
| `\sn` | sense number | Part-of-Speech / Sense Section | ✓ | ✓ |
| `\so` | source of data | Source / Status / Datestamp | — | ✓ |
| `\st` | status | Source / Status / Datestamp | — | — |
| `\sy` | synonym | Synonyms / Antonyms | — | — |
| `\tb` | table | Table | — | — |
| `\th` | thesaurus | Semantic Domain | — | — |
| `\ue` | usage (English) | Usage | — | — |
| `\un` | usage (national) | Usage | — | — |
| `\ur` | usage (regional) | Usage | — | — |
| `\uv` | usage (vernacular) | Usage | — | — |
| `\va` | variant forms | Main Entry / Variants | — | ✓ |
| `\ve` | variant comment (English) | Main Entry / Variants | — | — |
| `\vn` | variant comment (national) | Main Entry / Variants | — | — |
| `\vr` | variant comment (regional) | Main Entry / Variants | — | — |
| `\we` | word-level gloss (English) | Gloss & Definition | — | — |
| `\wn` | word-level gloss (national) | Gloss & Definition | — | — |
| `\wr` | word-level gloss (regional) | Gloss & Definition | — | — |
| `\xe` | translation of example (English) | Example Sentences | — | ✓ |
| `\xn` | translation of example (national) | Example Sentences | — | — |
| `\xr` | translation of example (regional) | Example Sentences | — | — |
| `\xv` | example sentence (vernacular) | Example Sentences | — | ✓ |

---
*Generated from `MDFields19a_UTF8.txt` (MDF 1.9a). Do not edit manually.*
