# Plan: Update Validator to Use Recommended MDF Tag Ordering

**Status:** 📋 Draft  
**Created:** 2026-03-04  
**Scope:** `src/mdf/validator.py` only

---

## Background

The previous analysis confirmed that `MDFValidator.REQUIRED_HIERARCHY` is incorrect:

```python
REQUIRED_HIERARCHY = ["lx", "so", "ps", "ge"]  # WRONG
```

Two problems:
1. **`\so` is misplaced.** Per `MDFields19a_UTF8.txt` (`Order_of_Fields`, line 1716), `\so` (source of data) appears near the **end** of the recommended order — after `\nt`, before `\st`/`\dt`. It is a valid MDF tag but has no defined position between `\lx` and `\ps`.
2. **The hierarchy is too narrow.** The official MDF standard defines a rich recommended ordering for all tag bundles. The validator should reflect the full structural sequence, not just 4 tags.

---

## Authority Source

`docs/mdf/original/MDFields19a_UTF8.txt` — `\key Order_of_Fields` section (lines 1567–1719).

The official recommended order for a standard `\lx` bundle (standard hierarchy) is:

```
\lx   lexical entry
\hm   homonym number
\lc   lexical citation
\ph   phonetic/phonemic form
\se   subentry          ← section boundary
\ps   part of speech    ← section boundary
\pn   part of speech-national
\sn   sense number      ← section boundary
\gv   gloss-vernacular
\dv   definition-vernacular
\ge   gloss-English
\re   reversal form-English
\we   word gloss-English
\de   definition-English
\gn   gloss-national
\rn   reversal form-national
\wn   word gloss-national
\dn   definition-national
\gr   gloss-regional
\rr   reversal form-regional
\wr   word gloss-regional
\dr   definition-regional
\lt   literal meaning
\sc   scientific name
\rf   reference
\xv   example-vernacular
\xe   example-English
\xn   example-national
\xr   example-regional
\uv   usage-vernacular
\ue   usage-English
\un   usage-national
\ur   usage-regional
\ev   encyclopedic info-vernacular
\ee   encyclopedic info-English
\en   encyclopedic info-national
\er   encyclopedic info-regional
\ov   only [restrictions]-vernacular
\oe   only [restrictions]-English
\on   only [restrictions]-national
\or   only [restrictions]-regional
\lf   lexical function label
\lv   vernacular lexeme (lexical function)
\le   lexical function-English gloss
\ln   lexical function-national gloss
\lr   lexical function-regional gloss
\sy   synonyms
\an   antonyms
\mr   morphemic representation
\cf   confer/cross-reference
\ce   cross-reference-English gloss
\cn   cross-reference-national gloss
\cr   cross-reference-regional gloss
\mn   main entry form
\va   variant forms
\ve   variant forms comment-English
\vn   variant forms comment-national
\vr   variant forms comment-regional
\bw   borrowed word
\et   etymology
\eg   etymology-gloss
\es   etymology-source
\ec   etymology-comment
\pd   paradigm set
\pdl  paradigm label
\pdv  paradigm vernacular form
\pde  paradigm form-English gloss
\pdn  paradigm form-national gloss
\pdr  paradigm form-regional gloss
\sg   singular noun form
\pl   plural noun form
\rd   reduplication forms
\tb   table
\sd   semantic domain
\is   index of semantics
\th   thesaurus
\bb   bibliographic reference
\pc   picture reference
\nt   notes
\np   notes on phonology
\ng   notes on grammar
\nd   notes on discourse
\na   notes on anthropology
\ns   notes on sociolinguistics
\nq   questions
\so   source of data      ← near end, after notes
\st   status
\dt   datestamp
```

**`\so` is valid and belongs near the end, after `\nt`.**

---

## Proposed Changes to `src/mdf/validator.py`

### Step 1 — Replace `REQUIRED_HIERARCHY` with the correct structural anchor tags

The full list above is too long to enforce positionally for every record. The validator should use a **structural anchor sequence** — the tags that define section boundaries and are most commonly present — drawn directly from the official order.

Replace:
```python
REQUIRED_HIERARCHY = ["lx", "so", "ps", "ge"]
```

With the MDF-standard structural anchors (standard hierarchy):
```python
REQUIRED_HIERARCHY = [
    "lx",   # lexical entry — always first
    "hm",   # homonym number
    "lc",   # lexical citation
    "ph",   # phonetic form
    "se",   # subentry (section boundary)
    "ps",   # part of speech (section boundary)
    "pn",   # part of speech-national
    "sn",   # sense number (section boundary)
    "ge",   # gloss-English
    "de",   # definition-English
    "rf",   # reference
    "xv",   # example-vernacular
    "xe",   # example-English
    "cf",   # cross-reference
    "sy",   # synonyms
    "an",   # antonyms
    "et",   # etymology
    "nt",   # notes
    "so",   # source of data (near end)
    "st",   # status
    "dt",   # datestamp
]
```

### Step 2 — Update the docstring

Update the class docstring to reflect the corrected hierarchy source:
```python
r"""
Validates MDF (Multi-Dictionary Form) data.
Hierarchy follows the official MDF recommended field order:
  \lx -> \ps -> \sn -> \ge -> ... -> \nt -> \so -> \dt
See: docs/mdf/original/MDFields19a_UTF8.txt (Order_of_Fields)
"""
```

### Step 3 — Update the missing-tags check

The "missing tags" global check currently flags all `REQUIRED_HIERARCHY` tags as missing. Since most are optional, restrict the missing-tags suggestion to only the **Basic (B)** tags that are truly expected in a standard entry:

```python
BASIC_TAGS = ["lx", "ps", "ge"]  # Minimum meaningful entry per MDF Basic set
```

Use `BASIC_TAGS` for the missing-tags diagnostic, not the full `REQUIRED_HIERARCHY`.

### Step 4 — Remove `\ln` from `LEGACY_TAG_MAPPING`

Currently `\ln` maps to `\so` as a "discouraged top-level language marker." This is **incorrect**. Per the official MDF docs (`Order_of_Fields`, line 1655), `\ln` is exclusively the **lexical function-national gloss** tag — a valid, standard MDF tag in its own right. It is not a language marker and must not be remapped to `\so`.

Remove this entry from `LEGACY_TAG_MAPPING`:
```python
"ln": "so",  # REMOVE — \ln is the MDF lexical-function-national-gloss tag, not a legacy language marker
```

---

## Checklist

- [ ] **Step 1**: Replace `REQUIRED_HIERARCHY` with MDF-standard structural anchors
- [ ] **Step 2**: Update class docstring
- [ ] **Step 3**: Introduce `BASIC_TAGS` and use it for missing-tags diagnostic
- [ ] **Step 4**: Remove `\ln` → `\so` from `LEGACY_TAG_MAPPING` — `\ln` is the MDF lexical-function-national-gloss tag
- [ ] **Tests**: Run existing validator tests; update or add tests to cover new hierarchy
- [ ] **Verify**: Confirm no false-positive "out of order" suggestions for `\so` after `\ge`

---

## Notes

- All diagnostics remain **advisory only** (NON-ENFORCEMENT POLICY).
- `\se` and `\sn` already reset the hierarchy in the second pass — this behavior is correct and must be preserved.
- The alternate hierarchy (`\sn → \se → \ps`) is already handled by the reset logic and does not require a separate code path.
- **`\so` multi-occurrence:** Per the MDF docs, `\so` is scoped to "the current entry" with no standard encoding and is `<Optional>`. It may validly appear multiple times — once per `\lx` bundle and once per `\se`/`\sn` sub-bundle. Because the hierarchy resets on `\se`/`\sn`, each sub-bundle evaluates `\so` independently. No special handling is needed; the reset logic already covers this correctly.
