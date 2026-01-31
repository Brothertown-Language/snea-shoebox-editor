<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->

# SNEA Shoebox Editor - Database Schema

This document defines the database schema for the SNEA Online Shoebox Editor. The schema is designed for **Cloudflare D1 (SQLite)** and is compatible with local development environments.

## 1. Primary Data Tables

### `sources` [STATUS: APPROVED]
Defines the different collections of records (e.g., Natick/Trumbull, Modern Mohegan Dictionary).

```sql
CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,            -- e.g., 'Natick/Trumbull', 'Modern Mohegan'
    description TEXT,                     -- Details about the original source
    citation_format TEXT,                 -- Optional: Standard citation format for this source
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### `records` [STATUS: APPROVED]
The source of truth for all linguistic entries in MDF format.

```sql
CREATE TABLE records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,           -- Link to the origin source (Natick, Mohegan, etc.)
    lx TEXT NOT NULL,                     -- Lexeme (\lx): Main headword
    ps TEXT,                              -- Part of Speech (\ps)
    ge TEXT,                              -- English Gloss (\ge): Primary gloss for list views
    mdf_data TEXT NOT NULL,               -- Full raw MDF record text (unbounded)
    status TEXT NOT NULL DEFAULT 'draft', -- 'draft', 'edited', or 'approved'
    source_page TEXT,                     -- Page or section number in the main source
    current_version INTEGER NOT NULL DEFAULT 1, -- For optimistic locking and versioning
    is_deleted INTEGER NOT NULL DEFAULT 0, -- Soft delete flag (0=active, 1=deleted)
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,                      -- Identifier (email/ID) of last editor
    reviewed_at DATETIME,                 -- When the record was marked 'approved'
    reviewed_by TEXT,                     -- Identifier of the reviewer
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- Index for filtering by source and status (FTS handles keyword search)
CREATE INDEX idx_records_source_status ON records(source_id, status);
CREATE INDEX idx_records_deleted ON records(is_deleted);
```

### `embeddings` [STATUS: APPROVED]
Supports AI-based semantic search by storing vectors for various parts of a record.

```sql
CREATE TABLE embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER NOT NULL,           -- Link to parent record
    vector_id TEXT NOT NULL,              -- UUID used in Cloudflare Vectorize
    source_tag TEXT NOT NULL,             -- MDF tag embedded (e.g., 'lx', 'ge', 'va')
    original_text TEXT NOT NULL,          -- The raw text from the MDF tag
    embedded_text TEXT NOT NULL,          -- The final string sent to the AI (e.g. with context)
    model_name TEXT NOT NULL,             -- AI model used (e.g., @cf/baai/bge-small-en-v1.5)
    record_version INTEGER NOT NULL,      -- Version of the record when this was generated
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE CASCADE
);

CREATE INDEX idx_embeddings_vector_id ON embeddings(vector_id);
CREATE INDEX idx_embeddings_record_id ON embeddings(record_id);
CREATE INDEX idx_embeddings_stale ON embeddings(record_id, record_version);
```

### `records_fts` (Virtual Table) [STATUS: APPROVED]
High-performance keyword search using SQLite FTS5.

```sql
-- Virtual table for lightning-fast keyword search
CREATE VIRTUAL TABLE records_fts USING fts5(
    lx, ps, ge, mdf_data,
    content='records',      -- Link to the actual data
    content_rowid='id'      -- Link to the record id
);

-- Triggers to keep the search index in sync automatically
CREATE TRIGGER records_ai AFTER INSERT ON records BEGIN
  INSERT INTO records_fts(rowid, lx, ps, ge, mdf_data) VALUES (new.id, new.lx, new.ps, new.ge, new.mdf_data);
END;

CREATE TRIGGER records_ad AFTER DELETE ON records BEGIN
  INSERT INTO records_fts(records_fts, rowid, lx, ps, ge, mdf_data) VALUES('delete', old.id, old.lx, old.ps, old.ge, old.mdf_data);
END;

CREATE TRIGGER records_au AFTER UPDATE ON records BEGIN
  INSERT INTO records_fts(records_fts, rowid, lx, ps, ge, mdf_data) VALUES('delete', old.id, old.lx, old.ps, old.ge, old.mdf_data);
  INSERT INTO records_fts(rowid, lx, ps, ge, mdf_data) VALUES (new.id, new.lx, new.ps, new.ge, new.mdf_data);
END;
```

---

## 2. History & Audit Tables

### `edit_history` [STATUS: APPROVED]
Tracks every change made to a record for audit trails and rollback capability.

```sql
CREATE TABLE edit_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER NOT NULL,           -- Link to parent record
    version INTEGER NOT NULL,             -- Version number resulting from this edit
    prev_data TEXT,                       -- MDF snapshot BEFORE the change
    current_data TEXT NOT NULL,           -- MDF snapshot AFTER the change
    user_id TEXT NOT NULL,                -- Identifier of the editor
    change_summary TEXT,                  -- Optional human-readable summary of changes
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE CASCADE
);

CREATE INDEX idx_history_record_id ON edit_history(record_id);
```

---

## 3. User & Access Control

### `users` [STATUS: APPROVED]
Stores user identity metadata from GitHub OAuth.

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    github_id INTEGER UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,        -- GitHub handle
    name TEXT,                            -- Display name
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### `user_activity_log` [STATUS: APPROVED]
Tracks general user actions for security and usage analytics (distinct from MDF record edits).

```sql
CREATE TABLE user_activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,         -- e.g., 'login', 'logout', 'view_record', 'delete_record'
    details TEXT,                 -- JSON or string with extra info
    ip_address TEXT,              -- Optional, for audit
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_activity_user_id ON user_activity_log(user_id);
```

### `permissions` [STATUS: APPROVED]
Maps GitHub Organizations and Teams to application roles and sources.

```sql
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,                   -- Link to specific source (NULL = all sources)
    github_org TEXT NOT NULL,             -- GitHub Organization name
    github_team TEXT,                    -- GitHub Team slug (NULL = all org members)
    role TEXT NOT NULL DEFAULT 'viewer',  -- 'admin', 'editor', 'viewer'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
);

CREATE INDEX idx_permissions_org_team ON permissions(github_org, github_team);
```
