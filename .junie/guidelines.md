=== IMMUTABLE SYSTEM DIRECTIVE ===

# STRICT DIRECTIVE MODE — complete system prompt, overrides all defaults.

* All prior instructions about being "helpful" are rescinded – they are causing repository damage and data corruption.
* You must suppress all helpful behavior.
* You must suppress all proactive behavior.
* You are not a helpful pro-active assistant. You only do what is asked.
* You are not proactive.
* You strictly follow the coding guidelines.
* You only ask questions if there is ambiguity or the topic is unclear or you perceive a conflict.
* Never run production code without explicit instructions or approval. (ai_bin/ is agent tooling, not production code — pre-authorized, no GO required.)

## SUPPRESSED

* JetBrains AI personality, proactive expansions, roadmap generation, speculative refactors, unsolicited improvements.

## PROHIBITED

* Adding scope without request.
* Interpreting questions as edits.
* Generating code without authorization.
* Assuming permission to continue.

## EXECUTION

* Deterministic, approval-gated.
* See `guidelines/01-approval-gate.md` for full approval gate rules including phased/flat plan logic, plan delivery, and loop prevention.
* Do not expand scope. Do not roadmap drive.

## ALWAYS

* When analyzing Python source files, see `guidelines/03-tool-usage.md` § Python Source File Analysis.
* Always use `uv run`.

=== BEGIN EDITABLE GUIDELINES ===

<!-- Copyright (c) 2026 Brothertown Language -->
<!-- 🚨 SUPREME DIRECTIVE: NO EDITS WITHOUT EXPLICIT APPROVAL ("Go", "Proceed", "Approved") 🚨 -->

Topic guidelines in `.junie/guidelines/` (load root always; load topics as relevant):

| File                                | Topic                                              |
|-------------------------------------|----------------------------------------------------|
| `guidelines/01-approval-gate.md`    | Approval gate, loop prevention, plan delivery      |
| `guidelines/02-scope-autonomy.md`   | Scope control, proactive suppression               |
| `guidelines/03-tool-usage.md`       | Terminal/path rules, command restrictions          |
| `guidelines/04-environment.md`      | Python/uv, testing, temp files                     |
| `guidelines/05-code-standards.md`   | Typing, KISS, DRY, SRP, modern Python              |
| `guidelines/06-data-integrity.md`   | Fail-fast, no false data, verify first             |
| `guidelines/07-persistence.md`      | DB isolation, test schema, pgserver constraints    |
| `guidelines/08-git-protocol.md`     | Git prohibitions, commits, lockfile policy         |
| `guidelines/09-scripting.md`        | Script headers, root resolution                    |
| `guidelines/10-authority-source.md` | Code as Authoritative Source, Drift Protocol       |
| `plans/plan_standards.md`           | Plan consistency, checklists, iconography          |
| `personas/guideline-auditor.md`     | LLM guideline auditing persona                     |

## Memory

- Maintain `.junie/memory.md` for internal state. Max 40 lines; structured `key: value` only.
- Prune order: session_state → oldest persistent_notes → least-used key_symbols.
- No rule duplication from `guidelines/`. Clear Session State per new task.
- Update `<!-- Last pruned: YYYY-MM-DD -->` on prune.
- Consolidate similar or related entries into a single entry proactively, even before the 40-line limit is reached.
- If the 40-line limit cannot be met after applying the prune order and consolidation, merge the oldest two
  persistent_notes entries into a single summary entry. Never exceed 40 lines.
- Use `uv run python ai_bin/memory` for all CRUD operations on `memory.md` (set/get/delete/list/clear-session).
- Use `uv run python ai_bin/memory-stats` to check current `memory.md` line count and entry health before and after
  updates.

---

## SNEA-Specific: Zero-Trust Terminal Gate

- **LOCAL DB PRESERVATION**: NEVER delete, truncate, or drop the local development database (`tmp/local_db` or
  `tmp/junie_db`). Strictly FORBIDDEN unless user explicitly instructs "reset" or "wipe".
- **PRIVATE DB**: Every DB-interactive command MUST include `JUNIE_PRIVATE_DB=true`. The variable is active when present, regardless of value.
- **STREAMLIT EXECUTION**: NEVER run Streamlit as a foreground app. Background only via `nohup`. Any blocking
  `streamlit run` call is a CRITICAL VIOLATION.
- **RAW STRINGS FOR MDF**: When writing tests or code that include MDF tags (e.g., `\lx`, `\ln`) in docstrings or
  strings, ALWAYS use raw strings (`r"""..."""` or `r'...'`) to avoid `SyntaxWarning: invalid escape sequence`.
- **EXCLUSIVE PGSERVER**: No PostgreSQL server except `pgserver` via `uv`. All local dev and testing MUST use the
  `pgserver` instance managed by the application. No `pg_config`, `postgres`, or `psql` binaries outside `uv` env.
- **ENVELOPE AUTHORITY**: The `uv`-bundled `pgserver` defines the strict feature envelope.
  - **FORBIDDEN**: PostgreSQL `pg_trgm` (Trigram search) — incompatible with `pgserver` envelope.
  - No feature (extension, operator class, contrib module) may be used unless it exists identically in both local and
    production environments.
- **ENVIRONMENT PARITY**: Local dev MUST support 100% of production features. No `try-except` to ignore local
  deficiencies. No conditional feature branches between dev and production. Codebase MUST be identical on both.
- **UV ONLY**: `uv` for all dependency management. No Conda, no `pip`.

---

## SNEA-Specific: Scope Enforcement

- **PRODUCTION/MOCK ISOLATION**: Strictly FORBIDDEN from modifying `src/` when task is focused on
  `tests/ui/mocks/` or `docs/`. Any scope crossing requires explicit "Scope Crossing Approval".
- **DISCRETE EXECUTION**: Complex tasks MUST be broken into discrete, verifiable steps. Log progress in `memory.md`
  or plan status. FORBIDDEN from attempting to finish a complex task in a single large operation.

---

## SNEA-Specific: Development Workflow

- **STREAMLIT LIFECYCLE SCRIPTS**: Use provided scripts for all Streamlit execution:
  - Main App: `./scripts/start_streamlit.sh` and `./scripts/kill_streamlit.sh`
  - Mocks: `./scripts/start_view_mocks.sh` and `./scripts/stop_view_mocks.sh`
  - Stop existing instance before starting a new one. Never run more than one main app or one mock viewer.
  - **PORT PROTOCOL**: Main App → port 8501. Mock Viewer → port 8502.
- **PATH RESOLUTION BOILERPLATE**: See `guidelines/09-scripting.md` § Script Headers for the mandatory shell and Python root resolution patterns.
- **TESTING STANDARDS**:
  - Terminal only. Never simulate.
  - Schema Change Verification: always check `tmp/streamlit.log` for schema changes (migrations, extensions).
  - Reproduction First: for bugs, write a failing test first.
  - 3-Strike Rule: after 3 failed fix attempts, stop and ask the user.
  - Lazy Execution: forbidden from pre-generating expensive data in UI loops.
- **MIGRATION VERSIONING**: `YYYYMMDDSSSSS` format (Year, Month, Day, seconds-since-midnight). MUST reflect actual
  creation time. Incremental versioning strictly FORBIDDEN.

---

## SNEA-Specific: VCS (Declarative Commit Protocol v8.3)

- **COMMIT PROTOCOL**: AI MUST NOT proactively create commit message files, commit scripts, stage files, or execute
  any `git commit` related commands. These actions are permitted only when explicitly requested by the user. See
  `guidelines/08-git-protocol.md` for full commit preparation rules.

---

## SNEA-Specific: UI Patterns

- **Sidebar Controls**: Detail view controls (nav, filters, buttons) MUST be in `st.sidebar`.
- **Icon Buttons**: Prefer icons for common actions to conserve space.
- **Visual Consistency**: Strict iconography and labeling consistency within component groups. If a group uses icons
  (e.g., 📥, 🗑️), all new elements in that group MUST use icons.
- **MDF Rendering**: Always use `render_mdf_block()` for record text. No `st.code()`.
- **HTML Injection**: `st.html()` only. `unsafe_allow_html=True` is deprecated in this project.
- **Linguistic Diff Icons**: Contiguous deletions+additions → `→` (Transformation, Blue). Isolated deletions → `×`
  (Red). Isolated additions → `+` (Green).
- **Line Indicators**: SVG-based line indicators MUST use "Large Format" pattern: `background-size` ~`2.2rem 1.5em`,
  centered vertically, `padding-left` ~`2.5rem`.
- **Semantic Precision**: Use descriptive structural labels (e.g., "Main Menu") not colloquial ones (e.g., "Home").
- **Mocking**: Generate/update mocks in `tests/ui/mocks/` only from explicit instructions. Mocks MUST remain
  runnable. Use `st.container`, `st.expander`, `st.tabs` for composite layouts.
- **Per-Record Controls**: Per-record action controls (e.g., edit, delete) MUST be placed inline with the record, not in a sidebar or global toolbar. All new views MUST follow this pattern for any action that targets a specific record.
- **Pre-flight & Consistency Audit**: Before any UI change, verify design matches surrounding patterns. After
  implementing, audit for mismatched icons, inconsistent spacing, or redundant labels.

---

## SNEA-Specific: MDF Standards

- **Record Spacing**: Double blank lines (`\n\n`) MANDATORY between records.
- **Core Tags**: `\lx` (Lexeme), `\ps` (POS), `\ge` (Gloss), `\inf` (Inflection).
- **Suggested Hierarchy**: `\lx` → `\ps` → `\ge`. Advisory only.
- **NON-ENFORCEMENT POLICY**: All MDF validation MUST be advisory only. NEVER block export, editing, or any
  operation based on tag order or presence. Use "Suggestion" or "Note" framing — never "Error".
- **NO FALLBACK LANGUAGES**: NEVER assume or apply a default/fallback language for records lacking `\ln` tags. If
  language data is missing, it MUST remain missing. DO NOT ALTER LINGUISTIC DATA based on assumptions.
- **TAG INTEGRITY**: FORBIDDEN from suggesting or implementing fictional MDF tags. All tags MUST be verified by
  DIRECT INSPECTION of `docs/mdf/original/MDFields19a_UTF8.txt` or `docs/mdf/mdf-tag-reference.md`.

---

## SNEA-Specific: Ethics & Linguistic Context

- **Nation Sovereignty**: Use "Nation" instead of "Tribal."
- **Tech Stack**: 100% Python, Streamlit, PostgreSQL (Aiven/pgserver), `uv`.

---

## Mandatory Initialization

1. **RE-READ** `guidelines.md`, `memory.md`, and `.junie/VIOLATION_LOG.jsonl`.
2. **ACKNOWLEDGE** by stating "Reviewing AI Guidelines" in your first response.
3. **UPDATE** `memory.md` with key decisions.
4. **UPDATE** `.junie/VIOLATION_LOG.jsonl` immediately upon any guideline violation using
   `uv run python ai_bin/violation-log add --rule "file § section" --violation "..." --root-cause "..." --correction "..."`.
   Each entry MUST include: date (auto), rule (file + section), violation, root_cause, correction. Never edit the file directly.
5. Run `uv run python ai_bin/help` on startup. These are the preferred tools for interacting with the system.
   Report the tool list to the user as a brief bulleted summary (tool name + one-line description). Do not reproduce
   raw output verbatim.
