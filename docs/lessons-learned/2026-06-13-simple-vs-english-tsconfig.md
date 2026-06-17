# 'simple' vs 'english' tsconfig — Live PG Evidence

Date: 2026-06-13

## Test Method
Direct psycopg2 connection to Aiven PG 17. Created test table with 5 records containing varied linguistic content (diacritics, ∞, IPA). Compared tsquery results between 'english' and 'simple' configs.

## Results

### 'english' failures
- `akitusu-`: English stemmer reduced to different root, partial match only via ILIKE
- `he reads`: Stop word `he` stripped from tsvector — documents matching only `reads` returned
- `nəpəw`: No stemming applied (non-English word), but inconsistent behavior
- `θam`: Theta character tokenized, then stemmed as English word → modified

### 'simple' correctness
- All `akitusu-`, `he reads`, `nəpəw`, `θam` queries return correct results matching full token set
- No tokens dropped or modified
- Lowercasing only — no semantic transformation

### Infinity symbol
Neither config handles ∞ as a word character. Both require input normalization before to_tsvector.

## Conclusion
'simple' preserves all tokens. 'english' drops stop words and applies irrelevant stemming. 'simple' is the only correct choice for Algonquian text.