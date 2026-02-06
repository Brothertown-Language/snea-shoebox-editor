<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->

# SNEA Shoebox Editor - Database Schema

This document defines the database schema for the SNEA Online Shoebox Editor. The schema is based on the authoritative [DATABASE_SPECIFICATION.md](./DATABASE_SPECIFICATION.md) and is designed for **PostgreSQL (Aiven)**.

---

## 1. Core Tables

### `records`
The source of truth for all linguistic entries in MDF format.

```sql
CREATE TABLE records (
    id SERIAL PRIMARY KEY,                -- Matches \nt Record: <id>
    lx TEXT NOT NULL,                     -- Lexeme (\lx)
    hm INTEGER DEFAULT 1,                 -- Homonym Number (\hm)
    ps TEXT,                              -- Part of Speech (\ps)
    ge TEXT,                              -- English Gloss (\ge)
    language_id INTEGER NOT NULL,         -- FK to languages.id
    source_id INTEGER NOT NULL,           -- FK to sources.id
    source_page TEXT,                     -- Specific citation (\so)
    status TEXT NOT NULL DEFAULT 'draft', -- 'draft', 'edited', 'approved'
    embedding VECTOR(1536),               -- For cross-reference lookup
    mdf_data TEXT NOT NULL,               -- Full raw MDF text
    FOREIGN KEY (language_id) REFERENCES languages(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);
```

### `search_entries`
Consolidated lookup table for instant search across lexemes, variants, and subentries. Uses **GIN Trigram Indexing**.

```sql
CREATE TABLE search_entries (
    id SERIAL PRIMARY KEY,
    record_id INTEGER NOT NULL,           -- Link to parent record
    term TEXT NOT NULL,                   -- Searchable string (\lx, \va, \se, etc.)
    entry_type TEXT NOT NULL,             -- 'lx', 'va', 'se', 'cf', 've'
    FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE CASCADE
);

-- Extension required: CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_search_entries_term_trgm ON search_entries USING GIN (term gin_trgm_ops);
```

### `matchup_queue`
Staging area for uploaded MDF files requiring manual lexeme-based matching.

```sql
CREATE TABLE matchup_queue (
    id SERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,             -- FK to users.email
    source_id INTEGER NOT NULL,           -- Target collection
    suggested_record_id INTEGER,          -- System potential match (FK to records.id)
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'matched', 'ignored'
    lx TEXT,                              -- Uploaded Lexeme
    mdf_data TEXT NOT NULL,               -- Raw uploaded entry
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email),
    FOREIGN KEY (source_id) REFERENCES sources(id),
    FOREIGN KEY (suggested_record_id) REFERENCES records(id)
);
```

---

## 2. Lookup Tables (Reference Data)

### `languages`
```sql
CREATE TABLE languages (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,            -- e.g., 'wam', 'mohegan'
    name TEXT NOT NULL,                   -- e.g., 'Wampanoag'
    description TEXT
);
```

### `sources`
```sql
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,            -- e.g., 'Natick/Trumbull'
    short_name TEXT,
    citation_format TEXT
);
```

---

## 3. Identity & Audit Tables

### `users`
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,           -- Logical Primary Key
    username TEXT UNIQUE NOT NULL,        -- GitHub Handle
    github_id INTEGER UNIQUE NOT NULL,    -- GitHub Numeric ID
    full_name TEXT,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

### `edit_history`
```sql
CREATE TABLE edit_history (
    id SERIAL PRIMARY KEY,
    record_id INTEGER NOT NULL,
    user_email TEXT NOT NULL,             -- FK to users.email
    session_id TEXT,                      -- Unique UUID per batch
    version INTEGER NOT NULL,
    change_summary TEXT,
    prev_data TEXT,
    current_data TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE CASCADE,
    FOREIGN KEY (user_email) REFERENCES users(email)
);
```

### `permissions`
```sql
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    source_id INTEGER,                   -- Link to source (NULL = all)
    github_org TEXT NOT NULL,
    github_team TEXT,
    role TEXT NOT NULL DEFAULT 'viewer',  -- 'admin', 'editor', 'viewer'
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
);
```

### `user_activity_log`
```sql
CREATE TABLE user_activity_log (
    id SERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,             -- FK to users.email
    session_id TEXT,                      -- Unique UUID per batch
    action TEXT NOT NULL,                 -- e.g., 'login', 'sync_start', 'batch_rollback'
    details TEXT,
    ip_address TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);
```

### `schema_version`
```sql
CREATE TABLE schema_version (
    id SERIAL PRIMARY KEY,
    version INTEGER NOT NULL,             -- Applied schema version
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT                      -- Change summary
);
```

---

## 4. Search Strategy

### Global Search (Full-Text Search)
Searches across headwords, glosses, examples, and raw data with weighted priority.

```sql
CREATE INDEX idx_records_fts ON records USING GIN (
    (
        setweight(to_tsvector('english', coalesce(lx, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(ge, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(mdf_data, '')), 'D')
    )
);
```

### Linguistic Search (Trigram)
Managed via the `search_entries` table for high-performance substring, prefix, and suffix matching.
