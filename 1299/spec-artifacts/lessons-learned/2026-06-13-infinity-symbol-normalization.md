# Infinity Symbol Normalization — ∞ in Algonquian Text

Date: 2026-06-13

## Context
∞ (U+221E) appears across Mohegan-Pequot, Narragansett, and Wampanoag records. It is a letter representing a long rounded vowel, not a mathematical symbol.

## Findings

### Production usage
Confirmed in lx, va, cf, se, ge fields. Examples: `*|achm∞wonk|`, `hogk∞`, `|n∞wantam∞̌e|` (combined with caron).

### PostgreSQL tokenization
`pg_catalog.default` parser classifies ∞ as Symbol-math → non-word character → word boundary. Both 'english' and 'simple' tokenize `achm∞wonk` as `{achm, wonk}`.

Using ∞ in tsquery without normalization produces syntax error: `achm:* & ∞:* & wonk:*` — `∞:*` is invalid.

### Normalization strategy
Map ∞ to `oozzz` in BOTH tsvector index and tsquery:
- `generate_sort_lx()` at linguistic_service.py:105 handles this: line 152-155
- `oozzz` sorts after all `oo*` entries and before `op*` in Unicode collation
- Both sides MUST use identical normalization or match fails

## Recommendation
Always normalize through `generate_sort_lx()` before to_tsvector() and before tsquery. Never reimplement the ∞→oozzz mapping — the canonical source is generate_sort_lx() line 152-155.