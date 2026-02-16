<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
---
author: Michael Conrad
contributor: Junie (gemini-3-flash-preview)
status: active
date: 2026-02-05
---
<!-- 
CRITICAL MAINTENANCE RULES:
1. This file must NEVER be altered except when expressly instructed to do so by the user.
2. If an edit appears necessary but has not been explicitly requested, the AI agent MUST stop and query the user with details.
3. An action plan for such edits must be developed, reviewed, and approved or rejected by the user before any changes are applied.
-->
<!-- Copyright (c) 2026 Brothertown Language -->

# SNEA Online Shoebox Editor - Database Specification

This document records the finalized database schema design and implementation strategy developed through collaborative review between Michael Conrad and Junie (gemini-3-flash-preview).

---

## 1. Record Identity & Synchronization (\nt Record: ID)

To maintain a persistent link between the PostgreSQL database and the raw MDF data (the project's linguistic source of truth) without using custom tags, we utilize the standard `\nt` (Note) tag.

### Strategy & Logic
- **Format**: `\nt Record: <id>`
- **Single Source of Truth**: Exactly one correct tag must exist per entry.
- **Auto-Correction Logic**:
    - **On Download/Export**: The system scans the MDF text. It adds a missing tag, overwrites an incorrect ID, or consolidates multiple tags into a single line matching the database `id`.
    - **On Upload/Sync**: The parser extracts this ID to perform a direct primary key lookup, ensuring edits are applied to the correct existing records rather than creating duplicates.
    - **Workflow Benefit**: This approach enables a flexible "Round-Trip" workflow. A linguist can download MDF data from the database, edit it locally in their editor of choice (e.g., ShoeBox, ToolBox, or a plain text editor), and upload it back. The system will recognize the `\nt Record: <id>` tags and accurately apply the changes to the correct existing records in the PostgreSQL database.

---

## 2. Optimized Table Schema

The schema is organized for human readability in SQL viewers like **DBeaver**, prioritizing core linguistic data on the left and pushing large data blobs or metadata to the right.

### Core Tables

#### `records`

| Column | Type | Description | Justification |
| :--- | :--- | :--- | :--- |
| **`id`** | SERIAL | Primary Key | Matches the `\nt Record: <id>` tag. |
| **`lx`** | TEXT | Lexeme (Headword) | Primary linguistic identifier. |
| **`hm`** | INTEGER | Homonym Number | Distinguishes entries with identical headwords. |
| **`ps`** | TEXT | Part of Speech | Grammatical classification. |
| **`ge`** | TEXT | English Gloss | Primary definition for searching/sorting. |
| **`source_id`** | INTEGER | FK to `sources.id` | Identifies the origin collection. |
| **`source_page`** | TEXT | Source Citation | Specific page or section number. |
| **`status`** | TEXT | Workflow State | 'draft', 'edited', 'approved'. |
| **`embedding`** | VECTOR(1536) | Semantic Vector | Used for cross-reference lookup (not general search). |
| **`mdf_data`** | TEXT | Raw MDF Body | The full, unparsed linguistic entry. |
| **`current_version`** | INTEGER | Version Number | Optimistic locking and revision tracking. |
| **`is_deleted`** | BOOLEAN | Soft Delete Flag | Allows restoration and maintains audit integrity. |
| **`updated_at`** | TIMESTAMP | Last Update | Automated timestamp. |
| **`updated_by`** | TEXT | Last Editor | FK to `users.email`. |
| **`reviewed_at`** | TIMESTAMP | Review Date | Timestamp of approval. |
| **`reviewed_by`** | TEXT | Reviewer | FK to `users.email`. |

#### `record_languages` (M:M Join Table)

Supports records having multiple languages (e.g., cross-dialectal entries).

| Column | Type | Description | Justification |
| :--- | :--- | :--- | :--- |
| **`id`** | SERIAL | Primary Key | Standard identifier. |
| **`record_id`** | INTEGER | FK to `records.id` | Link to linguistic record. |
| **`language_id`** | INTEGER | FK to `languages.id` | Link to language metadata. |
| **`is_primary`** | BOOLEAN | Primary Marker | Indicates the primary language of the record. |

#### `search_entries` (Consolidated Lookup)

To simplify UI development and maximize performance, all searchable linguistic forms are extracted into this auxiliary table.

| Column | Type | Description | Justification |
| :--- | :--- | :--- | :--- |
| **`id`** | SERIAL | Primary Key | Standard identifier. |
| **`record_id`** | INTEGER | FK to `records.id` | Links search term to its parent record. |
| **`term`** | TEXT | Searchable String | Standard B-tree Indexed for exact and prefix matching. |
| **`entry_type`** | TEXT | Tag Origin | `lx`, `va`, `se`, `cf`, `ve`. |

#### `matchup_queue` (Manual Sync Staging)

Enables linguists to upload MDF files and manually match them against production records based on lexemes.

| Column | Type | Description | Justification |
| :--- | :--- | :--- | :--- |
| **`id`** | SERIAL | Primary Key | Standard identifier. |
| **`user_email`** | TEXT | FK to `users.email` | Isolates sessions between different users. |
| **`source_id`** | INTEGER | FK to `sources.id` | Target source for the upload. |
| **`suggested_record_id`** | INTEGER | FK to `records.id` | Optional link to an existing potential match. |
| **`batch_id`** | TEXT | Batch ID | UUID identifying the upload session. |
| **`filename`** | TEXT | Filename | Original name of the uploaded file. |
| **`status`** | TEXT | Queue State | 'pending', 'matched', 'ignored'. |
| **`lx`** | TEXT | Uploaded Lexeme | Used for automated matching suggestions. |
| **`mdf_data`** | TEXT | Raw Uploaded MDF | Preservation of data as provided by the user. |
| **`match_type`** | TEXT | Match Logic | 'exact' or 'base_form'. |
| **`created_at`** | TIMESTAMP | Creation Date | Audit trail for the upload session. |

#### `iso_639_3` (Standard Reference)

| Column | Type | Description | Justification |
| :--- | :--- | :--- | :--- |
| **`id`** | VARCHAR(3) | Primary Key | The 3-letter ISO code. |
| **`ref_name`** | TEXT | Language Name | Reference name from the ISO standard. |
| **`comment`** | TEXT | SIL Notes | Additional context from the standard. |

#### Lookup Tables (Reference Data)

**`languages`**

| Column | Type | Description | Justification |
| :--- | :--- | :--- | :--- |
| **`id`** | SERIAL | Primary Key | Standard identifier. |
| **`code`** | TEXT | Unique Code | ISO 639-3 or project code (e.g., 'wam'). |
| **`name`** | TEXT | Display Name | Human-readable language name. |
| **`description`** | TEXT | Notes | Optional context about the language. |

**`sources`**

| Column | Type | Description | Justification |
| :--- | :--- | :--- | :--- |
| **`id`** | SERIAL | Primary Key | Standard identifier. |
| **`name`** | TEXT | Full Name | Unique name (e.g., 'Natick/Trumbull'). |
| **`short_name`** | TEXT | Abbreviation | Compact display name for UI. |
| **`citation_format`** | TEXT | Citation Template | Rule for generating standard citations. |

#### Identity & Audit Tables

**`users`**

| Column | Type | Description | Justification |
| :--- | :--- | :--- | :--- |
| **`id`** | SERIAL | Primary Key | Standard identifier. |
| **`email`** | TEXT | Logical PK | Primary unique identifier for all logic. |
| **`username`** | TEXT | GitHub Handle | Display name and secondary identifier. |
| **`github_id`** | INTEGER | GitHub ID | Immutable numeric ID from GitHub. |
| **`full_name`** | TEXT | Real Name | User's full name for attribution. |
| **`is_active`** | BOOLEAN | Account Status | Flag to enable/disable user access. |
| **`last_login`** | TIMESTAMP | Last Login | Audit trail for user activity. |
| **`created_at`** | TIMESTAMP | Join Date | When the user first logged in. |
| **`extra_metadata`** | JSONB | Settings/Info | Flexible storage for future extension (pushed right). |

**`edit_history`**

| Column | Type | Description | Justification |
| :--- | :--- | :--- | :--- |
| **`id`** | SERIAL | Primary Key | Standard identifier. |
| **`record_id`** | INTEGER | FK to `records.id` | Link to the linguistic record. |
| **`user_email`** | TEXT | FK to `users.email` | Attribution for the edit. |
| **`session_id`** | TEXT | Batch Identifier | A unique UUID generated at the start of an upload/edit session. Groups related changes for granular, independent rollback of specific batches. |
| **`version`** | INTEGER | Version Number | Tracks the iteration count of the record. |
| **`change_summary`** | TEXT | Summary | Description of the changes made. |
| **`prev_data`** | TEXT | MDF (Before) | Record snapshot before this edit. |
| **`current_data`** | TEXT | MDF (After) | Record snapshot after this edit. |
| **`timestamp`** | TIMESTAMP | Edit Date | When the change was committed. |

**`permissions`**

Access control mapping between GitHub Teams and application roles.

| Column | Type | Description | Justification |
| :--- | :--- | :--- | :--- |
| **`id`** | SERIAL | Primary Key | Standard identifier. |
| **`source_id`** | INTEGER | FK to `sources.id` | Link to specific source (NULL = all). |
| **`github_org`** | TEXT | GitHub Org | Organization required for access. |
| **`github_team`** | TEXT | GitHub Team | Team within the org required for access (Mandatory). |
| **`role`** | TEXT | App Role | 'admin', 'editor', 'viewer'. |

**Role Enforcement:**
- **admin**: Automatic full access to all resources and administrative functions.
- **editor**: Authorized to edit, update, and manage MDF records ONLY.
- **viewer**: Read-only access to records. **MAY NEVER** edit or modify any data (HARD BLOCK).

**`user_activity_log`**

| Column | Type | Description | Justification |
| :--- | :--- | :--- | :--- |
| **`id`** | SERIAL | Primary Key | Standard identifier. |
| **`user_email`** | TEXT | FK to `users.email` | Link to the performing user. |
| **`session_id`** | TEXT | Batch Identifier | Links activity to a unique upload/edit batch (UUID). Allows separate tracking and revert capability for multiple batches from the same user. |
| **`action`** | TEXT | Event Type | e.g., 'login', 'sync_start', 'batch_rollback'. |
| **`details`** | TEXT | Extra Info | Contextual information about the action. |
| **`ip_address`** | TEXT | IP Info | Security and audit logging. |
| **`timestamp`** | TIMESTAMP | Event Date | When the action occurred. |

**`schema_version`**

| Column | Type | Description | Justification |
| :--- | :--- | :--- | :--- |
| **`id`** | SERIAL | Primary Key | Standard identifier. |
| **`version`** | INTEGER | Current Version | Tracks the applied schema iteration. |
| **`applied_at`** | TIMESTAMP | Date | When this version was successfully applied. |
| **`description`** | TEXT | Summary | Notes on what changes were introduced in this version. |

---

## 3. Dual-Engine Search Strategy

| Engine | Technology | Best For... |
| :--- | :--- | :--- |
| **Linguistic Tool** | `ILIKE` / `LIKE` | Standard substring, prefix, and suffix matching with 100% environment parity. |
| **Global Search** | PostgreSQL FTS | Natural language "Google-style" searches across glosses, examples, and notes. |

---

## 4. Rollback & Data Recovery Strategy

To protect the production database from "bad" uploads (e.g., uploading old or incorrect data), the system implements a multi-layered defense and recovery strategy:

### Layer 1: Staging & Review (`matchup_queue`)
- All mass uploads are first placed in the `matchup_queue`.
- Linguists must review and confirm matches before any production data is updated.
- This serves as the first line of defense against batch data corruption.

### Layer 2: Batch Recovery (`session_id`)
- Every edit performed during an upload session is tagged with a unique, system-generated `session_id` (UUID) in the `edit_history` table.
- **Granular Control**: If a user uploads multiple batches, each batch receives its own unique ID. This allows an administrator to revert one specific "bad" batch without affecting other successful uploads from the same user or time period.
- **Rollback Mechanism**: The system identifies all `edit_history` rows matching the specific `session_id` and restores the `prev_data` snapshots to the `records` table.
- This allows an entire bad upload to be reverted without manually fixing each record.

### Layer 3: Data Preservation & "Safety-First" Deletion
- **Restrictive Deletion (RESTRICT)**: To prevent accidental data loss, the database uses restrictive foreign key constraints. 
    - A **Record** cannot be deleted if it has associated **Edit History** or **Search Entries**.
    - A **User** cannot be deleted if they have **Activity Logs**, **Edit History**, or **Matchup Queue** entries attributed to them.
    - **Language** and **Source** records cannot be deleted if they are referenced by any **Record**.
- **Permanent Attribution**: By using `user_email` as a stable identifier across all audit tables, the system ensures that every update, upload, and administrative action remains identifiable even if a user's GitHub handle changes or if the user account is deactivated.
- **Soft-Deletes (Optional/Future)**: While currently using hard-deletes (protected by restrictions), the system is designed to transition to `is_deleted` flags to preserve linguistic entries while hiding them from the UI.

### Layer 4: Point-in-Time Recovery
- For catastrophic events, the PostgreSQL database (Aiven) provides automated backups and point-in-time recovery.

---

## 5. Implementation Roadmap

1.  **Stage 1: SQL Models**: Update `src/database.py` with the finalized column order, relationships, the `Variant` model, `matchup_queue`, and `schema_version` tracking.
2.  **Stage 2: DDL Documentation**: Sync `docs/database/SCHEMA.md` with the production design.
3.  **Stage 3: Parser Refactor**: Update `src/mdf/parser.py` to support `hm`, `va`, `se`, `cf`, `ve` and implement strict `\nt Record:` deduplication.
4.  **Stage 4: Seeding**: Populate `languages` and `sources` with initial project defaults.
5.  **Stage 5: Migration**: Run a script to scan existing `mdf_data`, inject correct IDs, and build the search entries table.

---

## 5. Development Notes & Justifications

- **Why dedicated columns for `lx`, `ps`, `ge`?** While `mdf_data` is the source of truth, these columns allow for standard SQL filtering, sorting, and high-performance list views in Streamlit without parsing text on every request.
- **Why avoid custom MDF tags?** Standard compliance ensures the exported data remains compatible with legacy tools like ShoeBox or ToolBox.
- **Why `\nt Record:` over other tags?** The `\nt` tag is the standard "General Note" field. Prepending "Record: " provides a clear, human-readable indicator of the database identity that is unlikely to conflict with linguistic notes.
- **Email as User Identifier**: In the `edit_history`, `user_activity_log`, and `users` tables, the email is used as the primary logical link to ensure audit trails remain intact even if a user changes their GitHub username or if the record is removed from the `users` table.
