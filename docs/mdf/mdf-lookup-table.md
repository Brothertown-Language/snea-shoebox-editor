# MDF TAG QUICK LOOKUP TABLE

This table is derived from the authoritative MDF documentation in `documentation/MDFields19a_UTF8.txt`.
Markers marked with **(f)** are free-form fields.

## RECORD MARKER
| Tag | Description | Notes |
| :--- | :--- | :--- |
| `\lx` | Lexical entry | Only one allowed per record. |

## BASIC FIELDS
| Tag | Description |
| :--- | :--- |
| `\ps` | Part of speech |
| `\pn` | Part of speech (national) |
| `\ge` | Gloss (English) |
| `\gn` | Gloss (national) |
| `\re` | Reversal (English) |
| `\rn` | Reversal (national) |
| `\de` | Definition (English) |
| `\dn` | Definition (national) |
| `\rf` | Reference to notebooks **(f)** |
| `\xv` | Example (vernacular) **(f)** |
| `\xe` | Example (English) **(f)** |
| `\xn` | Example (national) **(f)** |
| `\cf` | Cross reference |
| `\ce` | Cross ref. (English) |
| `\cn` | Cross ref. (national) |
| `\nt` | Notes, etc. **(f)** |
| `\dt` | Datestamp |

## RESERVED FIELDS
| Tag | Description |
| :--- | :--- |
| `\hm` | Homonym number |
| `\lc` | Lexical citation |
| `\se` | Subentry |
| `\sn` | Sense number |

## OPTIONAL FIELDS
| Tag | Description | Tag | Description |
| :--- | :--- | :--- | :--- |
| `\gv` | Gloss (vernacular) | `\1i` | 1st plural incl. form |
| `\gr` | Gloss (regional) | `\2p` | 2nd plural form |
| `\rr` | Reversal (regional) | `\3p` | 3rd plural form |
| `\we` | Word-gloss (English) | `\4p` | Plural non-human form |
| `\wn` | Word-gloss (national) | `\ph` | Phonetic form |
| `\wr` | Word-gloss (regional) | `\cr` | Cross ref. (regional) |
| `\dv` | Definition (vernacular) | `\mr` | Morphemic form |
| `\dr` | Definition (regional) | `\rd` | Reduplication form |
| `\xr` | Example (regional) **(f)** | `\va` | Variant form |
| `\pd` | Paradigm set | `\ve` | Variant (English) |
| `\pdl` | Paradigm label | `\vn` | Variant (national) |
| `\pdv` | Paradigm form (vernacular) | `\vr` | Variant (regional) |
| `\pde` | Paradigm gloss (English) | `\mn` | Main entry form |
| `\pdn` | Paradigm gloss (national) | `\lf` | Lexical function |
| `\pdr` | Paradigm gloss (regional) | `\lv` | Lexeme ref'd by lexical function |
| `\sg` | Singular noun form | `\le` | Lexical function (English) |
| `\pl` | Plural noun form | `\ln` | Lexical function (national) |
| `\1s` | 1st singular verb form | `\lr` | Lexical function (regional) |
| `\2s` | 2nd singular verb form | `\sy` | Synonyms |
| `\3s` | 3rd singular verb form | `\an` | Antonyms |
| `\4s` | Singular non-human form | `\uv` | Usage (vernacular) **(f)** |
| `\1d` | 1st dual verb form | `\ue` | Usage (English) **(f)** |
| `\2d` | 2nd dual verb form | `\un` | Usage (national) **(f)** |
| `\3d` | 3rd dual verb form | `\ur` | Usage (regional) **(f)** |
| `\4d` | Dual non-human form | `\ov` | Only (vernacular) **(f)** |
| `\1p` | 1st plural form | `\oe` | Only (English) **(f)** |
| `\1e` | 1st plural excl. form | `\on` | Only (national) **(f)** |
| `\ev` | Encyclopedic (vernacular) **(f)** | `\or` | Only (regional) **(f)** |
| `\ee` | Encyclopedic (English) **(f)** | `\bw` | Borrowed word |
| `\en` | Encyclopedic (national) **(f)** | `\et` | Etymology |
| `\er` | Encyclopedic (regional) **(f)** | `\eg` | Etymology (gloss) |
| `\is` | Index of semantics | `\es` | Etymology (source) |
| `\th` | Thesaurus | `\ec` | Etymology (comment) **(f)** |
| `\sc` | Scientific name | `\sd` | Semantic domain |
| `\pc` | Picture **(f)** | `\bb` | Bibliographic ref. **(f)** |
| `\ng` | Notes on grammar **(f)** | `\tb` | Table/chart **(f)** |
| `\na` | Notes on anthropology **(f)** | `\np` | Notes on phonology **(f)** |
| `\nq` | Questions **(f)** | `\nd` | Notes on discourse **(f)** |
| `\so` | Source of data | `\ns` | Sociolinguistics **(f)** |
| | | `\st` | Status |
