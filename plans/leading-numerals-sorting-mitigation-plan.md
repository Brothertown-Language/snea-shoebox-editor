# Mitigation Plan: Leading Numerals in Sorting

## Problem Statement
Leading numerals in record lexemes (`\lx`) are currently considered during sorting. For linguistic records, it is often desired to ignore these numerals so that entries are sorted by their alphabetical content (e.g., "1 record" should sort with "record", not at the beginning of the list).

## Proposed Solution

### 1. Update Normalization Logic
Modify `LinguisticService.generate_sort_lx` in `src/services/linguistic_service.py` to strip leading numerals.

**Current Regex:**
```python
re.sub(r'^[*\-=\[\]\(\)]+', '', lowered)
```

**Proposed Regex:**
```python
re.sub(r'^[0-9*\-=\[\]\(\)\s]+', '', lowered)
```
*Note: Also added `\s` to handle potential leading spaces after digits or punctuation.*

### 2. Database Migration
Since `sort_lx` (for `Record` model) and `normalized_term` (for `SearchEntry` model) are persisted in the database, a migration is required to re-normalize all existing records. This explicitly includes stripping numerals from `search_entries.normalized_term` to ensure search behavior matches the new sorting logic.

- Create a new migration script using the `YYYYMMDDSSSSS` format.
- The migration will:
    1. Iterate through all `Record` entries and update `sort_lx` using the updated `generate_sort_lx`.
    2. Iterate through all `SearchEntry` entries and update `normalized_term` using the updated `generate_sort_lx`.

### 3. Verification Plan
- **Unit Tests:** Add test cases to `tests/services/test_linguistic_normalization.py` to verify that `generate_sort_lx` correctly handles leading numerals and spaces.
    - Input: `"123 apple"`, Output: `"apple"`
    - Input: `"123 apple"`, Output: `"apple"` (applied to `Record.sort_lx` and `SearchEntry.normalized_term`)
    - Input: `"(1) banana"`, Output: `"banana"`
    - Input: `"* orange"`, Output: `"orange"`
    - Input: `"10 quttaúatues"`, Output: `"quttauatues"`
- **Integration Tests:** Verify that sorting in the UI (Records page) reflects the new logic after migration.
- **Search Verification:** Verify that searching for "apple" matches a record with `\lx 123 apple` via the updated `SearchEntry.normalized_term`.
- **Data Integrity:** Ensure that the migration handles a large number of records efficiently.

## Impact Analysis
- **Sorting:** Records will now be grouped by their linguistic content regardless of leading numbering. Entries like "10 quttaúatues" and "6 quttáuatues" will be sorted based on "quttauatues".
- **Search:** Prefix search on normalized terms will be more intuitive (e.g., searching "app" will find "1. apple"). Since `search_entries.normalized_term` will no longer have leading numerals, searching for the headword's letters will match even numbered entries.
- **Performance:** Minimal impact on runtime; one-time cost for migration.

## Constraints
- **Codebase Identity:** The same logic will be applied to both local and production environments.
- **No Feature Creep:** This change is strictly limited to ignoring leading numerals/punctuation for sorting.
