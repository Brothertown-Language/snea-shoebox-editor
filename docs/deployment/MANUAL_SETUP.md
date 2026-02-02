<!-- Copyright (c) 2026 Brothertown Language -->
# Cloudflare Manual Setup Guide (Permanent)

This guide provides the one-time manual steps required to connect this repository to Cloudflare. The SNEA Editor runs as a **Unified Worker instance** that hosts both the Python backend and the **Stlite** (Streamlit in Wasm) frontend.

### Cleanup: Before You Start
To avoid conflicts, please **delete the following** from your Cloudflare Dashboard:
1.  **Workers & Pages** -> **snea-backend** (The old backend Worker).
2.  **Workers & Pages** -> **snea-editor** (If it exists as a Pages project; we will recreate it as a Worker).

## 1. PREREQUISITES: The Cloudflare API Token

Before starting the setup, you must have a Cloudflare API Token. This token is what allows GitHub to talk to Cloudflare.

### GitHub OAuth Setup (Mandatory)
You must create two separate GitHub OAuth Applications **within the Organization**:

1.  **Navigate to Organization Settings**:
    -   Go to [GitHub](https://github.com/) and navigate to the **Brothertown-Language** organization page.
    -   Click **Settings** (top tab).
    -   In the left sidebar, scroll down to **Developer settings** -> **OAuth Apps**.
    -   Click **New Org OAuth App**.

2.  **Production App**:
    -   **Application Name**: `SNEA Editor (Prod)`
    -   **Homepage URL**: `https://snea-editor.michael-conrad.com`
    -   **Authorization callback URL**: `https://snea-editor.michael-conrad.com`
    -   **Secret**: Save to `.env` as `PROD_SNEA_GITHUB_CLIENT_SECRET` (and Client ID as `PROD_SNEA_GITHUB_CLIENT_ID`).

2.  **Local Development App**:
    -   **Application Name**: `SNEA Editor (Local)`
    -   **Homepage URL**: `http://localhost:8787`
    -   **Authorization callback URL**: `http://localhost:8787`
    -   **Secret**: Save to `.env` as `SNEA_GITHUB_CLIENT_SECRET` (and Client ID as `SNEA_GITHUB_CLIENT_ID`).

**Tip**: If you have existing tokens and are unsure which is which, **delete them both** and create one fresh token following the steps below. This ensures you start with the correct permissions.

1.  **Create the Token**:
    -   Go to the [Cloudflare Dashboard > My Profile > API Tokens](https://dash.cloudflare.com/profile/api-tokens).
    -   Click **Create Token**.
    -   Find **Create Custom Token** (at the top) and click **Get started**.
2.  **Set Permissions**: Name the token `snea-deploy-token` and add these **3 specific permissions**:
    -   `Account` | `Cloudflare Pages` | `Edit` (Still required for some legacy bindings or if using Pages Assets)
    -   `Account` | `Workers Scripts` | `Edit`
    -   `Account` | `D1` | `Edit`
3.  **Save the Token**:
    -   Click **Continue to summary** -> **Create Token**.
    -   **COPY THE TOKEN IMMEDIATELY.** It will never be shown again.
    -   Paste this token into your `.env` file as `PROD_CF_API_TOKEN`.
    -   *(If you run `bootstrap_env.py`, it will automatically upload this token to GitHub as a secret named `CLOUDFLARE_API_TOKEN`.)*

---

## 2. APP SETUP (Cloudflare Worker + Static Assets)

The SNEA Editor runs as a single Worker. The backend is a Python Worker, and the frontend is a Streamlit app running in the browser via Stlite, served as a static asset by the same Worker.

### A. Create and Connect the Worker
1.  Navigate to **Workers & Pages** -> **Overview** -> **Create**.
2.  Select **Create application** -> **Import a repository**.
3.  Connect your GitHub account and select the `snea-shoebox-editor` repository.
4.  **Project Name**: `snea-editor`.
5.  **Set up your application**:
    - **Build command**: `sh scripts/cloudflare_build.sh`
    - **Deploy command**: `npx wrangler deploy`
    - **Non-production branch deploy command**: `npx wrangler versions upload`
    - **Path**: `/`
    - **Build Settings** (Advanced): Select your API token in the **API Token** dropdown.
6.  **Build Settings**:
    - **Production Branch**: `main`
    - **Build Command**: `sh scripts/cloudflare_build.sh`
    - **Root Directory**: (Leave EMPTY)
7.  Click **Save and Deploy**. Cloudflare will now pull the code and `wrangler.toml` from GitHub.

### B. Bindings and Secrets (Automated)

If you have already run `python3 bootstrap_env.py`, the following are handled for you:
-   **API Token**: `CLOUDFLARE_API_TOKEN` is uploaded to GitHub Secrets.
-   **Secrets**: `JWT_SECRET`, `SNEA_GITHUB_CLIENT_ID`, and `SNEA_GITHUB_CLIENT_SECRET` are uploaded to GitHub Secrets.
-   **Wrangler Config**: `wrangler.toml` is generated with your `database_id`.

Next, perform this manual step in the Cloudflare Dashboard for the `snea-editor` worker:

1.  **D1 Database Binding**:
    -   Go to the `snea-editor` Worker -> **Settings** -> **Bindings**.
    -   Click **Add Binding** -> **D1 Database**.
    -   **Variable Name**: `DB`
    -   **D1 Database**: Select `snea-shoebox`.
    -   Click **Save and Deploy**.

---

## 3. CUSTOM DOMAINS
1.  **Domain**: Worker -> **Settings** -> **Domains & Routes** -> **Add Custom Domain** -> Add `snea-editor.michael-conrad.com`.
