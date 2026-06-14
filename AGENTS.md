# AGENTS.md — Repository Guidelines for Coding Agents

## Research Catalog

Before making changes to search infrastructure, text normalization, FTS configuration, or regex processing linguistic data, consult `docs/lessons-learned/` for relevant research findings and design decisions.

| File | Topic |
|------|-------|
| `docs/lessons-learned/index.md` | Entry catalog with cross-references |
| `docs/lessons-learned/2026-06-13-postgres-fts-algonquian.md` | Why 'english' tsconfig corrupts Algonquian search |
| `docs/lessons-learned/2026-06-13-regex-linguistic-characters.md` | ASCII-based regex destroys linguistic data |
| `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md` | ∞ is a valid letter, maps to oozzz |
| `docs/lessons-learned/2026-06-13-simple-vs-english-tsconfig.md` | Live PG verification evidence |
