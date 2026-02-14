# MDF Tag Mappings

This document outlines the mappings between legacy MDF tags found in older Brothertown Language linguistic data (e.g., Trumbull Natick Dictionary) and their modern Multi-Dictionary Form (MDF) equivalents used in the SNEA Shoebox Editor.

## Legacy to Modern Mapping

| Legacy Tag | Modern Tag | Description |
| :--- | :--- | :--- |
| `\lmm` | `\lx` | Lexeme / Main Member → Lexeme |
| `\ctg` | `\ps` | Category → Part of Speech |
| `\gls` | `\ge` | Gloss → English Gloss |
| `\src` | `\rf` | Source → Reference |
| `\etm` | `\et` | Etymology → Etymology |
| `\rmk` | `\nt` | Remark → General Note |
| `\cmt` | `\nt` | Comment → General Note |
| `\twn` | `\cf` | Twin → Cross-reference |
| `\drv` | `\dr` | Derivative → Derivative |

## Validation Behavior

The SNEA Shoebox Editor's MDF Validator (`src/mdf/validator.py`) will automatically detect these legacy tags and provide a **Suggestion** to update them to their modern forms. 

- **Status**: `suggestion` (Non-blocking)
- **Tooltip**: "Legacy tag `\legacy` detected. Consider updating to the modern MDF form `\modern`."

## Leading Whitespace

In addition to tag mapping, the editor is configured to recognize MDF tags even when they are preceded by leading whitespace (spaces or tabs), as is common in legacy structured text files.
