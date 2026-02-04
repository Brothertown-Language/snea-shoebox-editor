<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->
# MDF Tag Reference Guide

This document provides a human-readable reference for the Multi-Dictionary Formatter (MDF) tags used in the Brothertown
Language project. MDF is a standard for structuring lexical data in software like ShoeBox and ToolBox.

**HTML Version:** An auto-generated HTML version of this guide is available at
`documentation/mdf-tag-reference.html`. To update it, run `uv run python scripts/shared/sync_mdf_docs.py`.

**Source of Truth:** This guide is based on the original MDF documentation found at
`documentation/MDFields19a_UTF8.txt`.

---

### Core Hierarchy

MDF entries are structured hierarchically. The order of tags determines how they are bundled together. In this project, every entry MUST include `\lg` (Language) and `\so` (Source) markers.

#### Standard Hierarchy

`\lx` (Lexeme) > `\lg` (Language) > `\so` (Source) > `\ps` (Part of Speech) > `\sn` (Sense) > `\se` (Subentry)

#### Alternate Hierarchy (Sense-Oriented)

`\lx` (Lexeme) > `\lg` (Language) > `\so` (Source) > `\sn` (Sense) > `\se` (Subentry) > `\ps` (Part of Speech)

---

### Tag Reference

#### Primary Entry Markers

- `\lx`: **Lexeme**. The headword for the entry.
- `\hm`: **Homonym Number**. Used when multiple entries have the same headword.
- `\se`: **Subentry**. A related form, compound, or phrase belonging to the main entry.
- `\ps`: **Part of Speech**. The grammatical category (typically in English).
- `\pn`: **Part of Speech (National)**. The POS in the national language.
- `\sn`: **Sense Number**. Used to distinguish multiple meanings of a single lexeme.

#### Glosses and Definitions

- `\ge`: **Gloss (English)**. A brief one- or two-word equivalent.
- `\gn`: **Gloss (National)**. Brief equivalent in the national language.
- `\de`: **Definition (English)**. A full sentence or phrase explaining the meaning.
- `\dn`: **Definition (National)**. Full definition in the national language.
- `\lt`: **Literal Meaning**. Used for idioms or complex terms.

#### Examples and Translations

- `\xv`: **Example (Vernacular)**. A sentence in the target language.
- `\xe`: **Example (English Translation)**. Translation of the example sentence.
- `\xn`: **Example (National Translation)**. Translation in the national language.

#### Cross-References

- `\cf`: **Confer (Cross-reference)**. Links to another related entry.
- `\ce`: **Cross-reference Gloss (English)**. Brief gloss for the cross-referenced item.
- `\sy`: **Synonym**. Links to a word with the same meaning.
- `\an`: **Antonym**. Links to a word with the opposite meaning.
- `\va`: **Variant Form**. Links to another form of the same word.

#### Etymology and Morphology

- `\et`: **Etymology**. The source or history of the word.
- `\eg`: **Etymology Gloss**. The meaning of the etymological root.
- `\es`: **Etymology Source**. The language or dictionary providing the etymology.
- `\mr`: **Morphemic Representation**. The breakdown of the word into morphemes.
- `\ph`: **Phonetic/Phonemic Form**. The pronunciation of the word.

#### Notes and Usage

- `\nt`: **General Note**. Any additional information.
- `\ng`: **Grammar Note**. Specific details about grammatical behavior.
- `\ue`: **Usage (English)**. Notes on when or how the word is used.

#### Source and Language Markers

- `\so`: **Source**. The original source of the data (e.g., Trumbull pg3).
- `\lg`: **Language Name**. The name of the language or dialect for this entry (e.g., `Wampanoag [wam]`).
- `\ln`: **Language (National)**. The name of the language in the national language.

---

### Dialect and Multi-lingual Data

In projects involving multiple languages or dialects (like the Brothertown project's use of Natick, Mohegan, and Narragansett data), the following conventions are used:

1. **The `\lg` Tag**: Use the `\lg` tag to explicitly identify the language or dialect of a record. For consistency, use the language name followed by its ISO 639-3 code in brackets.
   - Example: `\lg Narragansett [xnt]`
2. **Language Abbreviations**: When citing comparative data from other languages within a note or definition, use standard abbreviations (e.g., `Abn.` for Abenaki, `Del.` for Delaware). Refer to the project guidelines for a full list of abbreviations.
3. **Asterisk (*) Prefix**: In some source materials (like Trumbull's Natick dictionary), an asterisk `*` before a headword indicates it belongs to a related dialect (e.g., Wampanoag) rather than the primary dialect. These should be tagged with the appropriate `\lg` marker during processing.
4. **Loanwords**: Use `\et` (Etymology) and `\eg` (Etymology Gloss) to document loanwords and their sources.

---

### Formatting Rules

1. **One Tag Per Line**: Every MDF marker must start on its own line.
2. **Backslash Prefix**: All markers begin with a backslash (`\`).
3. **Indentation**: Standard MDF tools use indentation to reflect hierarchy in the source file, though the tags
   themselves are the primary structural indicators.
4. **Field Bundling**: certain tags are meant to be grouped. For example, a `\cf` should be followed by its optional
   glosses (`\ce`), and an `\xv` should be followed by its translations (`\xe`).

---

**References:**

- Detailed SPR-compressed reference: `.junie/mdf-guidelines-spr.md`
- Original Source Documentation: `documentation/MDFields19a_UTF8.txt`
