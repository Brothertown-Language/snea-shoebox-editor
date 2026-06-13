# Issue #401 Comments

*Auto-synced from GitHub. Last sync: 2026-06-13*

---

## Comment 1 — Issue Created (2026-04-05)

**User Prompt:**

Create one or more new specs for adjustments needed for the records view left panel controls:

1. The sources filter drop-down needs to say "All Sources" instead of "All" - provides end-user clarity
2. The languages filter drop-down needs to say "All Languages" instead of "All" - provides end-user clarity
3. The "any | primary | secondary" language filter radio needs to have behavior adjusted
4. When searching via headword+va, the filters for "Languages" and "Primary vs Secondary" do not apply and needs to be disabled.

---
🤖 ✨ Created by OpenCode (ollama-cloud/glm-5): Issue #401

---

## Comment 2 — Added dependency on Spec #400 (2026-04-05)

**Context-Based Summary:**

Added dependency on Spec #400 (Headword and Gloss Search Modes). The filter behavior changes in this spec depend on the search mode architecture from #400. Key points:

1. **Dependency Order**: Spec #400 must be implemented first
2. **Search Mode Integration**: When #400 adds Headword and Gloss modes, this spec's filter logic must account for them:
   - Headword mode: PRIMARY \lx + PRIMARY \va — language filters SHOULD apply
   - Gloss mode: PRIMARY \ge — language filters SHOULD apply
   - FTS mode: all fields — language filters may be disabled
3. **Phase Interdependencies**: Phase 2 and Phase 3 explicitly depend on #400 being complete
4. **Testing Scope**: Phase 5 testing now includes Headword and Gloss modes

---
🤖 📝 Updated by OpenCode (ollama-cloud/glm-5): Added dependency on Spec #400

---

## Comment 3 — User investigation note (2026-04-05)

investigate before implementation to determine which search modes the language filter impacts and does not impact - these can only be done after #400 is completed

it needs to be determined if this UX change would disable actual functionality for search filtering
