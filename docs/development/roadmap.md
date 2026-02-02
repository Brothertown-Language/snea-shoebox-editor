<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->
## Overview

This document outlines the implementation plan for the **SNEA Shoebox Editor**, a 100% Python-based web application for
collaborative, version-controlled editing of linguistic records from across Southern New England Algonquian (SNEA) languages.

---

## Setup & Deployment Flow

To ensure a "Zero-Touch" developer experience, the setup follows a strict sequential order. Complete each phase before
moving to the next.

**Note: If you are contributing to an existing repository via pull requests or have direct access, and the infrastructure is already configured, you can skip to Step 1 of Phase 3 (Initialize Environment) for local development.**

### Phase 1: Preparation (Manual One-Time Setup)

Before initializing the project, you must manually obtain the necessary "Master Keys" from Cloudflare and GitHub. **Note: GitHub OAuth credentials will be generated in Phase 5.**

1. **Generate Cloudflare API Token**:
    - Go to the [**Cloudflare Dashboard > API Tokens**](https://dash.cloudflare.com/profile/api-tokens).
    - Click **Create Token** and use the **Get started** button next to **Create Custom Token**.
    - *Note: A User API Token is recommended because it supports the mix of Account and Zone permissions required by Wrangler.*
    - Create a token with: `Account` | `D1` | `Edit`, `Account` | `Workers Scripts` | `Edit`, `Account` | `Cloudflare Pages` | `Edit`, `Account` | `Account Settings` | `Read`, `Zone` | `Workers Routes` | `Edit`, and `Zone` | `DNS` | `Read`.
    - *Note: `Workers KV Storage` and `Workers R2 Storage` are NOT required.*
    - **Final Summary Verification**:
        Your token summary should look like this:
        > **snea-editor API token summary**
        > This API token will affect the below accounts and zones, along with their respective permissions:
        > * **All accounts** - `Cloudflare Pages: Edit`, `Workers Scripts: Edit`, `Account Settings: Read`, `D1: Edit`
        > * **All zones** - `Workers Routes: Edit`, `DNS: Read`
2. **Generate GitHub Personal Access Token (PAT)**:
    - Go to [**Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**](https://github.com/settings/tokens).
    - Generate a token with the `repo` scope.

### Phase 2: Repository Initialization

1. **Create Private Repo**: Create a new **private** repository on GitHub (e.g., `snea-editor-private`) within the
   `Brothertown-Language` organization.
2. **Local Setup**: Clone the repo to your workstation.

### Phase 3: Automated Infrastructure & Schema Setup [IN PROGRESS]

Use the provided `bootstrap_env.py` script to automate the heavy lifting. **Note: This script will automatically detect your primary Cloudflare Account ID and set up the D1 database.**

1. **Initialize Environment [COMPLETED]**:
   It is required to use Docker for local development. See the **[Local Development Guide](local-development.md)**. Note that Cloudflare D1 type access (simulated locally) is required for local work.
2. **Schema Management [IN PROGRESS]**:
   The application automatically handles its own database schema. Upon first run and during subsequent updates, the app will:
   - Create any missing tables. (Implemented: `sources`, `records`, `seeding_progress`)
   - Update existing tables using `ALTER` statements as appropriate. (Pending)
   Manual execution of `schema.sql` via Wrangler is NOT required.
3. **Set Environment Variables [COMPLETED]**:
   These variables are used by the bootstrap script to configure your infrastructure. Create a `.env` file in the project root:

   ```env
   CF_EMAIL="your_cloudflare_email"
   CF_API_KEY="your_global_api_key"
   CF_API_TOKEN="your_cloudflare_user_token"
   GH_TOKEN="your_github_pat"
   ```

   *Note: Once the bootstrap script runs successfully, these keys are stored securely in GitHub Secrets, and you
   will not need them locally for deployment.*
3. **Run the Bootstrap Script (Production Only)**:
   This script automates the one-time setup of your production infrastructure. You must run it locally (requires Python and `uv`).

   ```bash
   uv venv && source .venv/bin/activate
   uv pip install -e .
   uv run python bootstrap_env.py
   ```

   **IMPORTANT**: This step is only for the initial setup of Cloudflare D1 and GitHub Secrets. **Skip this for local development.**

### Phase 4: Custom Domain Setup (Manual)

Since the app will use `snea-editor.michael-conrad.com` as the primary domain, you must link the Cloudflare Pages (apex) and Workers (subdomain) accordingly. **Note:
Cloudflare will automatically handle the DNS records once you add these domains in the dashboard.**

1. **Pages Custom Domain**:
    - Go to **Workers & Pages** > **snea-editor** (your Pages project) > **Custom domains**.
    - Add `snea-editor.michael-conrad.com`.
    - Cloudflare will prompt you to "Activate" or "Setup" the DNS; click through to let it create the record.
2. **Worker Custom Domain**:
    - Go to **Workers & Pages** > **snea-backend** (your Worker) > **Triggers** > **Custom Domains**.
    - Add `snea-backend.michael-conrad.com`.
    - Cloudflare will automatically generate the DNS record for this subdomain.

### Phase 5: GitHub OAuth Setup (Manual)

Authentication is handled via GitHub OAuth to ensure secure access and contributor tracking. **Access is restricted to members of the `proto-SNEA` team in the `Brothertown-Language` organization.**

1. **Register GitHub OAuth App**:
    - Go to [GitHub **Settings** > **Developer settings** > **OAuth Apps** > **New OAuth App**](https://github.com/settings/applications/new).
    - **Application Name**: `SNEA Shoebox Editor`
    - **Homepage URL**: `https://snea-editor.michael-conrad.com`
    - **Authorization callback URL**: `https://snea-editor.michael-conrad.com`
2. **Update Repo Secrets**:
    - Manually add `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` (from the OAuth App you just created) to your GitHub
      Repository Secrets.
3. **Required Scopes**:
    - Ensure the OAuth flow requests the `read:org` scope to verify team membership.

### Phase 5b: Local Development Auth Config (Manual)

To support authentication during local development, a separate GitHub OAuth application should be configured to point to your local environment.

1.  **Register Local GitHub OAuth App**:
    - Go to [GitHub **Settings** > **Developer settings** > **OAuth Apps** > **New OAuth App**](https://github.com/settings/applications/new).
    - **Application Name**: `SNEA Shoebox Editor (Local)`
    - **Homepage URL**: `http://localhost:8787`
    - **Authorization callback URL**: `http://localhost:8787`
2.  **Local Environment Configuration**:
    - Create a `.env` file in the project root (not committed to VCS).
    - Add `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` from the local OAuth app.
    - Build stlite frontend: `uv run python scripts/bundle_stlite.py`
3.  **Unified Worker Architecture**:
    - The worker (`src/backend/worker.py`) serves both API and stlite frontend from `http://localhost:8787`.
    - Team membership validation against the `proto-SNEA` team remains active in local development, requiring an internet connection.

---

## Architecture Details

### 1. Automated Deployment (Cloudflare Git Integration)

- **Process**: Cloudflare automatically pulls and builds from git on push to main branch.
- **stlite**: Uses stlite (Streamlit compiled to WebAssembly) for browser-based reactive UI.
- **Clean Workstation**: Local development uses Docker to avoid polluting the host environment with `npm`, `wrangler`, or specific Python versions.
- **Zero-Config Deployment**: Cloudflare handles build and deployment directly without GitHub Actions.

### 2. Python Frontend (stlite) [MINIMAL IMPLEMENTATION]

- **Responsive UI [PENDING]**: Basic mobile and desktop support using grid-based layouts (Current: Fixed layout with sidebar).
- **Strictly Python [COMPLETED]**: No JavaScript required for UI logic.
- **Basic Record Editor [PARTIAL]**:
    - **Display Mode [PENDING]**: Colorized and enhanced rendering of MDF records for linguistic readability.
    - **Edit Mode [COMPLETED]**: Plain text area containing raw MDF data for direct editing.
    - **Transition [PENDING]**: Validation occurs after editing to provide visual feedback (colorization), but does not block saving.
- **Advisory Validation [PENDING]**: Linguistic validation (e.g., hierarchy checks) is purely advisory. It highlights potential issues for linguists but **must not** interfere with or prevent the saving of records.
- **NFD Sorting [COMPLETED]**: Records are sorted by their extracted headword (\lx) using NFD normalization with leading punctuation ignored via `sort_key` column.
- **Read-Only Metadata [PENDING]**: Record metadata (last editor, timestamp, version) is visible but read-only to users (Current: Metadata tracked in DB but not displayed in UI).

### 3. Python Backend (Cloudflare Workers) [PARTIAL IMPLEMENTATION]

- **Data Layer [PARTIAL]**: D1 database using Python bindings (Implemented: `sources`, `records`, `seeding_progress`, `users`, `permissions`; Missing: `edit_history`, `embeddings`).
- **Source Code [COMPLETED]**: Implementation resides in `src/backend/worker.py`.
- **OAuth Authentication [COMPLETED]**: GitHub OAuth login and callback endpoints with session management.
- **Basic CRUD [PARTIAL]**: 
    - **GET /api/records [COMPLETED]**: Paginated record listing with NFD sorting.
    - **GET /api/records/count [COMPLETED]**: Total record count.
    - **POST /api/records/:id [PARTIAL]**: Basic update without conflict detection or edit history tracking.
    - **GET /api/me [COMPLETED]**: User profile endpoint.
- **Auto-Seeding [COMPLETED]**: Automatic seeding from `Natick/Trumbull` source file on first initialization.

### 4. Concurrency & Authentication Management [PARTIAL IMPLEMENTATION]

- **GitHub OAuth Authentication [COMPLETED]**: Access is strictly limited to authenticated GitHub users.
    - **Team Membership Verification [PENDING]**: Backend does NOT currently verify `proto-SNEA` team membership within the `Brothertown-Language` organization. All authenticated GitHub users can access the application.
- **Auth Logic [COMPLETED]**:
    - Backend retrieves user token via OAuth exchange.
    - Backend creates session tokens with HMAC signing.
    - Session persistence via HTTP-only cookies.
- **Optimistic Locking [PENDING]**: The editor does NOT currently implement optimistic locking. The `current_version` field exists in the database and is incremented on save, but no version checking occurs before updates.
- **Conflict Resolution Workflow [PENDING]**:
    - Version mismatch detection not implemented.
    - Conflict resolution UI not implemented.
    - No side-by-side comparison dialog.
- **Per-Record History Drawer [PENDING]**: No UI component for viewing edit history (edit_history table does not exist).
- **No Explicit Locking [COMPLETED]**: Records are never "locked" for editing. Multiple users can open the same record simultaneously.

### 5. Data Persistence & Edit History [NOT IMPLEMENTED]

- **Edit History Table [PENDING]**: The `edit_history` table does not exist. Changes to records are NOT tracked.
- **Audit Metadata [PENDING]**: No history entries are created. The following are not tracked:
    - **Modified Timestamp**: Only `updated_at` in records table (overwritten on each save).
    - **OAuth User Email**: Only `updated_by` in records table (overwritten on each save).
    - **Previous Data**: Not tracked.
    - **Current Data**: Not tracked separately from main record.

### 6. Administration & Permissions [NOT IMPLEMENTED]

- **Permissions Management [PENDING]**: No UI exists for managing the `permissions` table. The table exists in the database but is not used by the application.
- **Embeddings Management [PENDING]**: The `embeddings` table does not exist. No AI-generated vectors or search functionality implemented.
    - **Automatic Recalculation [PENDING]**: No vector recalculation logic exists.

---

## Feature Roadmap (Upcoming)

### Phase 6: Search & Discovery
1. **Unified Search Widget**: A single search interface supporting both FTS (Keyword) and Semantic (Vector) searching.
    - **Expanded Scope**: Search matches against Lexeme variants, Notes (`\nt`), and all example sentences (across all languages), in addition to `\lx` and `\ge` tags.
    - Support for "Hybrid Search" using a **combined weighted score** to rank results.
    - Embedding Model: `@cf/baai/bge-m3` for superior multilingual and sparse retrieval support (ideal for Algonquian-English code-switching).
2. **Source Filtering**: UI components to filter records by origin source (e.g., Natick, Mohegan).
3. **Manual Record Creation**:
    - Capability to manually add new records to any existing source.
    - **Conflict Detection**: When adding to an existing source, a semantic and keyword search is automatically performed to highlight potential conflicts or duplicate entries.
    - Support for creating records with entirely new sources not previously seen in the system.
4. **Embeddings Maintenance**:
    - **Stale Vector Handling**: When a search operation detects a `record_version` mismatch, the system will trigger a vector recalculation.
    - **Recalculation Strategy**: Recalculation will be attempted **inline** for single-record updates to ensure search accuracy, with a fallback to background processing if batch updates are detected.

### Phase 7: Quality Control & Audit
1. **Review Workflow**: Implementation of the 'approved' status to flag records as **vetted or updated**.
    - Note: Approved records remain editable by both **Editors and Admins** for future enhancements (cross-references, notes).
2. **Admin Audit Portal**: Restricted view (Admins only) of the `edit_history`.
    - **Full Snapshot History**: Every edit stores the full MDF record snapshot to facilitate easier human review, external exports, and reliable rollback.

### Phase 8: Developer Experience
1. **Dedicated Dev UI**: A built-in UI component (Dev Info) for inspecting system internals without using CLI tools.
    - **Table Schema Inspector**: View SQL schemas for all D1 tables.
    - **Environment Reporting**: Report Python versions and platforms for both Frontend (stlite/Pyodide) and Backend (Worker).

