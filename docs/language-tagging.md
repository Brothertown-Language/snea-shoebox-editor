Reviewing AI Guidelines.

### Mandatory Language Standard: ISO 639-3
All language markers (tags, dialect names, or codes) used in the Nation's reconstruction MUST EXPLICITLY BE LISTED in the project's master ISO list (`docs/iso-639-3.tab`). NO EXCEPTIONS.

Before applying any language tag, verify the code and reference name in that file.

| Language / Dialect | ISO 639-3 Code | Ref Name in .tab |
| :--- | :--- | :--- |
| Wampanoag | `wam` | Wampanoag |
| Mohegan-Pequot | `xpq` | Mohegan-Pequot |

Note: Use `xpq` for Mohegan-Pequot, per the official ISO 639-3 listing in `docs/iso-639-3.tab`. All language and dialect identifiers used in this project MUST exist in that file.

---

Based on a direct inspection of the **official MDF source documentation** (`MDFields19a_UTF8.txt`), the `\ln` tag is officially defined as **lexical function (national gloss)** (line 1217) and is NOT intended for "Language Name" or general dialect marking.

The documentation explicitly states: **"There are no specifically 'dialect' markers. Various alternative approaches can be used"** (line 1042).

### Recommended Official Strategy for Mohegan/Dialect Marking
To address the misuse of `\ln` and establish a dedicated, official-compliant way to identify non-Wampanoag SNEA dialects at all levels, I propose the following strategy derived directly from the MDF standard:

#### 1. Record Level: Use `\so` (Source of Data)
The `\so` field is officially for indicating the origin of the data. For records that are primarily Mohegan-Pequot, use this at the record level. Per MDF recommended order, it should follow the gloss (`\ge`) and example (`\xv`/`\xe`) bundles.

Mandatory: Use a single `\so` tag per record or subentry to identify the primary bibliographic source and language/dialect.

```mdf
\lx ahupanun
\ge come here
\so Mohegan-Pequot [xpq]; Prince-Speck 1904
```

#### 2. Variant Level: Use `\va` + `\ve` (Variant Form + English Comment)
MDF officially bundles `\va` with `\ve` to "specify the dialect name or area that uses the variant form" (line 3090). This is the official, required way to link a dialect name to a specific form within a record or subentry.
```mdf
\lx [Wampanoag Form]
\ge [Gloss]
\va ahupanun
\ve Mohegan-Pequot [xpq]
```

#### 3. Subentry Level: Use `\se` + `\va` + `\ve`
If a Mohegan form is a compound or derived subentry, you can still use the variant bundle inside the `\se` block.
```mdf
\lx [Root]
\se [Subentry Form]
\va [Mohegan Variant]
\ve Mohegan-Pequot [xpq]
```

#### 4. Contextual Information: Use `\ns` (Notes on Sociolinguistics)
For broader dialect information (e.g., "this form is used in the Mohegan village of..."), use `\ns` as officially recommended (line 297). This field is for narrative context and does not replace the mandatory `\so`/`\va`+`\ve` usage.

### Example: Mohegan Records Corrected
Applying the official standard to your examples:

```mdf
\lx ahupanun
\ge come here
\so Mohegan-Pequot [xpq]; Prince-Speck 1904

\lx appece
\ge apple
\so Mohegan-Pequot [xpq]; Prince-Speck 1904
```

Project Policy (Mandatory): Use `\so` at the record/subentry level and `\va`+`\ve` at the variant level to encode dialect information. Do not use `\ln` for language or dialect marking; in MDF, `\ln` is reserved for lexical function (national gloss). All languages and dialects referenced must exist in `docs/iso-639-3.tab`. No project-specific dialect tag (e.g., `\dia`) is defined or permitted.
