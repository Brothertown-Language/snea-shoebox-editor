# Plan: Synchronize Default Sources to Match Production

## Status: ✅ Complete

## Problem
The `_seed_default_sources()` method in `src/database/migrations.py` seeds only 2 sources
with incorrect `name` values and verbose `description` fields that do not match production.

### Current seed (local):
| name | short_name | description |
|---|---|---|
| Trumbull/Natick | Trumbull (1903) | Comprehensive lexicon... (long text) |
| Fielding/Mohegan | Fielding (2013) | Modern reconstruction... (long text) |

### Production DB (authoritative):
| id | name | short_name | description |
|---|---|---|---|
| 1 | Trumbull 1903 | Trumbull (1903) | Wampanoag [wam] |
| 2 | Fielding 2012 | Fielding (2013) | Mohegan-Pequot [xpq] |
| 4 | Anonymous 1647 | (null) | Wampanoag [wam] |
| 5 | Winslow 1624 | (null) | Wampanoag [wam] |
| 6 | Wood 1634 | (null) | Wampanoag [wam] |
| 7 | Prince-Speck 1904 | (null) | Mohegan-Pequot [xpq] |
| 42 | Williams 1643 | (null) | Narragansett [xnt] |

Note: `id=9` ("michael-conrad") is a user-created entry and MUST NOT be seeded.

## Steps

1. ⏳ Update `_seed_default_sources()` in `src/database/migrations.py` to replace the
   existing 2-entry list with all 7 scholarly sources matching production's `name`,
   `short_name`, and `description` values exactly. The `citation_format` for entries
   4–7 and 42 is `None` (null), matching production.
