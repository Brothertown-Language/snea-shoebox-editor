# Data Integrity

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
  suppress, or continue. Missing required data is a data integrity defect, not a filter condition. A field is
  **required** for a given step if the step's logic cannot produce a valid output without it; optional fields may be
  absent without triggering a hard fail.

## Verify Before Recommend

- Never recommend backfills/schema changes based on assumptions. Verify presence and distribution of source data with a
  robust sample before proposing solutions.
- **Robust Sampling Required**: When analyzing or remediating data formats, behavior, or patterns, you MUST compare
  across multiple samples (minimum 5-10 distinct records) from different categories/topics. Never assume a single
  example is representative of a set or format.
- **Evidence-Based Remediation**: All remediation plans MUST be based on findings verified through exhaustive
  automated analysis or robust multi-sample sets.

## Batch Operations

- For datasets exceeding 1,000 rows: use pagination (offset/keyset) for reads and batched commits (max 1,000 rows per
  commit) for writes.

## Long-Running Tasks

- All batch/long-running tasks MUST use `tqdm`. Update progress per individual item (`pbar.update(1)`), not per batch.
