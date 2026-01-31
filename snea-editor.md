## Overview

This document outlines the implementation plan for the **SNEA Shoebox Editor**, a 100% Python-based web application for
concurrent editing of linguistic records from across Southern New England Algonquian (SNEA) languages.

---

## Setup & Deployment Flow

To ensure a "Zero-Touch" developer experience, the setup follows a strict sequential order. Complete each phase before
moving to the next.

### Phase 1: Preparation (Manual One-Time Setup)

Before initializing the project, you must manually obtain the necessary "Master Keys" from Cloudflare and GitHub. **Note: GitHub OAuth credentials will be generated in Phase 5.**

1. **Generate Cloudflare API Token**:
    - Go to [Cloudflare Profile > API Tokens](https://dash.cloudflare.com/profile/api-tokens).
    - Use the **Edit Cloudflare Workers** template.
    - Ensure it has `Account.Workers Scripts: Edit`, `Account.D1: Edit`, and `User.Account: Read`.
2. **Generate GitHub Personal Access Token (PAT)**:
    - Go to **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
    - Generate a token with the `repo` scope.

### Phase 2: Repository Initialization

1. **Create Private Repo**: Create a new **private** repository on GitHub (e.g., `snea-editor-private`) within the
   `Brothertown-Language` organization.
2. **Local Setup**: Clone the repo to your workstation.

### Phase 3: Automated Infrastructure Setup

Use the provided `bootstrap_env.py` script (located in `tech-docs/snea-online-concurrent-shoebox-editor/`) to automate
the heavy lifting. **Note: This script will automatically detect your primary Cloudflare Account ID and set up the D1
database.**

1. **Initialize Environment**:
   Use `uv` to create a virtual environment and install dependencies. From the project root:
   ```bash
   cd tech-docs/snea-online-concurrent-shoebox-editor/
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```
2. **Set Environment Variables**:
   These variables are used by the bootstrap script to configure your infrastructure. You can either export them
   temporarily in your terminal or create a `.env` file in this directory (though the script currently expects
   them in the environment).

   ```bash
   export CF_API_TOKEN="your_cloudflare_token"
   export GH_TOKEN="your_github_pat"
   ```

   *Note: Once the bootstrap script runs successfully, these keys are stored securely in GitHub Secrets, and you
   will not need them locally for deployment.*
3. **Run the Bootstrap Script**:
   Make sure you are in the `tech-docs/snea-online-concurrent-shoebox-editor/` directory:
   ```bash
   python3 bootstrap_env.py
   ```
   **What this does automatically**:
    - Creates the `snea-shoebox` D1 database on Cloudflare.
    - Generates a secure `JWT_SECRET`.
    - Encrypts and uploads `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, and `JWT_SECRET` to your GitHub Repo
      Secrets.
    - Generates a ready-to-use `wrangler.toml` file.

### Phase 4: Custom Domain Setup (Manual)

Since the app will use `michael-conrad.com`, you must link the Cloudflare Pages and Workers to the subdomains. **Note:
Cloudflare will automatically handle the DNS CNAME records once you add these domains in the dashboard.**

1. **Pages Custom Domain**:
    - Go to **Workers & Pages** > **snea-editor** (your Pages project) > **Custom domains**.
    - Add `snea-editor.michael-conrad.com`.
    - Cloudflare will prompt you to "Activate" or "Setup" the DNS; click through to let it create the record.
2. **Worker Custom Domain**:
    - Go to **Workers & Pages** > **snea-backend** (your Worker) > **Triggers** > **Custom Domains**.
    - Add `snea-api.michael-conrad.com`.
    - Cloudflare will automatically generate the DNS record for this subdomain.

### Phase 5: GitHub OAuth Setup (Manual)

Authentication is handled via GitHub OAuth to ensure secure access and contributor tracking. **Access is restricted to members of the `proto-SNEA` team in the `Brothertown-Language` organization.**

1. **Register GitHub OAuth App**:
    - Go to GitHub **Settings** > **Developer settings** > **OAuth Apps** > **New OAuth App**.
    - **Application Name**: `SNEA Shoebox Editor`
    - **Homepage URL**: `https://snea-editor.michael-conrad.com`
    - **Authorization callback URL**: `https://snea-api.michael-conrad.com/auth/callback`
2. **Update Repo Secrets**:
    - Manually add `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` (from the OAuth App you just created) to your GitHub
      Repository Secrets.
3. **Required Scopes**:
    - Ensure the OAuth flow requests the `read:org` scope to verify team membership.

---

## Architecture Details

### 1. Automated Deployment (GitHub Actions)

- **Workflow**: `.github/workflows/deploy.yml` handles the build.
- **WASM Compilation**: Solara/Pyodide compiles Python UI code into WebAssembly.
- **Zero-Workstation-Install**: All deployment tools run strictly in the GitHub runner.

### 2. Python Frontend (Solara)

- **Responsive UI**: Mobile and Desktop support using grid-based layouts.
- **Strictly Python**: No JavaScript required for UI logic.

### 3. Python Backend (Cloudflare Workers)

- **Data Layer**: D1 database using Python bindings.
- **Source Code**: Implementation resides in `src/worker.py`.
- **Manual Seeding**: The app starts with an empty database. Administrators can trigger seed ingestion from multiple
  private source files (Natick, SNEALEX, Mohegan Dictionary, etc.) via dedicated endpoints.

### 4. Concurrency & Authentication Management

- **GitHub OAuth Authentication**: Access is strictly limited to authenticated GitHub users **who are active members of the `proto-SNEA` team within the `Brothertown-Language` organization.**
- **Auth Logic**:
    - Backend retrieves user token via OAuth exchange.
    - Backend verifies team membership via `GET /orgs/Brothertown-Language/teams/proto-snea/memberships/{username}`.
    - Access is granted only if the state is `active`.
- **Optimistic Locking**: The editor uses optimistic locking to prevent overlapping edits.
- **No Inactivity Timeouts**: Record locks are handled per session without automated expiration, relying on user action
  and version validation.

### 5. Data Persistence & Edit History

- **Edit History Table**: All changes to records must be tracked in a dedicated edit history table.
- **Audit Metadata**: Each history entry must include:
    - **Modified Timestamp**: Exact time of the change.
    - **OAuth User Email**: The identity of the editor.
    - **Previous Data**: State of the record before the edit.
    - **Current Data**: State of the record after the edit.
- **Main Table Integrity**: The current record in the main table must always be the last entry in the edit history table for that record ID.

