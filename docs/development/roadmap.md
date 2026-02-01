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
    - Create a token with: `Account` | `Workers Scripts` | `Edit`, `Account` | `Workers KV Storage` | `Edit`, `Account` | `Workers R2 Storage` | `Edit`, `Account` | `D1` | `Edit` (if available), `Account` | `Cloudflare Pages` | `Edit`, `Account` | `Account Settings` | `Read`, and `Zone` | `Workers Routes` | `Edit`.
    - *Note: D1 permissions are implicitly included in Workers permissions. "Account-level" tokens often fail for Wrangler deployments.*
    - **Final Summary Verification**:
        Your token summary should look like this:
        > **snea-editor API token summary**
        > This API token will affect the below accounts and zones, along with their respective permissions:
        > * **All accounts** - `Workers Scripts: Edit`, `Workers KV Storage: Edit`, `Workers R2 Storage: Edit`, `Cloudflare Pages: Edit`, `Account Settings: Read`
        > * **All zones** - `Workers Routes: Edit`
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
   python bootstrap_env.py
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
    - **Homepage URL**: `http://localhost:8501`
    - **Authorization callback URL**: `http://localhost:8501`
2.  **Local Environment Configuration**:
    - Create a `.env` file in the project root (not committed to VCS).
    - Add `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` from the local OAuth app.
3.  **CORS & Team Validation**:
    - The backend (`src/backend/worker.py`) must be configured to allow CORS requests from `http://localhost:8501` during local development.
    - Team membership validation against the `proto-SNEA` team remains active in local development, requiring an internet connection.

---

## Architecture Details

### 1. Automated Deployment (GitHub Actions)

- **Workflow**: `.github/workflows/deploy.yml` handles the build.
- **Streamlit**: Uses Streamlit for the reactive UI.
- **Clean Workstation**: Local development uses Docker to avoid polluting the host environment with `npm`, `wrangler`, or specific Python versions.
- **Zero-Workstation-Install**: All deployment tools run strictly in the GitHub runner.

### 2. Python Frontend (Streamlit) [IN PROGRESS]

- **Responsive UI [IN PROGRESS]**: Basic mobile and desktop support using grid-based layouts (Implemented: `RecordList`).
- **Strictly Python [COMPLETED]**: No JavaScript required for UI logic.
- **Hybrid Record Editor [PENDING]**:
    - **Display Mode**: Colorized and enhanced rendering of MDF records for linguistic readability.
    - **Edit Mode**: Switches to a plain text area containing raw MDF data for direct editing.
    - **Transition**: Validation occurs after editing to provide visual feedback (colorization), but does not block saving.
- **Advisory Validation [PENDING]**: Linguistic validation (e.g., hierarchy checks) is purely advisory. It highlights potential issues for linguists but **must not** interfere with or prevent the saving of records.
- **NFD Sorting [PENDING]**: Records must be sorted by their extracted headword (\lx). Sorting must use NFD normalization (preserving diacritics), and leading punctuation must be ignored. (Current: Basic ASC sorting in DB).
- **Read-Only Metadata [PENDING]**: Record metadata (last editor, timestamp, version) is visible but read-only to users.

### 3. Python Backend (Cloudflare Workers) [IN PROGRESS]

- **Data Layer [IN PROGRESS]**: D1 database using Python bindings (Implemented: `sources`, `records`, `seeding_progress`).
- **Source Code [COMPLETED]**: Implementation resides in `src/backend/worker.py`.
- **Manual Seeding [IN PROGRESS]**: The app starts with an empty database. Administrators can trigger seed ingestion from multiple
  private source files (Natick, SNEALEX, Mohegan Dictionary, etc.) via dedicated endpoints. (Implemented: Auto-seeding for `Natick/Trumbull`).

### 4. Concurrency & Authentication Management

- **GitHub OAuth Authentication**: Access is strictly limited to authenticated GitHub users **who are active members of the `proto-SNEA` team within the `Brothertown-Language` organization.**
- **Auth Logic**:
    - Backend retrieves user token via OAuth exchange.
    - Backend verifies team membership via `GET /orgs/Brothertown-Language/teams/proto-snea/memberships/{username}`.
    - Access is granted only if the state is `active`.
- **Optimistic Locking**: The editor uses optimistic locking to prevent overlapping edits. When a user attempts to save a record, the application verifies that the `current_version` in the database matches the version the user began editing. If they differ, the save is rejected, and the user is prompted to resolve the conflict via a comparison dialog.
- **Conflict Resolution Workflow**:
    - When a version mismatch is detected, a dialog must display both the **Live Record** (currently in the database) and the **Edited Record** (user's local changes) side-by-side.
    - Users must be presented with two primary options:
        - **Reload**: Discard local changes and load the latest live version.
        - **Overwrite**: Force save the local changes, incrementing the version and overwriting the live record.
- **Per-Record History Drawer**: A toggleable UI component for the active record that displays its specific `edit_history`, allowing users to see previous snapshots and audit changes.
- **No Explicit Locking**: Records are never "locked" for editing. Multiple users can open the same record simultaneously; the first one to save successfully increments the version, causing subsequent saves from other users (on the older version) to trigger the conflict resolution workflow.

### 5. Data Persistence & Edit History

- **Edit History Table**: All changes to records must be tracked in a dedicated edit history table.
- **Audit Metadata**: Each history entry must include:
    - **Modified Timestamp**: Exact time of the change.
    - **OAuth User Email**: The identity of the editor.
    - **Previous Data**: State of the record before the edit.
    - **Current Data**: State of the record after the edit.
### 6. Administration & Permissions

- **Permissions Management**: A dedicated, separate editor must be provided for the `permissions` table to manage GitHub Org/Team mappings and source-specific roles.
- **Embeddings Management**: A dedicated management interface for the `embeddings` table to monitor, refresh, and validate AI-generated vectors.
    - **Automatic Recalculation**: Logic to automatically trigger vector recalculation when a `record_version` mismatch is detected during a search operation.

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
    - **Environment Reporting**: Report Python versions and platforms for both Frontend (Streamlit) and Backend (Worker).

