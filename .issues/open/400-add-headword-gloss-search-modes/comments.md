---
issue: 400
type: comments
remote_issue: 400
---

## 2026-04-05 — Spec Created

This specification replaces #23 (closed for structural problems).

Key improvements over #23:
- Phases separated by concern boundaries
- Each phase has explicit risk level and blast radius
- Concrete implementation details
- MDF state tracking algorithm
- Interdependency ordering

🤖 OpenCode (ollama-cloud/glm-5) 📝

---

## 2026-04-24 — TDD Compliance Revision (v1.2)

STATUS updated to 1.2 (REVISED - NEEDS APPROVAL).

Changes:
1. Per-phase TDD RED/GREEN cycle tables added to all 6 phases
2. Success Criteria numbered SC-1 through SC-14
3. Phase 1 TDD Gap acknowledged (GREEN-without-RED violation)
4. Phase step order reversed for Phases 2-6 (RED before GREEN)
5. New integration test file specified for Phase 6

🤖 OpenCode (ollama-cloud/glm-5) 📝

---

## 2026-05-09 — Adversarial Spec Audit Round 1

FAIL (7/10). SC-2, SC-9, SC-10 failed.

🤖 OpenCode (ollama-cloud/glm-5.1) 🔍 spec-audit

---

## 2026-05-09 — Adversarial Spec Audit Round 2

FAIL (8/10). SC-4 (process_record wrong function), SC-9 improved.

🤖 OpenCode (ollama-cloud/glm-5.1) 🔍 spec-audit

---

## 2026-05-09 — Resolution v1.3

Changed Phase 1 markers from "☑ Retrospective" to "☐ TODO". Added Status column to Success Criteria.

🤖 OpenCode (ollama-cloud/glm-5.1) 📝 spec-audit resolution

---

## 2026-05-09 — Adversarial Spec Audit Round 2 (kimi-k2 + qwen3.5)

FAIL (8/10). SC-4: process_record() → populate_search_entries(). SC-9: Phase 1 GREEN-without-RED acknowledged.

🤖 OpenCode (ollama-cloud/glm-5.1) 🔍 spec-audit

---

## 2026-05-09 — Adversarial Spec Audit Round 4 (Final)

PASS (10/10). All criteria met. Spec v1.4 ready for approval.

🤖 OpenCode (ollama-cloud/glm-5.1) 🔍 spec-audit ✅

---

## 2026-05-10 — Spec-to-Codebase Audit (v1.5)

Step 1.4: `ai_bin/schema-version` → `./.opencode/tools/schema-version` (PEP 723 self-executing script)
Step 1.8: `_CURRENT_SCHEMA_VERSION` → `_MIGRATIONS` registry + `SchemaVersion` DB table
Step 1.9: Rollback is test-only (inline DROP + recreate, no production rollback migration)

🤖 OpenCode (ollama-cloud/glm-5.1) 📝 spec-audit

---

## 2026-05-11 — Phase 1 Retroactive Tests (branch: feature/400-phase1-retroactive-tests)

Test classes implemented:
- TestHeadwordSearchEntrySchema (5 tests): table exists, columns, indexes, FK, ORM roundtrip
- TestGlossSearchEntrySchema (5 tests): table exists, columns (no entry_type), indexes, FK, ORM roundtrip
- TestSearchEntryRollback (1 test): DROP + recreate idempotent, SearchEntry count preserved

All 18 tests pass idempotently.

🤖 OpenCode (ollama-cloud/glm-5.1) 📝