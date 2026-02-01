<!-- Copyright (c) 2026 Brothertown Language -->

# SNEA Editor Security Rotation Guide [COMPLETE - DO NOT EDIT]

> **STATUS: COMPLETE** - This document is a historical record of the security rotation performed on 2026-02-01. The infrastructure has been secured, keys rotated, and synchronization completed. This file should no longer be edited.

This guide covers the process of rotating the specific secrets that were exposed when the `.env` file was accidentally committed to the repository. Use these instructions to revoke the compromised keys and restore security.

> **Note:** For more detailed information on initial key setup, refer to the [Infrastructure & Production Setup Guide](PROD_SETUP.md).

---

### Phase 1: Generate New Keys (The "Rotate" Phase)

Follow these links to revoke the old (leaked) keys and generate new ones.

#### 1. GitHub OAuth Client Secret
*Used for user authentication.*

*   **Direct Link:** [https://github.com/organizations/Brothertown-Language/settings/applications](https://github.com/organizations/Brothertown-Language/settings/applications)
*   **Alternative:** If 404, go to [Personal Developer Settings](https://github.com/settings/developers), then use the sidebar dropdown to select "Brothertown-Language".
*   **Action:** Click your App name -> **Client secrets** -> **Generate a new client secret**.
*   **Update `.env`**: Replace the values for `SNEA_GITHUB_CLIENT_SECRET` and `PROD_SNEA_GITHUB_CLIENT_SECRET`.

#### 2. GitHub Personal Access Token (PAT)
*Used by the bootstrap script to manage your repo.*

*   **Direct Link:** [https://github.com/settings/tokens?type=beta](https://github.com/settings/tokens?type=beta)
*   **Action:** 
    1.  Delete the old token (e.g., `github_pat_11ABH...`).
    2.  Click **Generate new token** -> **Fine-grained token**.
*   **Setup:**
    *   **Token name**: e.g., `SNEA Rotation [Date]`
    *   **Resource owner**: Select **Brothertown-Language** (Crucial: Do not use your personal account).
*   **Permissions:** 
    *   **Repository access**: Select **Only select repositories** and pick `Brothertown-Language/snea-shoebox-editor`.
    *   **Repository permissions**:
        *   `Contents`: **Read and write**
        *   `Secrets`: **Read and write**
        *   `Metadata`: **Read-only**
*   **Update `.env`**: Replace the value for `PROD_GH_TOKEN`.

#### 3. Cloudflare User API Token
*Used to manage your database and backend (CI/CD).*

*   **Direct Link:** [https://dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens)

*   **Action:** 
    1.  Find your token (e.g., "snea-editor") in the list.
    2.  Click the three dots `...` -> **Roll**.
    3.  **Note**: Clicking "Roll" invalidates the old token and displays a **new token value** immediately. This is the value you need.
*   **Permissions Required:** 
    Ensure the token has the following permissions (Custom Token):
    *   `Account` | `D1` | `Edit`
    *   `Account` | `Workers Scripts` | `Edit`
    *   `Account` | `Account Settings` | `Read` (Required to find Account ID)
    *   `Account` | `Cloudflare Pages` | `Edit`
    *   `Zone` | `Workers Routes` | `Edit` (If managing custom domains)
    *   `Zone` | `DNS` | `Read` (If managing custom domains)
    
    *Note: `Workers KV Storage` and `Workers R2 Storage` are NOT required.*
*   **Update `.env`**: Replace the value for `PROD_CF_API_TOKEN`.
*   **Recommendation**: Use the API Token instead of the Global API Key for all bootstrap operations. The bootstrap script has been updated to prioritize the token if available.

#### 4. Cloudflare Global API Key
*This is a master key. If it was present in your `.env` when it was committed, it MUST be rotated.*

*   **Direct Link:** [https://dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens)
*   **Action:** Find the **Global API Key** section and click **Change** to rotate it.
*   **Update `.env`**: Replace the value for `PROD_CF_API_KEY`.

---

### Phase 2: Verify Local Environment (The "Replace" Phase)

Confirm your local `.env` file in the project root contains the new values. Update **both** sets if the keys were compromised.

**Important:** The `PROD_` prefixed variables are used by the bootstrap script to update the production environment. The `SNEA_` (non-prefixed) variables are for your local development.

**Your `.env` should look like this after editing:**
```env
# GitHub OAuth (Local Development)
SNEA_GITHUB_CLIENT_ID=Ov23lioCUeuhd94j3DLR
SNEA_GITHUB_CLIENT_SECRET=PASTE_NEW_OAUTH_SECRET_HERE

# GitHub OAuth (Production Credentials)
PROD_SNEA_GITHUB_CLIENT_ID=Ov23liQCsQIKRZ3kqqyB
PROD_SNEA_GITHUB_CLIENT_SECRET=PASTE_NEW_OAUTH_SECRET_HERE

# Production Bootstrap (Infrastructure Management)
PROD_CF_EMAIL=Muksihs@gmail.com
PROD_CF_API_KEY=PASTE_NEW_CLOUDFLARE_GLOBAL_KEY_HERE
PROD_CF_API_TOKEN=PASTE_NEW_CLOUDFLARE_TOKEN_HERE
PROD_GH_TOKEN=PASTE_NEW_GITHUB_PAT_HERE
```

---

### Phase 3: Sync to Production (The "Finalize" Phase)

Instead of manually typing secrets into GitHub's web interface, use the built-in bootstrap script to securely upload everything.

1.  **Open your terminal** in the project root.
2.  **Run the bootstrap script:**
    ```bash
    uv run python3 bootstrap_env.py
    ```
    *   **What this does:** This script reads your new `.env`, connects to GitHub using your new `PROD_GH_TOKEN`, and automatically updates the **encrypted secrets** in your GitHub repository settings.

3.  **Verify on GitHub:**
    *   Go to: [https://github.com/Brothertown-Language/snea-shoebox-editor/settings/secrets/actions](https://github.com/Brothertown-Language/snea-shoebox-editor/settings/secrets/actions)
    *   You should see that the "Last updated" timestamp for your secrets is now "just now".

---

### ✅ Success Check
Once finished:
- **Revoked:** The old keys are now invalid (even though they are in the git history).
- **Secure:** Your local `.env` is updated and ignored by Git.
- **Synchronized:** The production environment has the new keys.
