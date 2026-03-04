# Plan: Fix FTS tsquery Syntax Error from Pipe Character

## Status: DONE

## Problem

**Error:** `psycopg2.errors.SyntaxError: syntax error in tsquery: "|oo:*"`

When a user searches with a leading pipe (e.g. `|oo`), the word `|oo` is passed
directly into `to_tsquery('english', :fts_term)` as `|oo:*`, which is invalid tsquery
syntax. PostgreSQL tsquery operators (`|`, `&`, `!`, `(`, `)`) are not valid inside
lexeme tokens.

## Root Cause

In `src/services/linguistic_service.py`, at three identical sites (lines ~388, ~490, ~570):

```python
words = [w.strip() for w in search_term.split() if w.strip()]
fts_query = " & ".join([f"{w}:*" for w in words])
```

No sanitization of tsquery-unsafe characters within each word token.

## Fix

At all three sites, after splitting words, strip tsquery operator characters
(`|`, `&`, `!`, `(`, `)`, `:`) from each word, then skip words that become empty:

```python
_TSQUERY_UNSAFE = re.compile(r'[|&!():]+')
words = [
    clean for w in search_term.split()
    if (clean := _TSQUERY_UNSAFE.sub('', w).strip())
]
```

`re` is already imported at the top of the file.

## Checklist

- [x] Apply sanitization at line ~388 (get_records)
- [x] Apply sanitization at line ~490 (get_all_records_for_export)
- [x] Apply sanitization at line ~570 (stream_records_to_temp_file)
- [x] Verify existing tests pass (pre-existing unrelated failure in test_crud.py confirmed)
