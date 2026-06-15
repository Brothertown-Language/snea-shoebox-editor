# Regex Safety with Linguistic Characters

Date: 2026-06-13

## Context
This repo processes Algonquian text with diacritics (áéíóú âêîôû āēīōū), ∞ (U+221E, a letter), and IPA (ə θ ð ʃ ʒ ŋ ʔ ɾ). Any regex that strips characters must account for this full set.

## Findings

### ASCII-only char classes destroy data
`[a-zA-Z]` `[^a-zA-Z]` `[a-zA-Z0-9]` `[^a-zA-Z0-9]` strip non-ASCII, destroying all linguistic characters. Verified against production corpus.

### Python \w without re.ASCII is safe
`\w` matches Unicode letters, digits, underscore — covers all IPA base letters and diacritized chars. Use `[^\w]` for tsquery-safe filtering on normalized text.

### The canonical safe pattern: `[|&!()]+`
Strips only PostgreSQL tsquery operators. All linguistic chars pass through unchanged. No escape mechanism exists for tsquery grammar operators — they must be stripped.

### SQL injection
Parameterized queries (`:param`) are the only correct defense. Character filtering designed to prevent injection destroys linguistic data and provides no real security benefit over parameterized queries.

## Recommendations
1. Never use `[a-zA-Z]` or `[a-zA-Z0-9]` in any regex
2. Use `[|&!()]+` for tsquery sanitization (on normalized input)
3. Use `[^\w]+` for general non-word character removal on normalized text
4. Always test against corpus samples with diacritics, IPA, ∞