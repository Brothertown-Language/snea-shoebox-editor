| SC ID | Success Criterion | Test | Result |
| -- | -- | -- | -- |
| SC5 | 5-failure baseline set at trunk tip eb467b8 green after fresh sync | `PYTHONPATH=. uv run pytest test/test_upload_search_entries.py -k "test_sc8"` + `... test/test_semantic_search_schema_sc3.py -k "test_gloss_search_entries_embedding_is_vector384 or test_semantic_search_entries_embedding_is_vector384"` + `PYTHONPATH=. uv run pytest test/test_semantic_search_schema_sc3.py test/test_upload_search_entries.py` (live DB) | PASS |
| SC6 | No failures and no new failures vs pre-fix suite (5 failed / 169 passed / 8 skipped) | `PYTHONPATH=. uv run pytest test/` (live DB) — 178 passed, 8 skipped, 0 failed | PASS |
| SC1 | records.embedding format_type == vector(1536) | `psql postgresql://postgres:@localhost:5432/postgres -Atc "SELECT format_type(atttypid, atttypmod) ..."` (live DB) | PASS |
| SC2 | gloss_search_entries.embedding format_type == vector(384) | same psql live query (live DB) | PASS |
| SC3 | semantic_search_entries.embedding format_type == vector(384) | same psql live query (live DB) | PASS |
| SC4 | All 16 enumerated .id columns carry nextval pg_attrdef defaults | psql pg_get_expr(pg_attrdef) join over 16-table VALUES list (live DB) | PASS |
