# Data Integrity

## Global Absolute Prohibition

- **NO SYNTHETIC / IMAGINARY / FABRICATED DATA — PERIOD, NO EXCEPTIONS**: Across all code, notebooks, reports, plans, analyses, validation vocabularies, examples used as evidence, and recommendations, only real, verifiable data from real sources is allowed. Synthetic, placeholder, invented, proxy, mock-as-real, or guessed data is globally forbidden with no carve-outs.

## Fail-Fast

- Raise contextual errors immediately; never swallow exceptions.
- **NO FALSE DATA**: Never use proxy/fallback/synthetic data (e.g., `date.today()` for missing historical metadata,
  cross-field assignments like `journal_pub_date = discovery_date`). If metadata is missing, ambiguous, or unexpected (
  `None`, `0`), fail immediately and ask user.
- **NO DEFAULT DATA**: Never assign defaults to fill missing DB fields.
- **NO INVALID DEFAULTS**: Never default parameters that drive deterministic logic (e.g., `processing_date`). Caller
  must provide explicitly.
- **HARD FAIL ON MISSING REQUIRED DATA**: If data required for analysis or downstream processing is missing from a
  source record (e.g., `discovery_date` absent from an XML record), the process MUST raise immediately — never skip,
  suppress, or continue. Missing required data is a data integrity defect, not a filter condition. All fields referenced by the current logic are **required** by default. Any field that is genuinely optional (i.e., its absence is expected and documented in the schema) must be explicitly handled by the logic; otherwise, its absence MUST trigger a hard fail. **The agent is prohibited from using a default placeholder (e.g., '—') to mask a missing field that it has not explicitly confirmed as optional.**
  
  absent without triggering a hard fail.

## Verify Before Recommend

- Never recommend backfills/schema changes based on assumptions. Verify presence and distribution of source data with a
  robust sample before proposing solutions.
- **NO SYNTHETIC/IMAGINARY ANALYSIS VOCABULARIES**: In notebooks, reports, or analysis pipelines, do not invent
  placeholder term sets (e.g., "optional seed" dictionaries). Use only verifiable terms from real authorities and
  document the source in the artifact. If no real source is available, leave the vocabulary empty and block/flag
  validation rather than fabricating terms.
- **MANDATORY SOURCE TRACEABILITY FOR VALIDATION DATA**: Any reference data used to validate user-supplied artifacts
  (e.g., MeSH dictionaries, code lists, taxonomies) must include a real source of record (official API, release file,
  or documented curated dataset) and version/date when available. Unverifiable inline constants are prohibited for
  pass/fail validation logic.
- **Robust Sampling Required**: When analyzing or remediating data formats, behavior, or patterns, you MUST compare
  across multiple samples (minimum 5-10 distinct records) from different categories/topics. Never assume a single
  example is representative of a set or format.
- **Exhaustive Automated Analysis**: When a large archived dataset is available (e.g., `pubmed_data_2`), you MUST
  generate and run an automated script to scan the ENTIRE archive for frequency analysis of headers, fields, and
  formatting patterns. Relying on manual sampling for large datasets is strictly prohibited. A dataset is considered
  **large** for this rule if it contains more than 1,000 records or files.
- **Evidence-Based Remediation**: All remediation plans MUST be based on findings verified through exhaustive
  automated analysis or robust multi-sample sets.
- **NO UNAUTHORIZED FORMAT CHANGES**: You are strictly prohibited from adding, removing, or altering data fields,
  headers, or formatting styles (e.g., Markdown structure) without explicit, documented authorization. Any deviation
  from the established "Ground Truth" (e.g., archived datasets like `pubmed_data_2`) is a data integrity violation.
  Authorization is established by an explicit user instruction in the current session (chat or approved plan). A GO on
  a plan that includes the format change constitutes documented authorization.
- **MANDATORY AUDIT LOGGING**: Any proposed change to a data format MUST be accompanied by an automated audit report
  proving fidelity to the source or historical archive. "Speculative" or "unannounced" format improvements are
  forbidden.

## No Unauthorized Semantic Changes

- **NEVER ALTER SEMANTIC MEANING WITHOUT EXPLICIT PERMISSION**: You are strictly prohibited from changing the semantic meaning of any artifact — including queries, logic, data transformations, prompts, configurations, code, data structures, or any other artifact — without explicit user permission. This applies to all translation, refactoring, reformulation, and implementation tasks.
- **NO EQUIVALENCE CLAIMS WITHOUT PROOF**: Claiming that a transformed or translated artifact is "equivalent" or "semantically identical" to the original is forbidden unless you can formally prove the equivalence. If you cannot prove equivalence, you must explicitly state the discrepancy.
- **STOP AND REPORT ON SEMANTIC LOSS**: If a task (e.g., translating a query to a different syntax, refactoring logic, reformulating a prompt) cannot be completed while preserving exact semantics, you MUST stop immediately and report the discrepancy to the user before proceeding. Never silently approximate.

## Production Data Protection
- **ABSOLUTE PROHIBITION**: Strictly follow the production data protection rules in `070-environment.md`. Never run code against production data or databases without explicit user instruction in the current session.
- **NO TESTS AGAINST PRODUCTION**: Tests must NEVER run against production or live data. Always use isolated test fixtures with dedicated test databases. Running tests against production data is prohibited regardless of whether the test is read-only, verification, or diagnostic.

## No Hardcoded Entity IDs
- Hardcoding domain-specific entity IDs (e.g., PMIDs, database record IDs, foreign keys) in source code or notebooks is **absolutely forbidden**.
- Such values are tightly coupled to a specific database snapshot and will silently break or produce incorrect results when the database is updated or rebuilt.
- All entity IDs used in logic must be derived dynamically at runtime (e.g., via query, ranking, or configuration) — never cherry-picked and embedded in code.
- Existing violations (e.g., `SEED_PM_IDS`) must be removed and replaced with dynamic derivation.
## Batch Operations

- For datasets exceeding 1,000 rows: use pagination (offset/keyset) for reads and batched commits for writes.
- **CORRECTNESS OVER PERFORMANCE**: Always prioritize correct operation over insertion speeds or other optimizations. A smaller batch size that works reliably is better than a larger batch size that fails.
- **POSTGRESQL PARAMETER LIMIT**: Batch operations using parameterized queries must stay under PostgreSQL's 65,535 parameter limit. With N columns per row, batch size must satisfy: `batch_size × N < 65535`. For 10-column inserts, maximum safe batch size is ~6,500 (use 5,000 for safety margin).
- **ESTABLISH WORKING BATCH SIZES FIRST**: Start with conservative batch sizes (500-1,000 rows). Only increase after verifying correctness at scale. Never assume large batch sizes work without testing.
- **VALIDATE BATCH CONTENTS**: Before upserting a batch, validate that data structures match schema expectations. Catch errors early rather than mid-transaction.

## Long-Running Tasks

- All batch/long-running tasks MUST use `tqdm`. Update progress per individual item (`pbar.update(1)`), not per batch.

## Cross-References

- **200-errors-exception-handling.md** — Zero-tolerance rules for exception handling
- **201-errors-missing-data.md** — Zero-tolerance rules for missing data

---

This guideline works with the error handling series (200-203). When in doubt: **raise, don't return.**
