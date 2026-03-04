# Plan: Document ∞ → oozzz Sort Pattern

**Status: IMPLEMENTED**

## Scope
Documentation and pydoc/comment updates only. No logic changes.

## Files to Change

### 1. `src/services/linguistic_service.py` — `generate_sort_lx` docstring
Expand the docstring to document step 3b fully, including the `oozzz` rationale:

```
3b. Symbol substitution — treat linguistic symbols as letters:
    - ∞ (U+221E) is an Algonquian letter for a long rounded vowel.
      Mapped to "oozzz" so it sorts after "oo" and all "oo*" entries
      (ooa…ooy) and before any "op*" entries.
      "oozzz" is chosen because:
        • It sorts after oo and all ooa…ooy entries in ASCII/Unicode collation.
        • It sorts before op.
        • The extra zzz suffix eliminates collision risk with real ooz* lemmas.
    - ✔ (U+2714) is an annotation mark; stripped (→ "") for sort purposes.
```

### 2. `docs/ARCHITECTURE.md` — Add "Sorting & Normalization" section
Add a new section after "Data Model & Schema Management" documenting the sort key pipeline and the `∞ → oozzz` convention.

### 3. `.junie/memory.md` — Add symbol mapping key
Add: `sort_symbol_map: ∞(U+221E)→oozzz (Algonquian letter, after oo*/before op); ✔(U+2714)→"" (annotation, stripped)`

---

## Checklist
- [x] `generate_sort_lx` docstring updated
- [x] `docs/ARCHITECTURE.md` sorting section added
- [x] `memory.md` key added
