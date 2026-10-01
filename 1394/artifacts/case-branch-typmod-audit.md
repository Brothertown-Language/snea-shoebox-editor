# SC9 — Column-Type CASE Branch Typmod Audit (I-9, R-5)

**Issue:** .issues/1394
**Item:** I-9 / SC9 (structural)
**Audited file:** `scripts/sync_prod_to_local.py`, DDL-builder column-type CASE block (CASE at lines 123–135) plus post-CASE typmod handling (lines 160–164).
**Evidence type:** structural (code inspection + this recorded artifact)
**Source change:** none (audit item; `vector` typmod-applied fix already present in working tree — verified at line 163–164).

## CASE Branch Inventory

Post-CASE typmod handling exists for exactly two dtype strings: `character varying` (line 161–162) and `vector` (line 163–164). All other branches emit the bare dtype name with no typmod applied.

| # | Branch (t.typname) | Emitted dtype | Typmod handling | Justification |
|---|--------------------|---------------|-----------------|---------------|
| 1 | `vector` | `vector` | **typmod-applied** — post-CASE line: `vector({typmod})` when `typmod > -1` | pgvector typmod encodes dimensionality directly (no −4 offset); emitted correctly (post-fix). Matches spec classification: vector = typmod-applied. |
| 2 | `tsvector` | `tsvector` | typmod-free — bare type | `tsvector` accepts no user-facing typmod in column DDL; `atttypmod` is never meaningful. Bare emission is correct. |
| 3 | `bool` | `boolean` | typmod-free — bare type | `boolean` takes no typmod. Bare emission is correct. |
| 4 | `int4` | `integer` | typmod-free — bare type | `integer` takes no typmod. Bare emission is correct. |
| 5 | `int8` | `bigint` | typmod-free — bare type | `bigint` takes no typmod. Bare emission is correct. |
| 6 | `float8` | `double precision` | typmod-free — bare type | `double precision` takes no typmod. Bare emission is correct. |
| 7 | `numeric` | `numeric` | **typmod-free — see Finding F-1** | Bare emission drops precision/scale when production column is `numeric(p,s)`. |
| 8 | `varchar` | `character varying` | **typmod-applied** — post-CASE line: `character varying({typmod - 4})` when `typmod > -1` | PG stores varchar typmod as length + 4 header offset; the −4 correction is correct. Matches spec classification: character varying = typmod-applied. |
| 9 | `text` | `text` | typmod-free — bare type | `text` takes no typmod. Bare emission is correct. |
| 10 | `timestamptz` | `timestamp with time zone` | **typmod-free — see Finding F-2** | Bare emission drops precision when production column is `timestamptz(p)`. |
| 11 | ELSE (any other typname) | `t.typname` verbatim | **typmod-free — see Finding F-3** | Fallback emits bare typename; any typmod-bearing type falling through (e.g. `timestamp`, `char`, `interval`, `time`) loses its typmod. |

## Spec Classification Compliance

| Spec requirement | Status |
|------------------|--------|
| `character varying` = typmod-applied | ✅ PASS — line 161–162 applies `typmod - 4` |
| `vector` = typmod-applied (post-fix) | ✅ PASS — line 163–164 applies `typmod` |
| All other branches typmod-free or typmod-applied with correct handling | ✅ PASS with findings — branches 2–6, 9 are typmod-free and correct for their types; branches 7, 10, 11 are typmod-free but flagged as fidelity gaps (reported per R-5, not fixed in this scope) |

## R-5 Findings — Additional Fidelity Gaps (reported, NOT fixed in this scope)

### F-1 — `numeric` branch drops precision/scale

**Location:** CASE branch `WHEN t.typname = 'numeric' THEN 'numeric'` (line 130); no post-CASE typmod handling for `numeric`.
**Gap:** A production column declared `numeric(10,2)` carries `atttypmod` encoding precision and scale. The DDL builder emits bare `numeric`, so the local replica re-creates the column with default precision/scale semantics — a fidelity divergence from production.
**Proposed fix (out of scope):** add a post-CASE branch decoding numeric typmod: `numeric((typmod - 4) >> 16, (typmod - 4) & 0xffff)`.

### F-2 — `timestamptz` branch drops precision

**Location:** CASE branch line 133; no post-CASE typmod handling.
**Gap:** A production column declared `timestamptz(3)` carries typmod = precision + offset. Bare emission produces `timestamp with time zone` without precision. Note: in the synced production schema, columns are declared `timestamptz` without precision, so current impact is latent — but the branch is not typmod-safe in general.
**Proposed fix (out of scope):** apply typmod as `timestamp with time zone({typmod})` when `typmod > -1` (timestamptz typmod is precision + offset; offset handling must be verified against `pg_type` semantics before implementation).

### F-3 — ELSE fallback emits bare typename for typmod-bearing types

**Location:** `ELSE t.typname` (line 134) with no post-CASE typmod handling for fallback types.
**Gap:** Any typmod-bearing type not enumerated in the CASE (e.g. `timestamp(p)`, `char(n)`, `interval`, `time(p)`) falls through and loses its typmod in the emitted DDL. Currently latent for the production schema (no such column types observed in the synced tables), but the fallback is not typmod-safe in general.
**Proposed fix (out of scope):** generic typmod emission for the ELSE branch, or explicit CASE coverage for each typmod-bearing type in the production schema.

## Audit Verdict

SC9 GREEN: **PASS (structural)**. All 11 CASE branches inventoried; `character varying` and `vector` confirmed typmod-applied with correct typmod arithmetic; remaining branches typmod-free and correct for typmod-free types. Three latent typmod-fidelity gaps (F-1, F-2, F-3) reported as separate findings per R-5 — not fixed in this scope, per the spec's Change Control boundary.

---

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
