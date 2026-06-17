# PostgreSQL Full-Text Search for Algonquian Content

Date: 2026-06-13

## Context

Evaluated against 7,609 production records (Mohegan-Pequot, Narragansett, Wampanoag, Quiripi) via direct psycopg2 connection to Aiven PG 17.

## Findings

### 'english' config is incorrect
- Stems Algonquian words via Snowball English stemmer — produces wrong lexemes
- Strips English stop words (a, an, he, the) even when they appear as valid Algonquian morphemes
- Tokenization boundaries identical to 'simple' (same pg_catalog.default parser)

### 'simple' config is correct
- No stemming — each word is its own lexeme
- No stop words — every token indexed
- Only lowercases and splits on default word boundaries
- Works on PG 16 (pgserver) and PG 17 (Aiven)

### Infinity symbol
Neither config treats ∞ (U+221E, Symbol-math) as a word character. Normalize input before to_tsvector.

## Recommendation
`to_tsvector('simple', normalize(text))` with normalize via generate_sort_lx().